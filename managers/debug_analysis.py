"""Debug and viewer analysis helpers."""

from __future__ import annotations

import numpy as np

class DebugAnalysisManager:
    """AIの内部状態や評価結果を確認するための診断処理を担当する。"""

    def __init__(self, frame):
        self.frame = frame
        self.grad_index = frame.grad_index
        self.grad_mode = frame.grad_mode
        self.grad_layer = frame.grad_layer

    def update_viewer_settings(self, index_text, mode_text, layer_text):
        """UI入力値を読み取り、myviewerの表示対象設定を更新する。"""
        grad_index = self._parse_grad_index(index_text)
        if grad_index is None:
            return False
        self.grad_index = grad_index
        self.grad_mode = mode_text
        self.grad_layer = layer_text
        self._sync_frame_grad_settings()
        return True

    def show_current_viewer(self, ai_index, N):
        """現在のgrad設定に従って、正負の特徴Viewerを更新する。"""
        if self.grad_mode == "SVD":
            self.myviewer(ai_index,self.grad_index,N,SVD = True)
        elif self.grad_mode == "Grad":
            self.myviewer(ai_index,self.grad_index,N,Grad = True,layer = self.grad_layer)
        elif self.grad_mode == "IG":
            self.myviewer(ai_index,self.grad_index,N,IG = True,layer = self.grad_layer)
        elif self.grad_mode == "W1":
            self.myviewer(ai_index,self.grad_index,N)

    def sum_and_var(self, index):
        """指定AIの各パラメータについて、合計・分散・最大最小・更新量を表示する。"""
        ai = self.frame.AIs[index]
        for key in ai.params.keys():
            print(index,key)
            print("sum:",np.sum(ai.params[key]),"var:",np.var(ai.params[key]))
            print("max:",np.max(ai.params[key]),"min:",np.min(ai.params[key]))
            print("vsum:",np.sum(ai.v[key]))

    def max_val(self, T0 = (), T1 = (), head = '', Top = True, Num = 1):
        """条件に合うmyperm候補をAIで評価し、上位または下位の候補を表示する。"""
        keys = self.frame.search_myperms(T0,T1,head)
        input_data,empty_input = self._build_myperm_inputs(keys)
        for index in range(self.frame.AInum):
            self._print_ai_value_ranking(index,keys,input_data,empty_input,Top,Num)
        self.frame.cube.reset()

    def normalize(self, index):
        """指定AIの重みスケールを整え、BatchNorm系パラメータを初期値に戻す。"""
        ai = self.frame.AIs[index]
        for key in ai.params.keys():
            self._normalize_param(ai,key)
        ai.set_perfect_val()
        ai.mark_params_dirty()

    def re_activate(self, index):
        """更新量が小さいユニットを検出し、バイアスと一部重みを再活性化する。"""
        ai = self.frame.AIs[index]
        for key in ai.params.keys():
            if self._is_reactivation_target(key):
                self._reactivate_param(ai,key)
        ai.mark_params_dirty()

    def myviewer(self, AInum, i, N = 1, SVD = False, Grad = False, IG = False, layer = "WO_V"):
        """指定した重み・勾配・SVD成分をキューブ状態として可視化する。"""
        vector = self._viewer_vector(AInum,i,SVD,Grad,IG,layer)
        positive_state,negative_state = self._viewer_states(vector,N)
        self.frame.grad_viewer_positive.set_color(positive_state)
        self.frame.grad_viewer_negative.set_color(negative_state)

    def _build_myperm_inputs(self, keys):
        """myperm候補の手順を入力データ行列に変換する。"""
        input_data = np.zeros((self.frame.cube.ips,len(keys)),dtype = 'f')
        empty_input = np.zeros((self.frame.cube.ips,1),dtype = 'f')
        for index,key in enumerate(keys):
            self._write_myperm_input(input_data,index,key)
        return input_data,empty_input

    def _parse_grad_index(self, index_text):
        """grad index入力を整数へ変換し、変換できない場合はNoneを返す。"""
        try:
            return int(index_text)
        except ValueError:
            return None

    def _sync_frame_grad_settings(self):
        """既存コードとの互換性のため、Frame側のgrad設定にも同じ値を反映する。"""
        self.frame.grad_index = self.grad_index
        self.frame.grad_mode = self.grad_mode
        self.frame.grad_layer = self.grad_layer

    def _write_myperm_input(self, input_data, index, key):
        """1つのmyperm手順を実行し、その途中状態を評価用入力に書き込む。"""
        self.frame.cube.reset()
        for move in self.frame.cube.invert_moves(self.frame.cube.myperms[key]):
            self.frame.cube.make_move(move)
            input_data[:,index] = self.frame.cube.makedata()

    def _print_ai_value_ranking(self, index, keys, input_data, empty_input, Top, Num):
        """1つのAIについて、myperm候補の評価値ランキングを表示する。"""
        ai = self.frame.AIs[index]
        values = ai.predict(input_data,policy = False,value = True).reshape(-1)
        ordered_indices = np.argsort(values)
        selected_indices = self._selected_value_indices(ordered_indices,Top,Num)
        selected_keys = [keys[selected_index] for selected_index in selected_indices]
        selected_values = values[selected_indices]
        print(index,selected_keys,ai.perfect_val - selected_values)
        ai.predict(empty_input,policy = False,value = True).reshape(-1)

    def _selected_value_indices(self, ordered_indices, Top, Num):
        """上位表示か下位表示かに応じて、表示対象のindexを選ぶ。"""
        if Top:
            return ordered_indices[-Num:]
        return ordered_indices[:Num]

    def _normalize_param(self, ai, key):
        """1つのパラメータ配列に対して正規化または初期値リセットを行う。"""
        if key[0] == 'W' and len(key) == 2:
            scale = np.sqrt(np.var(ai.params[key],axis = 1).reshape(-1,1)) * np.sqrt(ai.params[key].shape[1] / 2)
            ai.params[key] /= scale
            ai.params['B' + key[1:]] /= scale.reshape(-1)
            ai.v[key] *= 0
        elif key[:3] == 'BNg':
            ai.params[key][:] = 1
        elif key[:3] == 'BNb':
            ai.params[key][:] = 0

    def _is_reactivation_target(self, key):
        """再活性化の対象になる重みパラメータか判定する。"""
        return key[0] == 'W' and key not in ['WO_P','WO_V','WM_P','WM_V']

    def _reactivate_param(self, ai, key):
        """更新量が小さいユニットに小さなバイアスと対角的な重みを入れる。"""
        weak_indices = np.where(ai.h['B' + key[1:]] < 1.0e-6)[0]
        print(key,weak_indices)
        ai.params['B' + key[1:]][weak_indices] = 0.05
        for weak_index in weak_indices:
            ai.params[key][weak_index,weak_index % ai.params[key].shape[1]] = -1.0

    def _viewer_vector(self, AInum, i, SVD, Grad, IG, layer):
        """myviewerで表示する元ベクトルを、指定モードに応じて取得する。"""
        ai = self.frame.AIs[AInum]
        if SVD:
            svd_result = np.linalg.svd(ai.params['W1'])
            return svd_result[2][i]
        if Grad:
            x = self.frame.cube.makedata().reshape(-1,1)
            return ai.grad(x,layer = layer,index = i).reshape(-1)
        if IG:
            x = self.frame.cube.makedata()
            return ai.integrated_grad(x,layer = layer,index = i).reshape(-1)
        return ai.params['W1'][i]

    def _is_megaminx_viewer(self):
        """Return whether the current cube exposes Megaminx-style feature ordering."""
        return hasattr(self.frame.cube, 'corner_key') and hasattr(self.frame.cube, 'edge_key') and self.frame.puzzle_type == 'megaminx'

    def _megaminx_viewer_states(self, vector, N):
        """Map Megaminx feature indices to a viewer state using the Megaminx makedata layout."""
        state_size = len(self.frame.cube.state)
        positive_state = np.zeros(state_size, dtype = str)
        negative_state = np.zeros(state_size, dtype = str)
        ordered_indices = np.argsort(vector)
        self._fill_megaminx_viewer_state(positive_state, ordered_indices[N-1::-1])
        self._fill_megaminx_viewer_state(negative_state, ordered_indices[-N:])
        return positive_state, negative_state

    def _fill_megaminx_viewer_state(self, state, ordered_indices):
        """Write selected Megaminx feature indices into a state array."""
        corner_limit = len(self.frame.cube.corner_index) * 60
        for vector_index in ordered_indices:
            if vector_index < corner_limit:
                self._write_megaminx_corner_to_state(state, vector_index)
            elif vector_index < self.frame.cube.ips:
                self._write_megaminx_edge_to_state(state, vector_index - corner_limit)

    def _write_megaminx_corner_to_state(self, state, vector_index):
        """Write one Megaminx corner feature to the viewer state."""
        position = self.frame.cube.corner_index[vector_index // 60]
        color = self.frame.cube.corner_colors[vector_index % 60]
        state[position[0]] = color[0]
        state[position[1]] = color[1]
        state[position[2]] = color[2]

    def _write_megaminx_edge_to_state(self, state, vector_index):
        """Write one Megaminx edge feature to the viewer state."""
        position = self.frame.cube.edge_index[vector_index // 60]
        color = self.frame.cube.edge_colors[vector_index % 60]
        state[position[0]] = color[0]
        state[position[1]] = color[1]

    def _supports_vector_viewer(self):
        """Return whether the current puzzle exposes the Rubiks-style feature metadata this viewer expects."""
        required_attrs = ('center_index', 'edge_index', 'corner_index', 'edge_colors', 'corner_colors')
        return all(hasattr(self.frame.cube, attr) for attr in required_attrs)

    def _viewer_states(self, vector, N):
        """ベクトルの上位N個と下位N個を、それぞれStateViewer用の状態に変換する。"""
        if self._is_megaminx_viewer():
            return self._megaminx_viewer_states(vector, N)

        state_size = 6 * self.frame.cube.surface_num
        positive_state = np.zeros(state_size,dtype = str)
        negative_state = np.zeros(state_size,dtype = str)
        if not self._supports_vector_viewer():
            return positive_state,negative_state

        ordered_indices = np.argsort(vector)
        self._fill_viewer_state(positive_state,ordered_indices[N-1::-1])
        self._fill_viewer_state(negative_state,ordered_indices[-N:])
        return positive_state,negative_state

    def _fill_viewer_state(self, state, ordered_indices):
        """選択された特徴index群をStateViewer用の色配列へ反映する。"""
        for vector_index in ordered_indices:
            self._write_vector_index_to_state(state,vector_index)

    def _write_vector_index_to_state(self, state, vector_index):
        """特徴indexがcenter/edge/cornerのどれに属するか判定して状態へ書き込む。"""
        center_limit = 36 * (self.frame.cube.size - 2) ** 2
        edge_limit = center_limit + len(self.frame.cube.edge_index) * 24
        if vector_index < center_limit:
            self._write_center_to_state(state,vector_index)
        elif vector_index < edge_limit:
            self._write_edge_to_state(state,vector_index,center_limit)
        else:
            self._write_corner_to_state(state,vector_index,edge_limit)

    def _write_center_to_state(self, state, vector_index):
        """center特徴のindexを該当ステッカー色として状態へ書き込む。"""
        position = self.frame.cube.center_index[vector_index // 6]
        color = self.frame.cube.colors[vector_index % 6]
        state[position[0]] = color[0]

    def _write_edge_to_state(self, state, vector_index, center_limit):
        """edge特徴のindexを2色のステッカー状態として書き込む。"""
        position = self.frame.cube.edge_index[(vector_index - center_limit) // 24]
        color = self.frame.cube.edge_colors[(vector_index - center_limit) % 24]
        state[position[0]] = color[0]
        state[position[1]] = color[1]

    def _write_corner_to_state(self, state, vector_index, edge_limit):
        """corner特徴のindexを3色のステッカー状態として書き込む。"""
        position = self.frame.cube.corner_index[(vector_index - edge_limit) // 24]
        color = self.frame.cube.corner_colors[(vector_index - edge_limit) % 24]
        state[position[0]] = color[0]
        state[position[1]] = color[1]
        state[position[2]] = color[2]


