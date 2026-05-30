"""Search data generation helpers."""

from __future__ import annotations

import numpy as np

from model.search_result import data_search3


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


class SearchDataManager:
    """solve履歴をSearch3用の学習データへ変換して蓄積する。"""

    def __init__(self, frame):
        self.frame = frame

    def store_search3_data(self, ai_index):
        """現在のsolve履歴を、指定AIのSearch3学習データとして追加する。"""
        state = self.frame.solve_state
        if self.frame.AI_idx == -1 or len(state.search_history) == 0:
            return

        ai = self.frame.AIs[ai_index]
        source_ai = self.frame.AIs[self.frame.AI_idx]
        next_index = len(ai.datas_search3)
        for history_index, history_item in enumerate(state.search_history):
            search_data = self.build_search3_training_sample(
                history_index,
                history_item,
                source_ai,
            )
            if search_data is None:
                continue
            search_data.succeeded = True
            ai.datas_search3.append(search_data)
            ai.indices_search3.append(next_index)
            next_index += 1

    def search3_training_moves(self, search_result):
        """Search3 学習用に手順列を simplify したものを返す。"""
        return self.frame.cube.simplify(search_result.moves)

    def build_search3_training_sample(self, history_index, history_item, source_ai):
        """保存前に手順列を簡約してから Search3 学習データ 1 件を作る。"""
        search_result = history_item['search_result']
        segment_moves = self.search3_training_moves(search_result)
        if len(segment_moves) == 0:
            return None

        value_targets = self.build_segment_value_targets(history_index, len(segment_moves))
        rewards = value_targets.copy()
        value_trace_raw = self.rebuild_search3_value_trace_raw(
            history_item['scramble'],
            segment_moves,
            source_ai,
        )
        value_trace = [sigmoid(value) for value in value_trace_raw]
        return data_search3(
            history_item['scramble'],
            segment_moves,
            rewards,
            value_trace[0],
            value_trace,
            value_trace[-1],
            search_result.stats,
            policy_target = self.build_search3_policy_target(search_result, segment_moves),
            search_mode = search_result.search_mode,
            sample_weight = self.search3_sample_weight(search_result),
            value_targets = value_targets,
            root_value_raw = value_trace_raw[0],
            value_trace_raw = value_trace_raw,
            best_value_raw = value_trace_raw[-1],
        )

    def build_segment_value_targets(self, history_index, segment_length):
        """残り手数とgammaから、その探索区間のvalue target列を作る。"""
        remaining_length = self.search3_remaining_length(history_index)
        value_targets = np.zeros(segment_length,dtype = 'f')
        gamma = self.frame.value_target_gamma
        for move_index in range(segment_length):
            value_targets[move_index] = gamma ** max(remaining_length - move_index - 1,0)
        return value_targets

    def search3_remaining_length(self, history_index):
        """指定履歴以降に残っている総手数を数える。"""
        remaining_length = 0
        for history_item in self.frame.solve_state.search_history[history_index:]:
            remaining_length += len(
                self.search3_training_moves(history_item['search_result'])
            )
        return remaining_length

    def build_search3_policy_target(self, search_result, segment_moves):
        """探索結果からpolicy targetを作る。soft targetがあれば正規化して使う。"""
        if search_result.policy_target is not None:
            policy_target = np.array(search_result.policy_target,dtype = 'f').reshape(-1)
            total = np.sum(policy_target)
            if total > 0:
                return policy_target / total

        policy_target = np.zeros((len(self.frame.move_keys),),dtype = 'f')
        if len(segment_moves) > 0:
            first_move = segment_moves[0]
            policy_target[self.frame.cube.key_to_num[first_move]] = 1.0
            return policy_target

        return np.ones((len(self.frame.move_keys),),dtype = 'f') / len(self.frame.move_keys)

    def rebuild_search3_value_trace_raw(self, scramble, moves, ai):
        """簡約後の全中間局面をまとめて推論して raw value trace を再計算する。"""
        features = self._collect_search3_trace_features(scramble, moves)
        prediction = ai._predict_search2(features)
        return prediction[-1, :].reshape(-1).tolist()

    def _collect_search3_trace_features(self, scramble, moves):
        """Search3 value trace 用に中間局面の特徴量列をまとめて作る。"""
        current_state = self.frame.cube.state.copy()
        self.frame.cube.reset()
        self.frame.cube.scramble(0, scramble)

        features = np.zeros((self.frame.cube.ips, len(moves) + 1), dtype = 'f')
        features[:, 0] = self.frame.cube.makedata()
        for move_index, move in enumerate(moves, 1):
            self.frame.cube.make_move(move)
            features[:, move_index] = self.frame.cube.makedata()

        self.frame.cube.state[:] = current_state
        return features

    def search3_sample_weight(self, search_result):
        """探索モードごとにSearch3学習のサンプル重みを決める。"""
        if search_result.search_mode == 'search3':
            return 1.0
        if search_result.search_mode == 'search2':
            return 0.5
        if search_result.search_mode == 'myval':
            return 0.2
        return 1.0
