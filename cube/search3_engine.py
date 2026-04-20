"""Search3 / PUCT engine implementation."""

import numpy as np

from model.search_result import SearchResult


def sigmoid(x):
    """Scalar sigmoid for Search3 value normalization."""
    return 1 / (1 + np.exp(-x))


class Search3Engine:
    def __init__(self, ai):
        self.ai = ai
        self.cube = ai.cube
        self.ips = ai.ips
        self.root_node = None
        self.root_state_key = None
        self.node_cache = {}
        self.prediction_cache = {}
        self.last_move = None
    
    def reset_tree(self):
        self.root_node = None
        self.root_state_key = None
        self.node_cache = {}
        self.prediction_cache = {}
        self.last_move = None

    def _state_key(self):
        return ''.join(self.cube.state)

    def _sync_root(self):
        state_key = self._state_key()
        if self.root_state_key != state_key:
            self.root_node = self.node_cache.get(state_key)
            self.root_state_key = state_key

    def _predict_current_state(self):
        return self._predict_feature(self.cube.makedata().reshape(-1), self._state_key())

    def _predict_feature(self, feature, state_key):
        cached_prediction = self.prediction_cache.get(state_key)
        if cached_prediction is not None:
            return cached_prediction
        prediction = self.ai._predict_search2(feature.reshape(-1, 1))
        self.prediction_cache[state_key] = prediction
        return prediction

    def _predict_leaf_batch(self, pending_leaves):
        if len(pending_leaves) == 0:
            return
        features = np.zeros((self.ips, len(pending_leaves)))
        for index, pending_leaf in enumerate(pending_leaves):
            features[:, index] = pending_leaf['feature']
        predictions = self.ai._predict_search2(features)
        for index, pending_leaf in enumerate(pending_leaves):
            state_key = pending_leaf['state_key']
            prediction = predictions[:, index:index + 1]
            self.prediction_cache[state_key] = prediction
            node_P = prediction[:-1].reshape(-1)
            node_V = prediction[-1, 0]
            child_node = self.node_cache.get(state_key)
            if child_node is None:
                child_node = self._create_node(state_key, node_P, node_V)
            else:
                child_node.P[:] = node_P
                child_node.value = node_V
            pending_leaf['parent_node'].children[pending_leaf['move_label']] = child_node
            pending_leaf['path_nodes'].append(child_node)
            pending_leaf['node_value'] = sigmoid(node_V)

    def _create_node(self, state_key, node_P, node_value=None, C=0.05):
        node = Node(node_P, state_key, node_value, C=self.ai.search3_C)
        self.node_cache[state_key] = node
        return node

    def _create_node_from_current_state(self, C=0.05):
        state_key = self._state_key()
        node_PV = self._predict_current_state()
        node_P = node_PV[:-1].reshape(-1)
        node_V = node_PV[-1, 0]
        node = self.node_cache.get(state_key)
        if node is None:
            node = self._create_node(state_key, node_P, node_V, C=C)
        else:
            node.value = node_V
        return node, node_V

    def _find_invalid_index(self, path_moves):
        if len(path_moves) > 0:
            last_move = path_moves[-1]
        else:
            last_move = self.last_move
        if last_move is None:
            return None
        inverse_move = self.cube.invert_str(last_move)
        return self.cube.move_keys.index(inverse_move)

    def _ensure_root_node(self, C=0.05):
        self._sync_root()
        root_prediction = self._predict_current_state()
        root_value = root_prediction[-1, 0]
        if self.root_node is None:
            root_P = root_prediction[:-1].reshape(-1)
            self.root_node = self._create_node(self._state_key(), root_P, root_value, C=C)
            self.root_state_key = self._state_key()
        return root_value

    def _evaluate_move_sequence(self, moves):
        if len(moves) == 0:
            return sigmoid(self._predict_current_state()[-1, 0])
        for move in moves:
            self.cube.make_move(move)
        leaf_value = sigmoid(self._predict_current_state()[-1, 0])
        for move in self.cube.invert_moves(tuple(moves)):
            self.cube.make_move(move)
        return leaf_value

    def _value_trace_for_moves(self, root_value, moves):
        value_trace = [root_value]
        if len(moves) == 0:
            return value_trace
        for move in moves:
            self.cube.make_move(move)
            value_trace.append(sigmoid(self._predict_current_state()[-1, 0]))
        for move in self.cube.invert_moves(tuple(moves)):
            self.cube.make_move(move)
        return value_trace

    def _raw_value_trace_for_moves(self, root_value_raw, moves):
        value_trace = [root_value_raw]
        if len(moves) == 0:
            return value_trace
        for move in moves:
            self.cube.make_move(move)
            value_trace.append(self._predict_current_state()[-1, 0])
        for move in self.cube.invert_moves(tuple(moves)):
            self.cube.make_move(move)
        return value_trace

    def advance_root(self, move):
        state_key = self._state_key()
        child_node = None
        if self.root_node is not None and move in self.root_node.children:
            child_node = self.root_node.children[move]
            if child_node.state_key != state_key:
                child_node = None
        if child_node is None:
            child_node = self.node_cache.get(state_key)
        self.root_node = child_node
        self.root_state_key = state_key
        self.last_move = move

    def _backup_path(self, path_nodes, path_indices, node_value):
        for depth in range(len(path_indices) - 1, -1, -1):
            parent_node = path_nodes[depth]
            parent_node.val[path_indices[depth]] += node_value

    def _revert_path(self, path_moves):
        for move in self.cube.invert_moves(tuple(path_moves)):
            self.cube.make_move(move)

    def _collect_leaf_path(self, root_node, max_depth):
        node = root_node
        path_nodes = [root_node]
        path_indices = []
        path_moves = []
        path_state_keys = {root_node.state_key}
        while True:
            index = node.select_node(self._find_invalid_index(path_moves))
            move_label = self.cube.move_keys[index]
            path_indices.append(index)
            path_moves.append(move_label)
            node.visited[index] += 1
            node.S += 1
            self.cube.make_move(move_label)
            if self.cube.is_perfect():
                return {
                    'resolved': True,
                    'solved_move': tuple(path_moves),
                    'path_nodes': path_nodes,
                    'path_indices': path_indices,
                    'path_moves': path_moves,
                    'node_value': 1.0,
                }

            state_key = self._state_key()
            if state_key in path_state_keys:
                return {
                    'resolved': True,
                    'solved_move': None,
                    'path_nodes': path_nodes,
                    'path_indices': path_indices,
                    'path_moves': path_moves,
                    'node_value': 0.0,
                }
            if len(path_moves) >= max_depth:
                return {
                    'resolved': False,
                    'parent_node': node,
                    'move_label': move_label,
                    'state_key': state_key,
                    'feature': self.cube.makedata().reshape(-1),
                    'path_nodes': path_nodes,
                    'path_indices': path_indices,
                    'path_moves': path_moves,
                }
            child_node = node.children.get(move_label)
            if child_node is None or child_node.state_key != state_key:
                child_node = self.node_cache.get(state_key)
                if child_node is not None:
                    node.children[move_label] = child_node
            if child_node is None:
                return {
                    'resolved': False,
                    'parent_node': node,
                    'move_label': move_label,
                    'state_key': state_key,
                    'feature': self.cube.makedata().reshape(-1),
                    'path_nodes': path_nodes,
                    'path_indices': path_indices,
                    'path_moves': path_moves,
                }
            path_state_keys.add(state_key)
            path_nodes.append(child_node)
            node = child_node

    def _principal_variation(self, root_node):
        pv_moves = []
        node = root_node
        visited_states = set([])
        while node is not None and node.S > 0 and node.state_key not in visited_states:
            visited_states.add(node.state_key)
            best_index = int(np.argmax(node.visited))
            if node.visited[best_index] == 0:
                break
            best_move = self.cube.move_keys[best_index]
            if best_move not in node.children:
                break
            pv_moves.append(best_move)
            node = node.children[best_move]
        return tuple(pv_moves)

    def search3(self, N, C=0.05):
        root_value_raw = self._ensure_root_node(C=C)
        root_value = sigmoid(root_value_raw)
        root_node = self.root_node
        solved_move = None
        remaining_playouts = N
        batch_size = min(getattr(self.ai, 'search_batch3', 32), N)
        max_depth = max(1, getattr(self.ai, 'search_depth3', 100))
        start_root_visits = root_node.visited.copy()
        total_playouts = 0

        while remaining_playouts > 0 and solved_move is None:
            current_batch_size = min(batch_size, remaining_playouts)
            pending_leaves = []
            processed_playouts = 0
            for _ in range(current_batch_size):
                leaf_path = self._collect_leaf_path(root_node, max_depth)
                processed_playouts += 1
                self._revert_path(leaf_path['path_moves'])
                if leaf_path['resolved']:
                    self._backup_path(leaf_path['path_nodes'], leaf_path['path_indices'], leaf_path['node_value'])
                    if leaf_path.get('solved_move') is not None:
                        solved_move = leaf_path['solved_move']
                        break
                else:
                    pending_leaves.append(leaf_path)

            self._predict_leaf_batch(pending_leaves)
            for pending_leaf in pending_leaves:
                self._backup_path(pending_leaf['path_nodes'], pending_leaf['path_indices'], pending_leaf['node_value'])

            total_playouts += processed_playouts
            remaining_playouts -= processed_playouts

        local_visits = root_node.visited - start_root_visits
        stats = np.array([np.max(local_visits), total_playouts], dtype='i')

        if solved_move is not None:
            best_moves = solved_move
            best_value = 1.0
            raw_value_trace = self._raw_value_trace_for_moves(root_value_raw, best_moves)
            raw_best_value = raw_value_trace[-1]
            value_trace = self._value_trace_for_moves(root_value, best_moves)
            if len(value_trace) > 0:
                value_trace[-1] = best_value
            return SearchResult(True, best_moves, root_value, value_trace, best_value, stats, root_node.visited.copy(), 'search3', 'solved', root_value_raw=root_value_raw, value_trace_raw=raw_value_trace, best_value_raw=raw_best_value)

        best_moves = self._principal_variation(root_node)
        if len(best_moves) == 0:
            best_moves = (self.cube.move_keys[np.argmax(root_node.visited)],)
        raw_value_trace = self._raw_value_trace_for_moves(root_value_raw, best_moves)
        best_value_raw = raw_value_trace[-1]
        best_value = sigmoid(best_value_raw)
        value_trace = self._value_trace_for_moves(root_value, best_moves)
        return SearchResult(False, best_moves, root_value, value_trace, best_value, stats, root_node.visited.copy(), 'search3', 'budget', root_value_raw=root_value_raw, value_trace_raw=raw_value_trace, best_value_raw=best_value_raw)


class Node:
    def __init__(self, P, state_key=None, value=None, C=0.05):
        self.P = P
        self.state_key = state_key
        self.value = value
        self.val = np.zeros_like(P, dtype='f')
        self.visited = np.zeros_like(P, dtype='i')
        self.S = 0
        self.C = C
        self.children = {}

    def select_node(self, invalid_index=None):
        score = np.where(self.visited != 0, self.val / self.visited, 0.5) + self.C * self.P * np.sqrt(max(1, self.S)) / (1 + self.visited)
        if invalid_index is not None:
            score[invalid_index] = -1000000000
        if self.S == 0:
            if invalid_index is not None:
                prior = self.P.copy()
                prior[invalid_index] = -1000000000
                return np.argmax(prior)
            return np.argmax(self.P)
        return np.argmax(score)
