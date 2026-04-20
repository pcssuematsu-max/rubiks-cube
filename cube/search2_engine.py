"""Search2 engine implementation."""

import numpy as np
from heapdict import heapdict

from model.search_result import SearchResult


def softmax(x):
    """Column-wise softmax used by Search2 candidate expansion."""
    shifted = x - np.max(x, axis=0, keepdims=True)
    exp_x = np.exp(shifted)
    return exp_x / np.sum(exp_x, axis=0, keepdims=True)


class Search2Engine:
    def __init__(self, ai):
        self.ai = ai
        self.cube = ai.cube
        self.ips = ai.ips

    def search2(self, N):
        value_by_key = {}
        frontier = heapdict()
        frontier[()] = -N * 2
        best_value = -1000000000
        best_key = ()
        counter = np.zeros(2, dtype='i')
        move_count = len(self.cube.move_keys)
        continue_searching = True
        root_value = None

        while continue_searching:
            search_batch = self._pop_search_batch(frontier)
            key_list, priorities = self._extract_search_keys(search_batch)
            features, priority_weights, invalid_move_mask, early_result = self._build_search_inputs(
                key_list, priorities, move_count, value_by_key, counter
            )
            if early_result is not None:
                return early_result

            prediction = self.ai._predict_search2(features)
            state_values, move_priors = self._split_search_outputs(prediction, invalid_move_mask, priority_weights)

            best_value, best_key, root_value, done = self._update_search_progress(
                key_list, state_values, value_by_key, counter, best_value, best_key, root_value, N
            )
            if done is not None:
                return done

            self._enqueue_search_candidates(frontier, key_list, move_priors)
            continue_searching = (len(frontier) > 0)

        return self._finalize_search(best_key, value_by_key, counter)

    def _pop_search_batch(self, frontier):
        batch_size = min(len(frontier), 100)
        search_batch = []
        for _ in range(batch_size):
            search_batch.append(frontier.popitem())
        return search_batch

    def _extract_search_keys(self, search_batch):
        key_list = [item[0] for item in search_batch]
        priorities = [item[1] for item in search_batch]
        return key_list, priorities

    def _build_search_inputs(self, key_list, priorities, move_count, value_by_key, counter):
        batch_size = len(key_list)
        features = np.zeros((self.ips, batch_size))
        priority_weights = np.zeros(batch_size)
        invalid_move_mask = np.zeros((move_count, batch_size), dtype=bool)

        for index, key in enumerate(key_list):
            self._apply_moves(key)
            self._apply_inverse_mask(key, invalid_move_mask, index)
            if self.cube.is_perfect():
                self._revert_moves(key)
                value_history = self._build_value_history(value_by_key, key, self.ai.perfect_val)
                early_result = SearchResult(True, key, value_history[0], value_history, self.ai.perfect_val, counter, search_mode='search2', end_reason='solved')
                return features[:, :1], priority_weights[:1], invalid_move_mask[:, :1], early_result

            features[:, index] = self.cube.makedata().reshape(-1)
            priority_weights[index] = -priorities[index]
            self._revert_moves(key)

        return features, priority_weights, invalid_move_mask, None

    def _apply_inverse_mask(self, key, invalid_move_mask, column_index):
        if len(key) > 0:
            removed_moves = {self.cube.invert_str(key[-1])}
        else:
            removed_moves = set([])
        filtered_moves = filter(lambda move: move[:2] in removed_moves, self.cube.move_keys)
        for move in filtered_moves:
            move_index = self.cube.move_keys.index(move)
            invalid_move_mask[move_index, column_index] = True

    def _split_search_outputs(self, prediction, invalid_move_mask, priority_weights):
        state_values = prediction[-1].reshape(-1)
        move_priors = prediction[:-1]
        move_priors[invalid_move_mask] = -10000
        move_priors = softmax(move_priors) * priority_weights
        return state_values, move_priors

    def _update_search_progress(self, key_list, state_values, value_by_key, counter, best_value, best_key, root_value, search_budget):
        for index, key in enumerate(key_list):
            value_by_key[key] = state_values[index]
            if key == ():
                root_value = state_values[index]
                best_value = root_value + 0.0001
                best_key = ()

            counter[1] += 1
            if root_value is None:
                continue

            node_value = state_values[index]
            if node_value > best_value:
                best_value = node_value
                best_key = key

            if node_value > root_value + 0.0001:
                counter[0] += 1

            if self._should_stop(best_key, node_value, root_value, counter, search_budget):
                value_history = self._build_value_history(value_by_key, best_key)
                result = SearchResult(False, best_key, root_value, value_history, value_by_key[best_key], counter, search_mode='search2', end_reason='budget')
                return best_value, best_key, root_value, result

        return best_value, best_key, root_value, None

    def _should_stop(self, best_key, node_value, root_value, counter, search_budget):
        search_improved = (
            len(best_key) >= 1
            and node_value > root_value + self.ai.skip_difference
            and self.ai.skip_search
        )
        budget_exhausted = (counter[1] >= search_budget and counter[0] > 0)
        return search_improved or budget_exhausted

    def _enqueue_search_candidates(self, frontier, key_list, move_priors):
        candidate_indices = np.where(move_priors >= 1)
        for move_index, key_index in zip(candidate_indices[0], candidate_indices[1]):
            if len(key_list[key_index]) < 200:
                next_key = key_list[key_index] + (self.cube.move_keys[move_index],)
                frontier[next_key] = -move_priors[move_index, key_index]

    def _finalize_search(self, best_key, value_by_key, counter):
        for move in best_key:
            self.cube.make_move(move)
        is_perfect = self.cube.is_perfect()
        for move in self.cube.invert_moves(best_key):
            self.cube.make_move(move)
        value_history = self._build_value_history(value_by_key, best_key)
        end_reason = 'solved' if is_perfect else 'budget'
        return SearchResult(is_perfect, best_key, value_history[0], value_history, value_by_key[best_key], counter, search_mode='search2', end_reason=end_reason)

    def _apply_moves(self, key):
        for move in key:
            self.cube.make_move(move)

    def _revert_moves(self, key):
        for move in self.cube.invert_moves(key):
            self.cube.make_move(move)

    def _build_value_history(self, value_by_key, key, tail_value=None):
        value_history = []
        for index in range(len(key)):
            value_history.append(value_by_key[key[:index]])
        if tail_value is None:
            value_history.append(value_by_key[key])
        else:
            value_history.append(tail_value)
        return value_history
