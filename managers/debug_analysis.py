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
        self._last_occlusion_scores = []
        self._last_attention_scores = []
        self._last_attention_relation = None
        self._last_attention_mode = ''
        self._last_attention_error = ''
        self._last_embedding_scores = []
        self._last_embedding_mode = ''
        self._last_embedding_error = ''

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
        elif self.grad_mode == "Contrast":
            self.myviewer(ai_index,self.grad_index,N,Contrast = True)
        elif self.grad_mode == "Occ":
            self.myviewer(ai_index,self.grad_index,N,Occ = True)
        elif self.grad_mode == "PieceOcc":
            self.myviewer(ai_index,self.grad_index,N,PieceOcc = True)
        elif self.grad_mode == "PolicyOcc":
            self.myviewer(ai_index,self.grad_index,N,PolicyOcc = True)
        elif self.grad_mode == "PiecePolicyOcc":
            self.myviewer(ai_index,self.grad_index,N,PiecePolicyOcc = True)
        elif self.grad_mode == "AttnIn":
            self.myviewer(ai_index,self.grad_index,N,AttnIn = True)
        elif self.grad_mode == "AttnOut":
            self.myviewer(ai_index,self.grad_index,N,AttnOut = True)
        elif self.grad_mode == "AttnCentral":
            self.myviewer(ai_index,self.grad_index,N,AttnCentral = True)
        elif self.grad_mode == "EmbNorm":
            self.myviewer(ai_index,self.grad_index,N,EmbNorm = True)
        elif self.grad_mode == "EmbPC1":
            self.myviewer(ai_index,self.grad_index,N,EmbPC1 = True)
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
        ai.mark_params_dirty()
        ai.set_perfect_val()

    def re_activate(self, index):
        """更新量が小さいユニットを検出し、バイアスと一部重みを再活性化する。"""
        ai = self.frame.AIs[index]
        for key in ai.params.keys():
            if self._is_reactivation_target(key):
                self._reactivate_param(ai,key)
        ai.mark_params_dirty()

    def show_transformer_attention_analysis(self, ai_index):
        """W1 token 化と Att1 attention をパーツ単位に戻して表示する。"""
        content = self.transformer_attention_analysis_text(ai_index)
        self.frame.show_analysis_text(f'transformer attention analysis (ai={ai_index})', content)

    def show_transformer_embedding_analysis(self, ai_index):
        """Aff1 が作る piece embedding の大きさ・類似関係を表示する。"""
        content = self.transformer_embedding_analysis_text(ai_index)
        self.frame.show_analysis_text(f'transformer embedding analysis (ai={ai_index})', content)

    def transformer_attention_analysis_text(self, ai_index):
        ai = self.frame.AIs[ai_index]
        if not self._supports_original_attention_analysis(ai):
            return (
                f'AI {ai_index} does not expose Original Transformer attention.\n'
                'Required: params W1/WQ1/WK1/WV1 and layer Att1.\n'
                'Use an Original Rubiks_3_AI with use_transformer_attention=True.'
            )

        x = self.frame.cube.makedata().reshape(-1,1)
        policy_value = ai.predict(x, policy = True, value = True, loss = False, retain_cache = True)
        logits = policy_value[:-1,0]
        value = float(policy_value[-1,0])
        attention_layer = self._original_attention_layer(ai)
        attention = np.asarray(attention_layer.M[0], dtype = 'f')
        token_count = attention.shape[0]
        blocks = self._piece_feature_blocks()
        if getattr(ai,'use_piece_tokens',False):
            piece_names, saliency = self._piece_saliency(ai, x, blocks)
            token_vectors = attention_layer.tokens[:,:,0]
            w1_mass = np.linalg.norm(token_vectors, axis = 1)
            relation = attention[:len(piece_names),:len(piece_names)]
        else:
            piece_names, part_token, saliency = self._attention_piece_projection(ai, x, blocks)
            w1_mass = np.sum(part_token, axis = 1)
            relation = part_token @ attention @ part_token.T
        relation = self._zero_relation_diagonal(relation)
        centrality = np.sum(relation, axis = 0) + np.sum(relation, axis = 1)
        entropy_rows = self._attention_entropy_rows(attention)

        lines = [
            f'AI: {ai_index}',
            f'value: {value:.6f}',
            f'top policy: {self._top_policy_text(logits, top_n = 5)}',
            f'token_count: {token_count}',
            f'attention entropy mean/min/max: {float(np.mean(entropy_rows)):.4f} / {float(np.min(entropy_rows)):.4f} / {float(np.max(entropy_rows)):.4f}',
            f'attention max mean/max: {float(np.mean(np.max(attention, axis = 1))):.4f} / {float(np.max(attention)):.4f}',
            '',
            '[Part Importance: value grad * input]',
        ]
        lines += self._format_ranked_scores(piece_names, saliency, top_n = 20)
        lines += [
            '',
            '[Part Importance: W1-token mass]',
        ]
        lines += self._format_ranked_scores(piece_names, w1_mass, top_n = 20)
        lines += [
            '',
            '[Part Importance: attention centrality]',
        ]
        lines += self._format_ranked_scores(piece_names, centrality, top_n = 20)
        lines += [
            '',
            '[Part Relations: query -> key]',
        ]
        lines += self._format_relation_scores(piece_names, relation, top_n = 30)
        lines += [
            '',
            '[Token Diagnostics]',
        ]
        if getattr(ai,'use_piece_tokens',False):
            lines += self._format_piece_token_diagnostics(attention, token_vectors, piece_names, top_n = 12)
        else:
            lines += self._format_token_diagnostics(ai, x, attention, part_token, piece_names, top_n = 12)
        return '\n'.join(lines)

    def transformer_embedding_analysis_text(self, ai_index):
        ai = self.frame.AIs[ai_index]
        if not self._supports_original_attention_analysis(ai):
            return (
                f'AI {ai_index} does not expose Original Transformer embeddings.\n'
                'Required: params W1/WQ1/WK1/WV1 and layer Aff1.\n'
                'Use an Original Rubiks_3_AI with use_transformer_attention=True.'
            )

        x = self.frame.cube.makedata().reshape(-1,1)
        ai.predict(x, policy = True, value = True, loss = False, retain_cache = True)
        blocks = self._piece_feature_blocks()
        piece_names, embeddings = self._piece_embedding_matrix(ai, x, blocks)
        norms = np.linalg.norm(embeddings, axis = 1)
        cosine = self._embedding_cosine_matrix(embeddings)
        centered = embeddings - np.mean(embeddings, axis = 0, keepdims = True)
        svd_values, explained, pc1_scores = self._embedding_svd_summary(centered)

        lines = [
            f'AI: {ai_index}',
            f'embedding_count: {embeddings.shape[0]}',
            f'embedding_dim: {embeddings.shape[1] if embeddings.ndim == 2 else 0}',
            f'norm mean/min/max: {float(np.mean(norms)):.6f} / {float(np.min(norms)):.6f} / {float(np.max(norms)):.6f}',
            '',
            '[Embedding Norm]',
        ]
        lines += self._format_ranked_scores(piece_names, norms, top_n = 20)
        lines += [
            '',
            '[Embedding PC1 Score]',
        ]
        lines += self._format_ranked_scores(piece_names, pc1_scores, top_n = 12)
        lines += [
            '',
            '[Embedding PC1 Score: negative side]',
        ]
        lines += self._format_ranked_scores(piece_names, -pc1_scores, top_n = 12)
        lines += [
            '',
            '[Nearest Embedding Pairs: cosine]',
        ]
        lines += self._format_embedding_pair_scores(piece_names, cosine, largest = True, top_n = 30)
        lines += [
            '',
            '[Opposite Embedding Pairs: cosine]',
        ]
        lines += self._format_embedding_pair_scores(piece_names, cosine, largest = False, top_n = 20)
        lines += [
            '',
            '[Embedding Type Similarity]',
        ]
        lines += self._format_embedding_type_similarity(piece_names, cosine)
        lines += [
            '',
            '[Embedding SVD]',
            '  singular values: ' + ', '.join(f'{float(value):.5f}' for value in svd_values[:8]),
            '  explained ratio: ' + ', '.join(f'{float(value):.4f}' for value in explained[:8]),
        ]

        relation_names, relation = self._current_attention_relation(ai, x, blocks)
        if relation is not None and len(relation_names) == len(piece_names):
            lines += [
                '',
                '[Attention vs Embedding]',
                f'  pearson(attention, cosine): {self._relation_correlation(relation, cosine): .6f}',
                '',
                '[Strong Attention Relations with Embedding Cosine]',
            ]
            lines += self._format_attention_embedding_pairs(piece_names, relation, cosine, top_n = 20)
        return '\n'.join(lines)

    def _supports_original_attention_analysis(self, ai):
        return (
            hasattr(ai, 'params')
            and all(key in ai.params for key in ('W1','WQ1','WK1','WV1'))
            and hasattr(ai, 'layers')
            and self._original_attention_layer(ai) is not None
        )

    def _original_attention_layer(self, ai):
        if hasattr(ai,'layers') and 'Att1' in ai.layers:
            return ai.layers['Att1']
        if hasattr(ai,'layers') and 'Aff1' in ai.layers and hasattr(ai.layers['Aff1'],'M'):
            return ai.layers['Aff1']
        return None

    def _piece_saliency(self, ai, x, blocks):
        try:
            grad = ai.grad(x, layer = 'WO_V').reshape(-1)
            feature_saliency = np.abs(grad * x.reshape(-1))
        except Exception:
            feature_saliency = np.zeros((x.shape[0],), dtype = 'f')
        piece_names = []
        saliency = []
        max_count = len(getattr(ai.layers['Aff1'],'piece_feature_indices',blocks))
        for name, mask in blocks[:max_count]:
            piece_names.append(name)
            saliency.append(float(np.sum(feature_saliency[mask])))
        return piece_names, np.asarray(saliency,dtype = 'f')

    def _attention_piece_projection(self, ai, x, blocks):
        contribution = np.zeros((len(blocks), ai.params['W1'].shape[0]), dtype = 'f')
        saliency = np.zeros((len(blocks),), dtype = 'f')
        try:
            grad = ai.grad(x, layer = 'WO_V').reshape(-1)
            feature_saliency = np.abs(grad * x.reshape(-1))
        except Exception:
            feature_saliency = np.zeros((x.shape[0],), dtype = 'f')

        for piece_index, (_, mask) in enumerate(blocks):
            if np.any(mask):
                contribution[piece_index] = np.sum(np.abs(ai.params['W1'][:,mask] * x[mask,0].reshape(1,-1)), axis = 1)
                saliency[piece_index] = float(np.sum(feature_saliency[mask]))

        part_token = self._normalize_columns(contribution)
        piece_names = [name for name, _ in blocks]
        return piece_names, part_token, saliency

    def _normalize_columns(self, matrix):
        denom = np.sum(matrix, axis = 0, keepdims = True)
        normalized = np.zeros_like(matrix, dtype = 'f')
        np.divide(matrix, denom, out = normalized, where = denom > 1.0e-8)
        return normalized

    def _zero_relation_diagonal(self, relation):
        relation = relation.copy()
        if relation.size > 0:
            np.fill_diagonal(relation, 0.0)
        return relation

    def _attention_entropy_rows(self, attention):
        return -np.sum(attention * np.log(attention + 1.0e-8), axis = 1)

    def _top_policy_text(self, logits, top_n = 5):
        ordered = np.argsort(logits)[-top_n:][::-1]
        items = []
        for index in ordered:
            move = self.frame.display_move_sequence((self.frame.move_keys[int(index)],))[0]
            items.append(f'{move}:{float(logits[index]):.4f}')
        return ', '.join(items)

    def _format_ranked_scores(self, names, scores, top_n = 20):
        if len(scores) == 0:
            return ['  (none)']
        ordered = np.argsort(scores)[-min(top_n, len(scores)):][::-1]
        return [f'  {rank:02d}. {names[index]:<28} {float(scores[index]): .6f}' for rank, index in enumerate(ordered, 1)]

    def _format_relation_scores(self, names, relation, top_n = 30):
        if relation.size == 0:
            return ['  (none)']
        flat = relation.reshape(-1)
        positive_indices = np.where(flat > 0)[0]
        if positive_indices.size == 0:
            return ['  (none)']
        selected = positive_indices[np.argsort(flat[positive_indices])[-min(top_n, positive_indices.size):][::-1]]
        lines = []
        width = relation.shape[1]
        for rank, flat_index in enumerate(selected, 1):
            source = int(flat_index // width)
            target = int(flat_index % width)
            lines.append(f'  {rank:02d}. {names[source]} -> {names[target]}  {float(relation[source,target]): .6f}')
        return lines

    def _format_token_diagnostics(self, ai, x, attention, part_token, piece_names, top_n = 12):
        aff_out = ai.layers['Aff1'].out[:,0] if getattr(ai.layers['Aff1'], 'out', None) is not None else ai.params['W1'] @ x[:,0]
        token_score = np.abs(aff_out) * (np.sum(attention, axis = 0) + np.sum(attention, axis = 1))
        ordered = np.argsort(token_score)[-min(top_n, token_score.size):][::-1]
        lines = []
        for rank, token_index in enumerate(ordered, 1):
            owner_index = int(np.argmax(part_token[:,token_index])) if part_token.shape[0] > 0 else -1
            owner = piece_names[owner_index] if owner_index >= 0 else 'n/a'
            entropy = -float(np.sum(attention[token_index] * np.log(attention[token_index] + 1.0e-8)))
            max_target = int(np.argmax(attention[token_index]))
            target_owner_index = int(np.argmax(part_token[:,max_target])) if part_token.shape[0] > 0 else -1
            target_owner = piece_names[target_owner_index] if target_owner_index >= 0 else 'n/a'
            lines.append(
                f'  {rank:02d}. token={int(token_index):03d} score={float(token_score[token_index]): .6f} '
                f'act={float(aff_out[token_index]): .6f} entropy={entropy:.4f} '
                f'owner={owner} max_attn_token={max_target:03d} max_attn_part={target_owner} '
                f'max_attn={float(attention[token_index,max_target]):.4f}'
            )
        return lines

    def _format_piece_token_diagnostics(self, attention, token_vectors, piece_names, top_n = 12):
        centrality = np.sum(attention, axis = 0) + np.sum(attention, axis = 1)
        token_norm = np.linalg.norm(token_vectors, axis = 1)
        token_score = token_norm * centrality
        ordered = np.argsort(token_score)[-min(top_n, token_score.size):][::-1]
        lines = []
        for rank, token_index in enumerate(ordered, 1):
            entropy = -float(np.sum(attention[token_index] * np.log(attention[token_index] + 1.0e-8)))
            max_target = int(np.argmax(attention[token_index]))
            owner = piece_names[token_index] if token_index < len(piece_names) else 'n/a'
            target_owner = piece_names[max_target] if max_target < len(piece_names) else 'n/a'
            lines.append(
                f'  {rank:02d}. piece_token={int(token_index):03d} score={float(token_score[token_index]): .6f} '
                f'norm={float(token_norm[token_index]): .6f} entropy={entropy:.4f} '
                f'piece={owner} max_attn_piece={target_owner} max_attn={float(attention[token_index,max_target]):.4f}'
            )
        return lines

    def myviewer(self, AInum, i, N = 1, SVD = False, Grad = False, IG = False, Contrast = False, Occ = False, PieceOcc = False, PolicyOcc = False, PiecePolicyOcc = False, AttnIn = False, AttnOut = False, AttnCentral = False, EmbNorm = False, EmbPC1 = False, layer = "WO_V"):
        """指定した重み・勾配・SVD成分をキューブ状態として可視化する。"""
        vector = self._viewer_vector(AInum,i,SVD,Grad,IG,Contrast,Occ,PieceOcc,PolicyOcc,PiecePolicyOcc,AttnIn,AttnOut,AttnCentral,EmbNorm,EmbPC1,layer)
        positive_state,negative_state = self._viewer_states(vector,N)
        self.frame.grad_viewer_positive.set_color(positive_state)
        self.frame.grad_viewer_negative.set_color(negative_state)
        self.frame.set_grad_viewer_info(
            self._viewer_label_text(AInum),
            self._viewer_range_text(vector,N,positive = True),
            self._viewer_range_text(vector,N,positive = False),
        )
        if Contrast:
            self._log_policy_contrast(AInum)
        if Occ or PieceOcc or PolicyOcc or PiecePolicyOcc:
            if Occ:
                mode_name = 'group'
            elif PieceOcc:
                mode_name = 'piece'
            elif PolicyOcc:
                mode_name = 'policy-group'
            else:
                mode_name = 'policy-piece'
            self._show_occlusion_scores(AInum, mode_name)
        if AttnIn or AttnOut or AttnCentral:
            self._show_attention_scores(AInum)
        if EmbNorm or EmbPC1:
            self._show_embedding_scores(AInum)

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

    def _viewer_label_text(self, ai_index):
        """GradViewerの対象情報を短く表示する。"""
        return f'AI {ai_index}  mode={self.grad_mode}  idx={self.grad_index}  layer={self.grad_layer}'

    def _viewer_range_text(self, vector, N, positive):
        """色付け対象として選んだ値のrangeを表示用文字列にする。"""
        selected_values = self._selected_viewer_values(vector,N,positive)
        label = 'High value' if positive else 'Low value'
        if selected_values.size == 0:
            return f'{label}: n=0'
        return (
            f'{label}: n={selected_values.size}  '
            f'[{float(np.min(selected_values)): .4g} .. {float(np.max(selected_values)): .4g}]'
        )

    def _selected_viewer_values(self, vector, N, positive):
        """Positive/Negative viewerで実際に選ぶ特徴値を返す。"""
        flat_vector = np.asarray(vector).reshape(-1)
        if flat_vector.size == 0:
            return np.zeros((0,), dtype = 'f')
        count = max(0,min(int(N),flat_vector.size))
        if count == 0:
            return np.zeros((0,), dtype = 'f')
        ordered_indices = np.argsort(flat_vector)
        if positive:
            selected_indices = ordered_indices[-count:]
        else:
            selected_indices = ordered_indices[:count]
        return flat_vector[selected_indices]

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

    def _viewer_vector(self, AInum, i, SVD, Grad, IG, Contrast, Occ, PieceOcc, PolicyOcc, PiecePolicyOcc, AttnIn, AttnOut, AttnCentral, EmbNorm, EmbPC1, layer):
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
        if Contrast:
            return self._policy_contrast_vector(ai)
        if Occ:
            return self._occlusion_vector(ai, self._group_feature_blocks())
        if PieceOcc:
            return self._occlusion_vector(ai, self._piece_feature_blocks())
        if PolicyOcc:
            return self._policy_occlusion_vector(ai, self._group_feature_blocks())
        if PiecePolicyOcc:
            return self._policy_occlusion_vector(ai, self._piece_feature_blocks())
        if AttnIn or AttnOut or AttnCentral:
            return self._transformer_attention_vector(ai, AttnIn, AttnOut, AttnCentral)
        if EmbNorm or EmbPC1:
            return self._transformer_embedding_vector(ai, EmbNorm, EmbPC1)
        return ai.params['W1'][i]

    def _policy_contrast_vector(self, ai):
        """Return grad(logit_top1 - logit_top2) with respect to input."""
        x = self.frame.cube.makedata().reshape(-1,1)
        logits = ai.predict(x, policy = True, value = False).reshape(-1)
        ordered = np.argsort(logits)
        top1 = int(ordered[-1])
        top2 = int(ordered[-2]) if len(ordered) >= 2 else top1
        grad_top1 = ai.grad(x, layer = "WO_P", index = top1).reshape(-1)
        grad_top2 = ai.grad(x, layer = "WO_P", index = top2).reshape(-1)
        self._last_policy_contrast = {
            'top1_index': top1,
            'top2_index': top2,
            'top1_move': self.frame.display_move_sequence((self.frame.move_keys[top1],))[0],
            'top2_move': self.frame.display_move_sequence((self.frame.move_keys[top2],))[0],
            'top1_logit': float(logits[top1]),
            'top2_logit': float(logits[top2]),
        }
        return grad_top1 - grad_top2

    def _log_policy_contrast(self, ai_index):
        """Log the top-1 vs top-2 policy contrast metadata."""
        if not hasattr(self, '_last_policy_contrast'):
            return
        info = self._last_policy_contrast
        self.frame.append_log(
            'contrast: ai={ai} {m1}({v1:.4f}) - {m2}({v2:.4f})'.format(
                ai = ai_index,
                m1 = info['top1_move'],
                v1 = info['top1_logit'],
                m2 = info['top2_move'],
                v2 = info['top2_logit'],
            )
        )

    def _occlusion_vector(self, ai, blocks):
        """Return a feature vector where each block is weighted by its value-drop under occlusion."""
        x = self.frame.cube.makedata().reshape(-1,1)
        base_value = float(ai.predict(x,policy = False,value = True)[0][0])
        vector = np.zeros((self.frame.cube.ips,),dtype = 'f')
        self._last_occlusion_scores = []
        for key, mask in blocks:
            occluded_x = x.copy()
            occluded_x[mask,0] = self.frame.cube.perfect_data[mask]
            occluded_value = float(ai.predict(occluded_x,policy = False,value = True)[0][0])
            score = base_value - occluded_value
            vector[mask] += score
            self._last_occlusion_scores.append((key, score))
        return vector

    def _show_occlusion_scores(self, ai_index, mode_name):
        """Log and show the most influential occlusion blocks."""
        if not self._last_occlusion_scores:
            return
        ordered_scores = sorted(self._last_occlusion_scores, key = lambda item: item[1], reverse = True)
        top_scores = ', '.join(f'{key}={score:.4f}' for key, score in ordered_scores[:5])
        if mode_name.startswith('policy') and hasattr(self, '_last_policy_occlusion'):
            info = self._last_policy_occlusion
            self.frame.append_log(
                f"{mode_name}-occ: ai={ai_index} "
                f"{info['top1_move']}-{info['top2_move']} margin={info['base_margin']:.4f} {top_scores}"
            )
        else:
            self.frame.append_log(f'{mode_name}-occ: ai={ai_index} {top_scores}')
        self.frame.show_analysis_scores(
            f'{mode_name} occlusion scores (ai={ai_index})',
            ordered_scores[: min(30, len(ordered_scores))],
        )

    def _transformer_attention_vector(self, ai, AttnIn, AttnOut, AttnCentral):
        """Return an input-feature vector that highlights Transformer attention by piece."""
        x = self.frame.cube.makedata().reshape(-1,1)
        vector = np.zeros((self.frame.cube.ips,), dtype = 'f')
        self._last_attention_scores = []
        self._last_attention_relation = None
        self._last_attention_error = ''
        if AttnOut:
            self._last_attention_mode = 'out'
        elif AttnIn:
            self._last_attention_mode = 'in'
        else:
            self._last_attention_mode = 'central'
        if not self._supports_original_attention_analysis(ai):
            self._last_attention_error = 'This AI does not expose Original Transformer attention.'
            return vector
        try:
            ai.predict(x, policy = True, value = True, loss = False, retain_cache = True)
            attention_layer = self._original_attention_layer(ai)
            attention = np.asarray(attention_layer.M[0], dtype = 'f')
            blocks = self._piece_feature_blocks()
            piece_names, relation = self._attention_piece_relation(ai, x, attention, blocks)
        except Exception as error:
            self._last_attention_error = str(error)
            return vector

        relation = self._zero_relation_diagonal(relation)
        if relation.size == 0:
            self._last_attention_error = 'Attention relation is empty.'
            return vector

        if AttnOut:
            scores = np.sum(relation, axis = 1)
            mode_name = 'out'
        elif AttnIn:
            scores = np.sum(relation, axis = 0)
            mode_name = 'in'
        else:
            scores = np.sum(relation, axis = 0) + np.sum(relation, axis = 1)
            mode_name = 'central'

        self._last_attention_scores = [(piece_names[index], float(scores[index])) for index in range(len(scores))]
        self._last_attention_relation = (piece_names, relation)
        self._last_attention_mode = mode_name
        return self._piece_scores_to_active_feature_vector(scores, blocks, x)

    def _attention_piece_relation(self, ai, x, attention, blocks):
        """Convert token-token attention into a piece-piece relation matrix."""
        if getattr(ai,'use_piece_tokens',False):
            piece_count = min(len(blocks), attention.shape[0])
            piece_names = [name for name, _ in blocks[:piece_count]]
            return piece_names, attention[:piece_count,:piece_count]
        piece_names, part_token, _ = self._attention_piece_projection(ai, x, blocks)
        relation = part_token @ attention @ part_token.T
        return piece_names, relation

    def _piece_scores_to_active_feature_vector(self, scores, blocks, x):
        """Map one score per piece to the currently active feature of that piece."""
        vector = np.zeros((self.frame.cube.ips,), dtype = 'f')
        flat_x = x.reshape(-1)
        for index, score in enumerate(scores[:len(blocks)]):
            mask = blocks[index][1]
            active_indices = np.where(mask & (flat_x > 0))[0]
            if active_indices.size == 0:
                active_indices = np.where(mask)[0][:1]
            vector[active_indices] = float(score)
        return vector

    def _show_attention_scores(self, ai_index):
        """Show attention piece scores and the strongest piece-to-piece relations."""
        title = f'transformer attention {self._last_attention_mode} (ai={ai_index})'
        if self._last_attention_error:
            self.frame.append_log(f'attention viewer: ai={ai_index} {self._last_attention_error}')
            self.frame.show_analysis_text(title, self._last_attention_error)
            return
        if not self._last_attention_scores:
            return

        ordered_scores = sorted(self._last_attention_scores, key = lambda item: item[1], reverse = True)
        top_scores = ', '.join(f'{key}={score:.4f}' for key, score in ordered_scores[:5])
        self.frame.append_log(f'transformer-attn-{self._last_attention_mode}: ai={ai_index} {top_scores}')

        lines = [
            title,
            '-' * len(title),
            '',
            '[Piece Scores]',
        ]
        names = [name for name, _ in self._last_attention_scores]
        scores = np.asarray([score for _, score in self._last_attention_scores], dtype = 'f')
        lines += self._format_ranked_scores(names, scores, top_n = 30)
        if self._last_attention_relation is not None:
            relation_names, relation = self._last_attention_relation
            lines += [
                '',
                '[Strong Relations: query -> key]',
            ]
            lines += self._format_relation_scores(relation_names, relation, top_n = 30)
        self.frame.show_analysis_text(title, '\n'.join(lines))

    def _transformer_embedding_vector(self, ai, EmbNorm, EmbPC1):
        """Return a feature vector that highlights Aff1 piece embeddings."""
        x = self.frame.cube.makedata().reshape(-1,1)
        vector = np.zeros((self.frame.cube.ips,), dtype = 'f')
        self._last_embedding_scores = []
        self._last_embedding_error = ''
        self._last_embedding_mode = 'norm' if EmbNorm else 'pc1'
        if not self._supports_original_attention_analysis(ai):
            self._last_embedding_error = 'This AI does not expose Original Transformer embeddings.'
            return vector
        try:
            ai.predict(x, policy = True, value = True, loss = False, retain_cache = True)
            blocks = self._piece_feature_blocks()
            piece_names, embeddings = self._piece_embedding_matrix(ai, x, blocks)
            if EmbNorm:
                scores = np.linalg.norm(embeddings, axis = 1)
            else:
                centered = embeddings - np.mean(embeddings, axis = 0, keepdims = True)
                _, _, scores = self._embedding_svd_summary(centered)
        except Exception as error:
            self._last_embedding_error = str(error)
            return vector
        self._last_embedding_scores = [(piece_names[index], float(scores[index])) for index in range(len(scores))]
        return self._piece_scores_to_active_feature_vector(scores, blocks, x)

    def _show_embedding_scores(self, ai_index):
        """Show the current embedding viewer scores and full embedding diagnostics."""
        title = f'transformer embedding {self._last_embedding_mode} (ai={ai_index})'
        if self._last_embedding_error:
            self.frame.append_log(f'embedding viewer: ai={ai_index} {self._last_embedding_error}')
            self.frame.show_analysis_text(title, self._last_embedding_error)
            return
        if self._last_embedding_scores:
            ordered_scores = sorted(self._last_embedding_scores, key = lambda item: item[1], reverse = True)
            top_scores = ', '.join(f'{key}={score:.4f}' for key, score in ordered_scores[:5])
            self.frame.append_log(f'transformer-emb-{self._last_embedding_mode}: ai={ai_index} {top_scores}')
        self.show_transformer_embedding_analysis(ai_index)

    def _piece_embedding_matrix(self, ai, x, blocks):
        """Return one Aff1 embedding vector per piece."""
        if getattr(ai,'use_piece_tokens',False):
            attention_layer = self._original_attention_layer(ai)
            embeddings = np.asarray(attention_layer.tokens[:,:,0], dtype = 'f')
            piece_count = min(len(blocks), embeddings.shape[0])
            piece_names = [name for name, _ in blocks[:piece_count]]
            return piece_names, embeddings[:piece_count]

        embedding_dim = ai.params['W1'].shape[0]
        embeddings = np.zeros((len(blocks), embedding_dim), dtype = 'f')
        for piece_index, (_, mask) in enumerate(blocks):
            if np.any(mask):
                embeddings[piece_index] = ai.params['W1'][:,mask] @ x[mask,0]
        piece_names = [name for name, _ in blocks]
        return piece_names, embeddings

    def _embedding_cosine_matrix(self, embeddings):
        """Return pairwise cosine similarity between piece embeddings."""
        norms = np.linalg.norm(embeddings, axis = 1, keepdims = True)
        normalized = np.zeros_like(embeddings, dtype = 'f')
        np.divide(embeddings, norms, out = normalized, where = norms > 1.0e-8)
        return normalized @ normalized.T

    def _embedding_svd_summary(self, centered_embeddings):
        """Return singular values, explained ratios and PC1 scores for embeddings."""
        if centered_embeddings.size == 0:
            return np.zeros((0,), dtype = 'f'), np.zeros((0,), dtype = 'f'), np.zeros((0,), dtype = 'f')
        try:
            _, singular_values, vh = np.linalg.svd(centered_embeddings, full_matrices = False)
        except np.linalg.LinAlgError:
            return np.zeros((0,), dtype = 'f'), np.zeros((0,), dtype = 'f'), np.zeros((centered_embeddings.shape[0],), dtype = 'f')
        total = float(np.sum(singular_values ** 2))
        explained = np.zeros_like(singular_values, dtype = 'f')
        if total > 1.0e-8:
            explained = (singular_values ** 2 / total).astype('f')
        if vh.shape[0] == 0:
            pc1_scores = np.zeros((centered_embeddings.shape[0],), dtype = 'f')
        else:
            pc1_scores = (centered_embeddings @ vh[0]).astype('f')
        return singular_values.astype('f'), explained, pc1_scores

    def _format_embedding_pair_scores(self, names, cosine, largest = True, top_n = 20):
        """Format strongest or most opposite embedding pairs."""
        if cosine.size == 0:
            return ['  (none)']
        pair_scores = []
        for source in range(cosine.shape[0]):
            for target in range(source + 1, cosine.shape[1]):
                pair_scores.append((float(cosine[source,target]), source, target))
        if not pair_scores:
            return ['  (none)']
        pair_scores.sort(key = lambda item: item[0], reverse = largest)
        lines = []
        for rank, (score, source, target) in enumerate(pair_scores[:min(top_n, len(pair_scores))], 1):
            lines.append(f'  {rank:02d}. {names[source]} <-> {names[target]}  {score: .6f}')
        return lines

    def _format_embedding_type_similarity(self, names, cosine):
        """Summarize cosine similarity grouped by piece label prefix."""
        groups = {}
        for index, name in enumerate(names):
            piece_type = name.split('-', 1)[0]
            groups.setdefault(piece_type, []).append(index)
        lines = []
        for source_type, source_indices in groups.items():
            for target_type, target_indices in groups.items():
                if source_type > target_type:
                    continue
                values = []
                for source in source_indices:
                    for target in target_indices:
                        if source >= target:
                            continue
                        values.append(float(cosine[source,target]))
                if values:
                    lines.append(f'  {source_type:<10} {target_type:<10} mean={float(np.mean(values)): .6f} n={len(values)}')
        return lines if lines else ['  (none)']

    def _current_attention_relation(self, ai, x, blocks):
        """Return the current piece-piece attention relation if available."""
        try:
            attention_layer = self._original_attention_layer(ai)
            attention = np.asarray(attention_layer.M[0], dtype = 'f')
            piece_names, relation = self._attention_piece_relation(ai, x, attention, blocks)
            return piece_names, self._zero_relation_diagonal(relation)
        except Exception:
            return None, None

    def _relation_correlation(self, relation, cosine):
        """Pearson correlation between off-diagonal attention relation and embedding cosine."""
        if relation.shape != cosine.shape or relation.size == 0:
            return 0.0
        mask = ~np.eye(relation.shape[0], dtype = bool)
        x = relation[mask].reshape(-1)
        y = cosine[mask].reshape(-1)
        if x.size == 0 or float(np.std(x)) < 1.0e-8 or float(np.std(y)) < 1.0e-8:
            return 0.0
        return float(np.corrcoef(x, y)[0,1])

    def _format_attention_embedding_pairs(self, names, relation, cosine, top_n = 20):
        """Format strong attention edges with their embedding cosine."""
        if relation.size == 0:
            return ['  (none)']
        flat = relation.reshape(-1)
        positive_indices = np.where(flat > 0)[0]
        if positive_indices.size == 0:
            return ['  (none)']
        selected = positive_indices[np.argsort(flat[positive_indices])[-min(top_n, positive_indices.size):][::-1]]
        width = relation.shape[1]
        lines = []
        for rank, flat_index in enumerate(selected, 1):
            source = int(flat_index // width)
            target = int(flat_index % width)
            lines.append(
                f'  {rank:02d}. {names[source]} -> {names[target]}  '
                f'attn={float(relation[source,target]): .6f} cos={float(cosine[source,target]): .6f}'
            )
        return lines

    def _policy_occlusion_vector(self, ai, blocks):
        """Return a feature vector weighted by top1-vs-top2 policy margin drop under occlusion."""
        x = self.frame.cube.makedata().reshape(-1,1)
        logits = ai.predict(x, policy = True, value = False).reshape(-1)
        ordered = np.argsort(logits)
        top1 = int(ordered[-1])
        top2 = int(ordered[-2]) if len(ordered) >= 2 else top1
        base_margin = float(logits[top1] - logits[top2])
        vector = np.zeros((self.frame.cube.ips,), dtype = 'f')
        self._last_occlusion_scores = []
        self._last_policy_occlusion = {
            'top1_index': top1,
            'top2_index': top2,
            'top1_move': self.frame.display_move_sequence((self.frame.move_keys[top1],))[0],
            'top2_move': self.frame.display_move_sequence((self.frame.move_keys[top2],))[0],
            'base_margin': base_margin,
        }
        for key, mask in blocks:
            occluded_x = x.copy()
            occluded_x[mask,0] = self.frame.cube.perfect_data[mask]
            occluded_logits = ai.predict(occluded_x, policy = True, value = False).reshape(-1)
            occluded_margin = float(occluded_logits[top1] - occluded_logits[top2])
            score = base_margin - occluded_margin
            vector[mask] += score
            self._last_occlusion_scores.append((key, score))
        return vector

    def _group_feature_blocks(self):
        """Return boolean feature masks for each solve group."""
        blocks = []
        for key, group_vector in self.frame.cube.group_val.items():
            blocks.append((key, group_vector.reshape(-1) > 0))
        return blocks

    def _piece_feature_blocks(self):
        """Return boolean feature masks for each piece-sized input block."""
        if self._is_megaminx_viewer():
            return self._megaminx_piece_feature_blocks()
        if self._has_generic_piece_feature_layout():
            return self._generic_piece_feature_blocks()
        return self._rubiks_piece_feature_blocks()

    def _rubiks_piece_feature_blocks(self):
        """Build Rubiks piece-level feature masks from makedata layout."""
        blocks = []
        offset = 0
        for piece in self.frame.cube.center_index:
            mask = np.zeros((self.frame.cube.ips,), dtype = bool)
            mask[offset:offset + 6] = True
            blocks.append((self._piece_block_label('Center', piece), mask))
            offset += 6
        for piece in self.frame.cube.edge_index:
            mask = np.zeros((self.frame.cube.ips,), dtype = bool)
            mask[offset:offset + 24] = True
            blocks.append((self._piece_block_label('Edge', piece), mask))
            offset += 24
        for piece in self.frame.cube.corner_index:
            mask = np.zeros((self.frame.cube.ips,), dtype = bool)
            mask[offset:offset + 24] = True
            blocks.append((self._piece_block_label('Corner', piece), mask))
            offset += 24
        return blocks

    def _megaminx_piece_feature_blocks(self):
        """Build Megaminx piece-level feature masks from makedata layout."""
        blocks = []
        offset = 0
        for piece in self.frame.cube.corner_index:
            mask = np.zeros((self.frame.cube.ips,), dtype = bool)
            mask[offset:offset + 60] = True
            blocks.append((self._piece_block_label('Corner', piece), mask))
            offset += 60
        for piece in self.frame.cube.edge_index:
            mask = np.zeros((self.frame.cube.ips,), dtype = bool)
            mask[offset:offset + 60] = True
            blocks.append((self._piece_block_label('Edge', piece), mask))
            offset += 60
        return blocks

    def _generic_piece_feature_blocks(self):
        """Build piece-level feature masks from puzzle-provided feature offsets."""
        blocks = []
        for group_name, pieces in self.frame.cube.group_pieces.items():
            for piece in pieces:
                offset, feature_size = self.frame.cube.piece_feature_offsets[piece]
                mask = np.zeros((self.frame.cube.ips,), dtype = bool)
                mask[offset:offset + feature_size] = True
                blocks.append((self._piece_block_label(group_name, piece), mask))
        return blocks

    def _piece_block_label(self, piece_type, piece):
        """Format a piece label using sticker indices so the target piece is identifiable."""
        if hasattr(self.frame.cube, 'piece_display_name'):
            return self.frame.cube.piece_display_name(piece_type, piece)
        return f"{piece_type}-{self._piece_indices_text(piece)}"

    def _piece_indices_text(self, piece):
        """Convert a piece tuple like (12, 34, 56) to a compact label."""
        return '-'.join(f'{index:02d}' for index in piece)

    def _is_megaminx_viewer(self):
        """Return whether the current cube exposes Megaminx-style feature ordering."""
        return hasattr(self.frame.cube, 'corner_key') and hasattr(self.frame.cube, 'edge_key') and self.frame.puzzle_type == 'megaminx'

    def _is_pyraminx_viewer(self):
        """Return whether the current cube exposes Pyraminx piece-feature ordering."""
        return (
            self.frame.puzzle_type in ('pyraminx', 'master_pyraminx')
            and hasattr(self.frame.cube, 'feature_index_to_piece_color')
        )

    def _has_generic_piece_feature_layout(self):
        """Return whether the current puzzle can map feature indices back to pieces."""
        return (
            hasattr(self.frame.cube, 'feature_index_to_piece_color')
            and hasattr(self.frame.cube, 'piece_feature_offsets')
            and hasattr(self.frame.cube, 'group_pieces')
        )

    def _megaminx_viewer_states(self, vector, N):
        """Map Megaminx feature indices to a viewer state using the Megaminx makedata layout."""
        state_size = len(self.frame.cube.state)
        positive_state = np.zeros(state_size, dtype = str)
        negative_state = np.zeros(state_size, dtype = str)
        positive_indices, negative_indices = self._viewer_ordered_indices(vector, N)
        self._fill_megaminx_viewer_state(positive_state, positive_indices)
        self._fill_megaminx_viewer_state(negative_state, negative_indices)
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

    def _pyraminx_viewer_states(self, vector, N):
        """Map Pyraminx piece-feature indices to a viewer state."""
        state_size = len(self.frame.cube.state)
        positive_state = np.zeros(state_size, dtype = str)
        negative_state = np.zeros(state_size, dtype = str)
        positive_indices, negative_indices = self._viewer_ordered_indices(vector, N)
        self._fill_pyraminx_viewer_state(positive_state, positive_indices)
        self._fill_pyraminx_viewer_state(negative_state, negative_indices)
        return positive_state, negative_state

    def _fill_pyraminx_viewer_state(self, state, ordered_indices):
        """Write selected Pyraminx feature indices into a state array."""
        for vector_index in ordered_indices:
            if vector_index not in self.frame.cube.feature_index_to_piece_color:
                continue
            piece, color = self.frame.cube.feature_index_to_piece_color[vector_index]
            for sticker_index, sticker_color in zip(piece, color):
                state[sticker_index] = sticker_color

    def _supports_vector_viewer(self):
        """Return whether the current puzzle exposes the Rubiks-style feature metadata this viewer expects."""
        required_attrs = ('center_index', 'edge_index', 'corner_index', 'edge_colors', 'corner_colors')
        return all(hasattr(self.frame.cube, attr) for attr in required_attrs)

    def _viewer_states(self, vector, N):
        """ベクトルの上位N個と下位N個を、それぞれStateViewer用の状態に変換する。"""
        if self._is_megaminx_viewer():
            return self._megaminx_viewer_states(vector, N)
        if self._is_pyraminx_viewer() or self.frame.puzzle_type == 'skewb' or self._has_generic_piece_feature_layout():
            return self._pyraminx_viewer_states(vector, N)

        state_size = 6 * self.frame.cube.surface_num
        positive_state = np.zeros(state_size,dtype = str)
        negative_state = np.zeros(state_size,dtype = str)
        if not self._supports_vector_viewer():
            return positive_state,negative_state

        positive_indices, negative_indices = self._viewer_ordered_indices(vector, N)
        self._fill_viewer_state(positive_state,positive_indices)
        self._fill_viewer_state(negative_state,negative_indices)
        return positive_state,negative_state

    def _viewer_ordered_indices(self, vector, N):
        """Positiveは大きい値、Negativeは小さい値を選ぶ。"""
        flat_vector = np.asarray(vector).reshape(-1)
        if flat_vector.size == 0:
            return np.asarray([], dtype = int), np.asarray([], dtype = int)
        count = max(0,min(int(N),flat_vector.size))
        if count == 0:
            return np.asarray([], dtype = int), np.asarray([], dtype = int)
        ordered_indices = np.argsort(flat_vector)
        positive_indices = ordered_indices[-count:][::-1]
        negative_indices = ordered_indices[:count]
        return positive_indices, negative_indices

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
