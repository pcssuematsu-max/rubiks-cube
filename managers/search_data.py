"""Search data generation helpers."""

from __future__ import annotations

import numpy as np

from model.search_result import data_search3

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
        next_index = len(ai.datas_search3)
        for history_index, history_item in enumerate(state.search_history):
            search_result = history_item['search_result']
            segment_moves = self.search3_training_moves(history_index, search_result)
            if len(segment_moves) == 0:
                continue
            value_targets = self.build_segment_value_targets(history_index, len(segment_moves))
            rewards = value_targets.copy()
            search_data = data_search3(
                history_item['scramble'],
                segment_moves,
                rewards,
                search_result.root_value,
                search_result.value_trace,
                search_result.best_value,
                search_result.stats,
                policy_target = self.build_search3_policy_target(search_result),
                search_mode = search_result.search_mode,
                sample_weight = self.search3_sample_weight(search_result),
                value_targets = value_targets,
                root_value_raw = search_result.root_value_raw,
                value_trace_raw = search_result.value_trace_raw,
                best_value_raw = search_result.best_value_raw,
            )
            search_data.succeeded = True
            ai.datas_search3.append(search_data)
            ai.indices_search3.append(next_index)
            next_index += 1

    def search3_training_moves(self, history_index, search_result):
        """1回の探索結果から学習対象に使う手順列を取り出す。"""
        return tuple(search_result.moves)

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
            remaining_length += len(history_item['search_result'].moves)
        return remaining_length

    def remaining_search_solution_moves(self, history_index):
        """指定位置より後ろに残っているsolve手順を1列にまとめる。"""
        remaining_moves = tuple([])
        for moves in self.frame.solve_state.move_lis[history_index + 1:]:
            remaining_moves += tuple(moves)
        return remaining_moves

    def build_search3_rewards(self, remaining_moves):
        """残り手順列に対して、gamma減衰付きのreward列を作る。"""
        rewards = np.zeros(len(remaining_moves),dtype = 'f')
        if len(remaining_moves) == 0:
            return rewards
        gamma = self.frame.value_target_gamma
        for index in range(len(remaining_moves)):
            rewards[index] = gamma ** (len(remaining_moves) - index - 1)
        return rewards

    def build_search3_policy_target(self, search_result):
        """探索結果からpolicy targetを作る。soft targetがあれば正規化して使う。"""
        if search_result.policy_target is not None:
            policy_target = np.array(search_result.policy_target,dtype = 'f').reshape(-1)
            total = np.sum(policy_target)
            if total > 0:
                return policy_target / total

        policy_target = np.zeros((len(self.frame.move_keys),),dtype = 'f')
        if len(search_result.moves) > 0:
            first_move = search_result.moves[0]
            policy_target[self.frame.cube.key_to_num[first_move]] = 1.0
            return policy_target

        return np.ones((len(self.frame.move_keys),),dtype = 'f') / len(self.frame.move_keys)

    def search3_sample_weight(self, search_result):
        """探索モードごとにSearch3学習のサンプル重みを決める。"""
        if search_result.search_mode == 'search3':
            return 1.0
        if search_result.search_mode == 'search2':
            return 0.5
        if search_result.search_mode == 'myval':
            return 0.2
        return 1.0


