"""Solve session state and orchestration helpers."""

from __future__ import annotations

import random
from functools import reduce

import numpy as np
import tkinter as Tk

from model.search_result import SearchResult, data

PERFECT_VAL = 1.0e+8


def softmax(x):
    """1次元配列をsoftmaxで確率分布へ変換する。"""
    shifted = x - np.max(x)
    exp_x = np.exp(shifted)
    return exp_x / np.sum(exp_x)


class SolveSessionState:
    """1回のsolve過程で蓄積されるログ・表示用データをまとめて保持する。"""

    def __init__(self):
        self.s = None
        self.phase = -1
        self.search_TF = False
        self.end_solve = False
        self.last_perfect_key = ''
        self.last_simplified_lis = tuple([])
        self.move_lis = []
        self.key_lis = []
        self.val_lis = []
        self.val_lis2 = []
        self.display_move_lis = []
        self.display_key_lis = []
        self.display_root_lis = []
        self.display_val_lis = []
        self.display_val_lis2 = []
        self.search_history = []

    def reset_tracking(self):
        """solve中に蓄積した手順・評価値・表示履歴を空に戻す。"""
        self.move_lis.clear()
        self.key_lis.clear()
        self.val_lis.clear()
        self.val_lis2.clear()
        self.display_move_lis.clear()
        self.display_key_lis.clear()
        self.display_root_lis.clear()
        self.display_val_lis.clear()
        self.display_val_lis2.clear()
        self.search_history.clear()

    def reset_session(self):
        """1回のsolveに紐づく状態をまとめて初期化する。"""
        self.reset_tracking()
        self.s = None
        self.phase = -1
        self.search_TF = False
        self.end_solve = False
        self.last_perfect_key = ''
        self.last_simplified_lis = tuple([])


class SolveSessionManager:
    """Frameのsolve実行フローと、その途中状態の更新を担当する。"""

    def __init__(self, frame):
        self.frame = frame

    def my_solve(self):
        """1ステップ分のsolve処理を進め、表示更新と終了判定まで行う。"""
        state = self.frame.solve_state
        if self.frame.stop:
            return
        succeeded = False
        self._disable_solve_controls()
        AI = self._get_active_ai()
        if state.phase == -1:
            self._start_new_solve(AI)
        else:
            succeeded = self._advance_solve_step(AI)
            state.phase += 1

        self._update_viewers(AI)
        if state.end_solve:
            self._finalize_solve_step(succeeded)
        self.frame._schedule_next_solve()

    def _disable_solve_controls(self):
        """solve実行中は手動操作ボタンを無効化する。"""
        self.frame.my_solve_button.configure(state = Tk.DISABLED)
        for key in self.frame.move_keys:
            self.frame.movebuttons[key].configure(state = Tk.DISABLED)

    def _get_active_ai(self):
        """現在のAI indexに対応する探索主体を返す。"""
        if self.frame.AI_idx != -1:
            return self.frame.AIs[self.frame.AI_idx]
        return self.frame.myval_AI

    def _start_new_solve(self, AI):
        """新しいスクランブルを用意してsolveセッションを開始する。"""
        state = self.frame.solve_state
        self.frame.cube.reset()
        self._reset_search_engine(AI)
        if self.frame.AI_idx != -1:
            self._scramble_with_ai_settings()
        else:
            self._scramble_with_manual()
        state.phase += 1
        state.search_TF = (self.frame.AI_idx != -1)
        self._reset_solve_tracking()

    def _scramble_with_ai_settings(self):
        """現在のAI設定に従ってスクランブルを生成する。"""
        state = self.frame.solve_state
        scramble_num = self.frame.level[self.frame.AI_idx,self.frame.stage]
        add_moves = (self.frame.N % (self.frame.AInum * 2) < self.frame.AInum)
        while self.frame.cube.is_perfect():
            self.frame.cube.reset()
            if self.frame.transform_random:
                transform_N = None
                flip_inside = None
            else:
                transform_N = self.frame.transform_idx[self.frame.AI_idx]
                flip_inside = self.frame.flip_inside_idx[self.frame.AI_idx]

            state.s = self.frame.cube.scramble(
                scramble_num,
                difficult_mode = True,
                scramble_mode = self.frame.scramble_mode[self.frame.stage],
                add_moves = add_moves,
                transform_N = transform_N,
                flip_inside = flip_inside,
            )

    def _scramble_with_manual(self):
        """手動指定されたスクランブル列を現在状態へ反映する。"""
        state = self.frame.solve_state
        self.frame.cube.reset()
        state.s = self.frame.cube.scramble(0,Move = self.frame.my_scramble[self.frame.N])

    def _reset_solve_tracking(self):
        """1回のsolveに紐づく履歴と補助状態を初期化する。"""
        state = self.frame.solve_state
        state.reset_tracking()
        state.end_solve = False
        state.last_perfect_key = ''
        state.last_simplified_lis = tuple([])

    def _advance_solve_step(self, AI):
        """search段階かgreedy段階かを見て、次の1ステップを進める。"""
        if self.frame.solve_state.search_TF:
            return self._advance_search_step(AI)
        return self._advance_greedy_step(AI)

    def _advance_search_step(self, AI):
        """探索AIで1回探索し、結果を状態と表示用ログへ反映する。"""
        state = self.frame.solve_state
        succeeded = False
        current_state = self.frame.cube.state.copy()
        if len(state.val_lis) == 0:
            self._append_initial_value(AI)

        if self._uses_search3(AI):
            search_result = AI.search(progress_callback = lambda result: self._record_search_attempt_progress(AI, result))
        else:
            search_result = AI.search()
        self._record_search_history(search_result)
        if self._should_fallback_from_search3(AI, search_result):
            state.search_TF = False
            return False
        reduced_lis = self.frame.cube.reduce(search_result.moves)
        simplified_lis = self.frame.cube.simplify(search_result.moves)
        value_deltas = self._display_value_deltas(search_result)
        self._record_search_result(reduced_lis, search_result, value_deltas)

        if search_result.succeeded:
            succeeded = True
            state.end_solve = True
            simplified_lis = self._store_perfect_key(simplified_lis)

        for move in reduced_lis[0]:
            self.frame.cube.make_move(move)
            self._advance_search_engine(AI, move)

        if (self.frame.cube.state == current_state).all():
            self._handle_no_progress_search(AI)

        return succeeded

    def _record_search_result(self, reduced_lis, search_result, value_deltas):
        """探索結果をmainログへ追加し、必要なら表示ログにも反映する。"""
        state = self.frame.solve_state
        state.move_lis.append(reduced_lis[0])
        state.key_lis.append(str(search_result.stats[0]) + '/' + str(search_result.stats[1]))
        state.val_lis.append(search_result.root_value)
        state.val_lis2.append(self._reduce_value_deltas(reduced_lis[1], value_deltas))
        if search_result.search_mode != 'search3':
            state.display_move_lis.append(reduced_lis[0])
            state.display_key_lis.append(str(search_result.stats[0]) + '/' + str(search_result.stats[1]))
            state.display_root_lis.append(search_result.root_value)
            state.display_val_lis.append(search_result.best_value)
            state.display_val_lis2.append(self._reduce_value_deltas(reduced_lis[1], value_deltas))

    def _record_search_display(self, AI, search_result):
        """attempt単位の探索結果をMoveViewer表示用ログへ積む。"""
        state = self.frame.solve_state
        attempt_results = search_result.attempt_results
        if len(attempt_results) == 0:
            attempt_results = [search_result]
        for attempt_index, attempt_result in enumerate(attempt_results,1):
            reduced_lis = self.frame.cube.reduce(attempt_result.moves)
            value_deltas = self._display_value_deltas(attempt_result)
            key_label = str(attempt_result.stats[0]) + '/' + str(attempt_result.stats[1])
            if self._uses_search3(AI):
                current_attempt = attempt_result.attempt_index
                if current_attempt is None:
                    current_attempt = attempt_index
                key_label = 'S3-' + str(current_attempt) + ':' + key_label
            state.display_move_lis.append(reduced_lis[0])
            state.display_key_lis.append(key_label)
            state.display_root_lis.append(attempt_result.root_value)
            state.display_val_lis.append(attempt_result.best_value)
            state.display_val_lis2.append(self._reduce_value_deltas(reduced_lis[1], value_deltas))

    def _record_search_attempt_progress(self, AI, attempt_result):
        """Search3の途中経過を表示ログへ反映して即時更新する。"""
        self._record_search_display(AI, attempt_result)
        self._refresh_search_attempt_display(AI)

    def _refresh_search_attempt_display(self, AI):
        """attempt途中のMoveViewerとStateViewerをその場で描き直す。"""
        state = self.frame.solve_state
        self.frame.MV.set_str(
            state.s,
            state.display_move_lis,
            state.display_key_lis,
            state.display_root_lis,
            state.display_val_lis,
            state.display_val_lis2,
            self.frame.perf_num[self.frame.stage],
            self.frame.N,
            AI.search_mode,
        )
        self.frame.set_color(AI.cube.state)
        self.frame.update()

    def _display_value_deltas(self, search_result):
        """探索結果を表示用のvalue系列へ変換する。"""
        if search_result.search_mode == 'search3':
            return search_result.value_trace.copy()
        return [value - self.frame.AIs[self.frame.AI_idx].perfect_val for value in search_result.value_trace]

    def _reduce_value_deltas(self, reduced_indices, value_deltas):
        """簡約後の手順indexに合わせてvalue系列を間引く。"""
        if len(value_deltas) == 0:
            return []
        reduced_values = [value_deltas[0]]
        last_value = value_deltas[-1]
        for reduced_index in reduced_indices:
            value_index = reduced_index + 1
            if value_index < len(value_deltas):
                reduced_values.append(value_deltas[value_index])
            else:
                reduced_values.append(last_value)
        return reduced_values

    def _record_search_history(self, search_result):
        """探索結果をSearch3学習データ化用の履歴へ保存する。"""
        self.frame.solve_state.search_history.append({
            'scramble': self._current_search_scramble(),
            'search_result': search_result,
        })

    def _record_myval_history(self, scramble, root_value, succeeded):
        """greedy段階の結果もSearchResult形式にして履歴へ保存する。"""
        state = self.frame.solve_state
        if len(state.move_lis) == 0:
            return
        best_moves = tuple(state.move_lis[-1])
        if len(best_moves) == 0:
            return
        best_value = state.val_lis[-1]
        search_result = SearchResult(
            succeeded,
            best_moves,
            root_value,
            [root_value,best_value],
            best_value,
            np.array([1,1],dtype = 'i'),
            search_mode = 'myval',
            end_reason = 'solved' if succeeded else 'greedy',
        )
        self.frame.solve_state.search_history.append({
            'scramble': tuple(scramble),
            'search_result': search_result,
        })

    def _sync_display_tracking_from_main(self):
        """mainログをそのまま表示ログへコピーする。"""
        state = self.frame.solve_state
        state.display_move_lis[:] = state.move_lis.copy()
        state.display_key_lis[:] = state.key_lis.copy()
        state.display_root_lis[:] = state.val_lis.copy()
        state.display_val_lis[:] = state.val_lis.copy()
        state.display_val_lis2[:] = state.val_lis2.copy()

    def _reset_search_engine(self, AI):
        """Search3を使うAIなら探索木を初期状態に戻す。"""
        if self._uses_search3(AI):
            AI.search3_engine.reset_tree()

    def _advance_search_engine(self, AI, move):
        """Search3のrootを実際に選んだ手へ進める。"""
        if self._uses_search3(AI):
            AI.search3_engine.advance_root(move)

    def _uses_search3(self, AI):
        """このAIがSearch3型の探索を使うか判定する。"""
        return hasattr(AI,'search_mode') and AI.search_mode == 'search3'

    def _should_fallback_from_search3(self, AI, search_result):
        """Search3がbudget終了したときにgreedy側へ落とすか判定する。"""
        return self._uses_search3(AI) and search_result.end_reason == 'budget'

    def _current_search_scramble(self):
        """現在地点までに実行した手を含むスクランブル列を作る。"""
        state = self.frame.solve_state
        current_scramble = tuple(state.s)
        for moves in state.move_lis:
            current_scramble += tuple(moves)
        return current_scramble

    def _store_perfect_key(self, simplified_lis):
        """完成局面に対応するmypermキー情報を保存する。"""
        x = self.frame.cube.makedata().reshape(-1,1)
        perfect_key = ''
        state_key = ''.join(self.frame.cube.state)
        if state_key not in self.frame.myperms_col:
            for key in self.frame.cube._group_name_map().values():
                value = self.frame.cube.total_val[key] - (self.frame.cube.group_val[key] @ x)[0][0]
                if value > 0.01:
                    perfect_key += key + '(' + str(int(round(value,0))) + ')'
        else:
            perfect_key = self.frame.myperms_col[state_key][:-2]
            simplified_lis = self.frame.cube.transform(simplified_lis,int(self.frame.myperms_col[state_key][-2:]))
        self.frame.solve_state.last_perfect_key = perfect_key
        self.frame.solve_state.last_simplified_lis = tuple(simplified_lis)
        return simplified_lis

    def _handle_no_progress_search(self, AI):
        """探索で状態が進まなかったときにsearch段階を打ち切る。"""
        state = self.frame.solve_state
        state.search_TF = False
        if self.frame.AIs[self.frame.AI_idx].search_mode == 'search2':
            for moves in state.move_lis:
                state.s += tuple(moves)
            self.frame.solve_state.reset_tracking()

    def _advance_greedy_step(self, AI):
        """myvalベースのgreedy選択で次の手順を進める。"""
        state = self.frame.solve_state
        if self.frame.AI_idx in list(range(self.frame.AInum)):
            AI = self.frame.myval_AI

        if len(state.val_lis) == 0:
            self._append_initial_value(AI)

        current_scramble = self._current_search_scramble()
        root_value = state.val_lis[-1]
        succeeded = self._choose_and_apply_myperms(AI)
        self._record_myval_history(current_scramble, root_value, succeeded)
        return succeeded

    def _append_initial_value(self, AI):
        """現在局面の初期valueをログへ追加する。"""
        state = self.frame.solve_state
        x = self.frame.cube.makedata().reshape(-1,1)
        state_array = self.frame.cube.state.reshape(1,-1)
        if AI.myval:
            value = AI.myval_predict(x,state_array).reshape(-1)
        else:
            value = AI.predict(x,policy = False,value = True).reshape(-1)

        state.move_lis.append(tuple([]))
        state.key_lis.append('')
        state.val_lis.append(value[0])
        state.val_lis2.append([])
        state.display_move_lis.append(tuple([]))
        state.display_key_lis.append('')
        state.display_root_lis.append(value[0])
        state.display_val_lis.append(value[0])
        state.display_val_lis2.append([])

    def _choose_and_apply_myperms(self, AI):
        """候補mypermを評価して、最良の手順を実際に適用する。"""
        x = self.frame.cube.makedata().reshape(-1,1)
        top_group = self._select_top_group(x)
        myperms_key, top_key = self._collect_myperms_keys(top_group)
        return self._evaluate_myperms_candidates(AI, myperms_key, top_key)

    def _select_top_group(self, x):
        """優先順位に従って、次に注目するgroup名を選ぶ。"""
        top_group = 'Corner'
        top_val = 0
        for key in self.frame.priority_list[self.frame.AI_idx]:
            value = self.frame.cube.total_val[key] - (self.frame.cube.group_val[key] @ x)[0][0]
            if value > 0.001 and value > top_val:
                top_val = value
                top_group = key
                break
        return top_group

    def _collect_myperms_keys(self, top_group):
        """注目groupに対応するmyperm候補キー集合を集める。"""
        myperms_key = set(self.frame.cube.collect_single_move_and_rotate())
        top_key = set([])
        for piece_index in self.frame.cube.myperms_order[top_group]:
            piece = self.frame.cube.num_to_piece[piece_index]
            color_key = reduce(lambda left,right:left+right,[self.frame.cube.state[index] for index in piece])
            if color_key != self.frame.cube.default_color[piece]:
                top_key.add((piece,color_key))
                myperms_key |= set(self.frame.cube.myperms_dict[(piece,color_key)])
                break
        return list(myperms_key), top_key

    def _evaluate_myperms_candidates(self, AI, myperms_key, top_key):
        """myperm候補をvalueで評価し、継続できるかを判定する。"""
        state = self.frame.solve_state
        eval_num = len(myperms_key)
        X = np.empty((self.frame.cube.ips,eval_num),dtype = 'f')
        S = np.empty((eval_num,6 * self.frame.cube.surface_num),dtype = str)

        total_keys = len(myperms_key)
        idx = 0
        solved = False
        perfect_key = ''
        base = 0
        should_continue = False
        random.shuffle(myperms_key)
        for key in myperms_key:
            for move in AI.myperms[key]:
                self.frame.cube.make_move(move)

            if self.frame.cube.is_perfect():
                solved = True
                perfect_key = key

            x = self.frame.cube.makedata()
            X[:,idx] = x
            S[idx,:] = self.frame.cube.state

            for move in self.frame.cube.invert_moves(AI.myperms[key]):
                self.frame.cube.make_move(move)

            idx += 1
            if solved:
                break

            if idx == eval_num or base + idx == total_keys:
                idx = 0
                if AI.myval:
                    values = AI.myval_predict(X,S).reshape(-1)
                else:
                    values = AI.predict(X,policy = False,value = True).reshape(-1)

                if len(state.val_lis) == 0 or state.val_lis[-1] + 0.0001 < np.max(values):
                    should_continue = self._apply_best_myperms(AI, values, myperms_key, base)
                    if should_continue:
                        break
                else:
                    base += eval_num

        if solved:
            self._finish_with_perfect_myperms(AI, perfect_key)
            return True
        if not should_continue:
            print(top_key)
            state.end_solve = True
            if self.frame.AI_idx != -1:
                for moves in state.move_lis:
                    state.s += tuple(moves)
                self.frame.my_scramble.append(state.s)
        return False

    def _apply_best_myperms(self, AI, values, myperms_key, base):
        """評価が最良のmyperm候補を選んでログと状態へ反映する。"""
        state = self.frame.solve_state
        args = np.where(values >= np.max(values) - 0.0001)[0]
        new_keys = []
        new_moves = []
        X = np.empty((self.frame.cube.ips,0),dtype = 'f')
        S = np.empty((0,6 * self.frame.cube.surface_num),dtype = str)
        for arg_index in args[:1]:
            key = myperms_key[arg_index + base]
            move_count = 0
            for move in AI.myperms[key]:
                move_count += 1
                self.frame.cube.make_move(move)
                x = self.frame.cube.makedata()
                X = np.c_[X,x.reshape(-1,1)]
                S = np.r_[S,self.frame.cube.state.reshape(1,-1)]
                new_keys.append(key + '(' + str(move_count) + ')')
                new_moves.append(AI.myperms[key][:move_count])

            for move in self.frame.cube.invert_moves(AI.myperms[key]):
                self.frame.cube.make_move(move)

        if AI.myval:
            next_values = AI.myval_predict(X,S).reshape(-1)
        else:
            next_values = AI.predict(X,policy = False,value = True).reshape(-1)

        top_arg = np.argmax(next_values)
        best_value = next_values[top_arg]
        best_key = new_keys[top_arg]
        best_move = new_moves[top_arg]

        state.key_lis.append(best_key)
        state.move_lis.append(best_move)
        state.val_lis.append(best_value)
        state.val_lis2.append([])
        state.display_key_lis.append(best_key)
        state.display_move_lis.append(best_move)
        state.display_root_lis.append(state.display_val_lis[-1])
        state.display_val_lis.append(best_value)
        state.display_val_lis2.append([])
        for move in best_move:
            self.frame.cube.make_move(move)
        return True

    def _finish_with_perfect_myperms(self, AI, perfect_key):
        """完成が見つかったmyperm手順をログへ追加してsolve終了にする。"""
        state = self.frame.solve_state
        state.val_lis.append(PERFECT_VAL)
        state.key_lis.append(perfect_key)
        state.val_lis2.append([])
        state.move_lis.append(AI.myperms[perfect_key])
        state.display_key_lis.append(perfect_key)
        state.display_move_lis.append(AI.myperms[perfect_key])
        state.display_root_lis.append(state.display_val_lis[-1])
        state.display_val_lis.append(PERFECT_VAL)
        state.display_val_lis2.append([])
        state.end_solve = True

    def _update_viewers(self, AI):
        """現在局面のpolicy表示とMoveViewer表示を更新する。"""
        state = self.frame.solve_state
        x = self.frame.cube.makedata().reshape(-1,1)
        W = softmax(AI.predict(x,policy = True,value = False).reshape(-1))
        self.frame.PV.put_val(W)
        self.frame.debug_analysis_manager.show_current_viewer(self.frame.AI_idx,self.frame.cube_size ** 2)
        self.frame.MV.set_str(
            state.s,
            state.display_move_lis,
            state.display_key_lis,
            state.display_root_lis,
            state.display_val_lis,
            state.display_val_lis2,
            self.frame.perf_num[self.frame.stage],
            self.frame.N,
            AI.search_mode,
        )
        self.frame.set_color(AI.cube.state)

    def _finalize_solve_step(self, succeeded):
        """1回のsolve終了時に成功集計・学習データ追加・次AI準備を行う。"""
        state = self.frame.solve_state
        result_recorded = False
        if state.phase > 0 and succeeded:
            if state.search_TF:
                self.frame.perf_num[self.frame.stage] += 1
                self.frame.success[self.frame.AI_idx] += 1
                result_recorded = True

            combined_moves = ()
            if state.search_TF or self.frame.AIs[self.frame.AI_idx].search_mode == "search2":
                for moves in state.move_lis:
                    combined_moves += moves
                    if len(combined_moves) > 0:
                        rewards = np.zeros(len(combined_moves),dtype = 'f')
                        rewards[-1] = 10
                        datas = self.frame.cube.make_transformations(state.s,combined_moves)

                        data_item = data(datas[0][0],datas[1][0],rewards)
                        data_item.succeeded = True
                        self.frame.AIs[self.frame.AI_idx].datas.append(data_item)

                        for ai_index in range(self.frame.AInum):
                            self.frame.AIs[ai_index].indices.append(len(self.frame.AIs[ai_index].datas) - 1)

                        state.s += combined_moves
                        combined_moves = ()

            if state.search_TF and len(state.move_lis) >= 2:
                simplified_moves = tuple(state.last_simplified_lis)
                if simplified_moves not in self.frame.myperms_vals:
                    myperms_key = state.last_perfect_key + '00'
                    if myperms_key in self.frame.cube.myperms and len(self.frame.cube.myperms[myperms_key]) > len(simplified_moves):
                        print(self.frame.AI_idx,state.last_perfect_key,len(simplified_moves),'<-----------')
                    else:
                        print(self.frame.AI_idx,state.last_perfect_key,len(simplified_moves))

                    if state.last_perfect_key not in self.frame.last_perms:
                        self.frame.last_perms[state.last_perfect_key] = set([])
                    self.frame.last_perms[state.last_perfect_key].add(simplified_moves)

            if state.search_TF and self.frame.AIs[self.frame.AI_idx].search_mode == 'search2':
                max_level = max(1,int(- state.val_lis2[1][0] / 5))
                if max_level >= len(self.frame.cube.my_scrambles2):
                    for _ in range(max_level - len(self.frame.cube.my_scrambles2) + 1):
                        self.frame.cube.create_new_set()

                for move_index in range(1,len(state.move_lis)):
                    inverted_moves = self.frame.cube.invert_moves(state.move_lis[move_index])
                    level = max(0,int(- state.val_lis2[move_index][0] / 5))
                    self.frame.cube.my_scrambles2[level][inverted_moves[-1]].add(inverted_moves)

            if state.search_TF or self.frame.AIs[self.frame.AI_idx].search_mode == 'search3':
                for ai_index in range(self.frame.AInum):
                    self.frame.search_data_manager.store_search3_data(ai_index)

        if state.phase > 0:
            self.frame.success_viewer.put_result(self.frame.success,self.frame.N,self.frame.AI_idx,result_recorded)

        self.frame.N += 1
        self.frame.AI_idx += 1
        self.frame.AI_idx %= self.frame.AInum
        if len(self.frame.AIs[0].datas) - self.frame.data_len >= 200:
            self.frame.learn()
            self.frame.data_len = len(self.frame.AIs[0].datas)

        if self.frame.N == 200:
            self.frame.N = 0
            self.frame.stage += 1
            if self.frame.stage == self.frame.stage_num:
                self.frame.stage = 0

                if np.sum(self.frame.perf_num) >= 180:
                    self.frame.level[:] += 1

                print(self.frame.level[:])
                self.frame.my_scramble = []
                self.frame.perf_num[:] = 0
                self.frame.learn()

        state.phase = -1




    
