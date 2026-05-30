"""Rubiks AI model and its local layer/loss implementations."""

import gc
import math
import random
from collections import OrderedDict

import numpy as np

try:
    import torch
    import torch.nn.functional as F_torch
except Exception:
    torch = None
    F_torch = None

from cube.search2_engine import Search2Engine
from cube.search3_engine import Search3Engine
from cube.rubiks_cube import Rubiks_3
from ai.layers import Affine, Batch_Normalization, Hard_Sigmoid, ReLU, Sigmoid
from ai.losses import MSE, Myloss, Q_loss, Soft_Target_Cross_Entropy, Softmax_Cross_Entropy



class Rubiks_3_AI:
    def __init__(self,Mid,cube_size = 3,Activation = 'ReLU',cube = None,Batch_Normalize = False,search_mode = 'search2'):
        if cube == None:
            self.cube = Rubiks_3(size = cube_size)
        else:
            self.cube = cube
        #self.ips = 36 * self.cube.surface_num
        self.Batch_Normalize = Batch_Normalize
        self.activation = Activation
        self.ips = self.cube.ips
        self.ops = self.cube.move_len
        self.Mid = Mid

        self.skip_search = False
        self.skip_difference = 10.0
        self.search_mode = search_mode
        self.value_target_gamma = (1/2) ** (1/20)
        




        self.myval = False
        self.weight_decay = False
        self.adam = True
        self.cube_size = cube_size
        self.surface_num = self.cube.surface_num







        self.layers = OrderedDict()
        self.params = {}
        
        
        
        self.affines = ['Aff1']
        self.BNs = []
        
        self.layers['Aff1'] = Affine(self.ips,Mid[0])
        if self.Batch_Normalize:
            self.layers['BN1'] = Batch_Normalization(Mid[0])
            self.BNs.append('BN1')
        
        if Activation == 'ReLU':
            self.layers['Act1'] = ReLU()
        elif Activation == 'Hard_Sigmoid':
            self.layers['Act1'] = ReLU()
        else:
            self.layers['Act1'] = ReLU()
        
        self.params['W1'] = self.layers['Aff1'].W
        self.params['B1'] = self.layers['Aff1'].B

        if self.Batch_Normalize:
            self.params['BNg1'] = self.layers['BN1'].g
            self.params['BNb1'] = self.layers['BN1'].b
            self.params['BNm1'] = self.layers['BN1'].m
            self.params['BNs1'] = self.layers['BN1'].s

        
        for i in range(1,len(Mid)):
            self.layers['Aff' + str(i+1)] = Affine(Mid[i-1],Mid[i])
            if self.Batch_Normalize:
                self.layers['BN' + str(i+1)] =  Batch_Normalization(Mid[i])
            if Activation == 'ReLU':
                self.layers['Act' + str(i+1)] = ReLU()
            elif Activation == 'Hard_Sigmoid':
                self.layers['Act' + str(i+1)] = ReLU()
            else:
                self.layers['Act' + str(i+1)] = ReLU()

            self.params['W' + str(i + 1)] = self.layers['Aff' + str(i + 1)].W
            self.params['B' + str(i + 1)] = self.layers['Aff' + str(i + 1)].B
            self.affines.append('Aff' + str(i+1))
            if self.Batch_Normalize:
                self.params['BNg' + str(i+1)] = self.layers['BN' + str(i+1)].g
                self.params['BNb' + str(i+1)] = self.layers['BN' + str(i+1)].b
                self.params['BNm' + str(i+1)] = self.layers['BN' + str(i+1)].m
                self.params['BNs' + str(i+1)] = self.layers['BN' + str(i+1)].s
            
                self.BNs.append('BN' + str(i+1))


        self.policy_mid = Affine(Mid[-1],Mid[-1] // 2)
        self.value_mid = Affine(Mid[-1],Mid[-1] // 2)

        if self.Batch_Normalize:
            self.policy_BN = Batch_Normalization(Mid[-1] // 2)
            self.value_BN = Batch_Normalization(Mid[-1] // 2)

        if Activation == 'ReLU':
            self.policy_act = ReLU()
            self.value_act = ReLU()
        elif Activation == 'Hard_Sigmoid':
            self.policy_act = Hard_Sigmoid()
            self.value_act = Hard_Sigmoid()           
        else:
            self.policy_act = Sigmoid()
            self.value_act = Sigmoid()
        
        
        self.policy_layer = Affine(Mid[-1] // 2,self.ops)
        self.value_layer = Affine(Mid[-1] // 2,1)

        self.params['WM_P'] = self.policy_mid.W
        self.params['BM_P'] = self.policy_mid.B

        self.params['WM_V'] = self.value_mid.W
        self.params['BM_V'] = self.value_mid.B


        if self.Batch_Normalize:
            self.params['BNgP'] = self.policy_BN.g
            self.params['BNbP'] = self.policy_BN.b
            self.params['BNmP'] = self.policy_BN.m
            self.params['BNsP'] = self.policy_BN.s

            self.params['BNgV'] = self.value_BN.g
            self.params['BNbV'] = self.value_BN.b
            self.params['BNmV'] = self.value_BN.m
            self.params['BNsV'] = self.value_BN.s

        self.params['WO_P'] = self.policy_layer.W
        self.params['BO_P'] = self.policy_layer.B

        self.params['WO_V'] = self.value_layer.W
        self.params['BO_V'] = self.value_layer.B
        
        self.params['BO_P'][:] = np.random.uniform(-5,5,self.params['BO_P'].shape)

        self.v = {}
        for key in self.params.keys():
            self.v[key] = np.zeros_like(self.params[key],dtype = 'f')

        self.h = {}
        for key in self.params.keys():
            self.h[key] = np.zeros_like(self.params[key],dtype = 'f')        

    
            
        self.lr = 1.0e-3
        self.wdlr = 1.0e-6
        self.PV_ratio = 1
        self.lr_C = 1
        self.out_C = 1.0
        self.lr_v = 0.99
        self.lr_h = 0.99

        self.losslayer = Softmax_Cross_Entropy()
        self.losslayer2 = Myloss()
        self.losslayer3 = MSE()
        self.losslayer4 = Soft_Target_Cross_Entropy()
        self.search3_value_sigmoid = Sigmoid()




        self.scramble_num = 3
        self.scramble_num_min = 2
        self.solve_num = 30
        self.datas = []
        self.indices = []
        self.datas_search3 = []
        self.indices_search3 = []


        self.myperms = {}
        self.nodes = {}
        self.search_num2 = 10000
        self.search_num3 = 1000
        self.search_repeat3 = 10
        self.search_batch3 = 40
        self.search_depth3 = 200
        self.search3_C = 0.05
        self.perfect_val = 1.0
        self._torch_params_cache = None
        self._torch_params_dirty = True
        self._torch_params_device = None
        self._search3_policy_transform_cache = {}
        self.search2_engine = Search2Engine(self)
        self.search3_engine = Search3Engine(self)
        self.set_perfect_val()
        
        
        


    def set_perfect_val(self):
        self.perfect_val = self.predict(self.cube.perfect_data.reshape(-1,1),False,True)[0][0]

    def mark_params_dirty(self):
        self._torch_params_dirty = True
        self._torch_params_cache = None
        self._torch_params_device = None
        if hasattr(self,'search3_engine'):
            self.search3_engine.reset_tree()
        if torch is not None and torch.backends.mps.is_available():
            torch.mps.empty_cache()

    def clear_training_cache(self):
        for layer in self.layers.values():
            self._clear_layer_cache(layer)
        extra_layers = [
            self.policy_mid,
            self.value_mid,
            self.policy_act,
            self.value_act,
            self.policy_layer,
            self.value_layer,
            self.losslayer,
            self.losslayer2,
            self.losslayer3,
            self.losslayer4,
            self.search3_value_sigmoid,
        ]
        if self.Batch_Normalize:
            extra_layers += [self.policy_BN,self.value_BN]
        for layer in extra_layers:
            self._clear_layer_cache(layer)
        gc.collect()

    def _clear_layer_cache(self, layer):
        for attr_name in ['x','out','y','t','x_bar','train_m','train_s']:
            if hasattr(layer,attr_name):
                setattr(layer,attr_name,None)

            
        
    def predict(self,x,policy = True,value = False,loss = False):
        trunk_out = self._forward_trunk(x, loss = loss)

        if policy and not value:
            return self._predict_policy_head(trunk_out, loss = loss)

        if value and not policy:
            return self._predict_value_head(trunk_out, loss = loss)

        policy_out = self._predict_policy_head(trunk_out, loss = loss)
        value_out = self._predict_value_head(trunk_out, loss = loss)
        return np.r_[policy_out, value_out]

    def _forward_trunk(self, x, loss = False):
        """共有 trunk を順伝播して中間表現を返す。"""
        out = x.copy()
        for key in self.layers.keys():
            if loss and key[:2] == 'BN':
                out = self.layers[key].forward(out,True)
            else:
                out = self.layers[key].forward(out)
        return out

    def _predict_policy_head(self, trunk_out, loss = False):
        """policy head を順伝播して policy 出力を返す。"""
        out = self.policy_mid.forward(trunk_out)
        if self.Batch_Normalize:
            out = self.policy_BN.forward(out,loss)
        out = self.policy_act.forward(out)
        return self.policy_layer.forward(out)

    def _predict_value_head(self, trunk_out, loss = False):
        """value head を順伝播して value 出力を返す。"""
        out = self.value_mid.forward(trunk_out)
        if self.Batch_Normalize:
            out = self.value_BN.forward(out,loss)
        out = self.value_act.forward(out)
        return self.value_layer.forward(out)

    def grad(self,x,layer = "WO_V",index = 0):
        self.predict(x,policy = True,value = True,loss = False)

        if layer == "WO_V":
            dO = self._grad_from_value_head(x.shape[1])

        elif layer == "WO_P":
            dO = self._grad_from_policy_head(x.shape[1],index)

        else:
            dO = self._grad_from_hidden_layer(layer,index)
                

        return dO

    def _grad_from_value_head(self, batch_size):
        """value head 出力から trunk 入力まで勾配を戻す。"""
        dO = np.ones((1,batch_size),dtype = 'f')
        dO = self.value_layer.backward(dO)
        dO = self.value_act.backward(dO)
        dO = self.value_mid.backward(dO)
        return self._backprop_through_trunk_layers(dO)

    def _grad_from_policy_head(self, batch_size, index):
        """policy head の指定 index から trunk 入力まで勾配を戻す。"""
        dO = np.zeros((self.ops,batch_size),dtype = "f")
        dO[index] = 1
        dO = self.policy_layer.backward(dO)
        dO = self.policy_act.backward(dO)
        dO = self.policy_mid.backward(dO)
        return self._backprop_through_trunk_layers(dO)

    def _grad_from_hidden_layer(self, layer, index):
        """指定した trunk layer の出力から入力側へ勾配を戻す。"""
        reverse_key = list(self.layers)
        reverse_key.reverse()
        backward = False
        for key in reverse_key:
            if key == layer:
                dO = np.zeros(self.layers[key].out.shape,dtype = 'f')
                dO[index] = 1
                backward = True

            if backward:
                dO = self.layers[key].backward(dO)
        return dO

    def _backprop_through_trunk_layers(self, dO):
        """共有 trunk layer 群を逆順に backward する。"""
        reverse_key = list(self.layers)
        reverse_key.reverse()
        for key in reverse_key:
            dO = self.layers[key].backward(dO)
        return dO
        
    def integrated_grad(self,x,steps = 200,layer = "WO_V",index = 0):
        interpolated_inputs = self._integrated_grad_inputs(x,steps)
        gradients = self.grad(interpolated_inputs,layer = layer,index = index)
        return np.average(gradients,axis = 1)

    def _integrated_grad_inputs(self, x, steps):
        """完全状態と入力状態の間を結ぶ補間入力列を作る。"""
        interpolated_inputs = np.zeros((self.ips,steps),dtype = 'f')
        for i in range(steps):
            interpolated_inputs[:,i] = i / steps * self.cube.perfect_data + (1 - i / steps) * x
        return interpolated_inputs

    

    def loss(self,d_Lis,transformation = 0,flip_inside = False):
        loss_inputs = self._build_loss_inputs(
            d_Lis,
            transformation = transformation,
            flip_inside = flip_inside,
        )
        out = self._predict_loss_outputs(loss_inputs['x'])
        return self._compute_search2_losses(out,loss_inputs['args'],loss_inputs['indices'])

    def _build_loss_inputs(self, d_lis, transformation = 0, flip_inside = False):
        """Search2 学習用の入力テンソルと index 情報を構築する。"""
        indices, total_steps = self._build_loss_indices(d_lis)
        args = np.zeros(total_steps - len(d_lis),dtype = 'i')
        x = np.zeros((self.ips,total_steps))
        self._fill_loss_tensors(d_lis, transformation, flip_inside, args, x)
        return {'indices': indices, 'args': args, 'x': x}

    def _predict_loss_outputs(self, x):
        """loss 計算用に policy/value 出力をまとめて推論する。"""
        return self.predict(x,policy = True,value = True,loss = True)

    def _compute_search2_losses(self, out, args, indices):
        """Search2 用の policy loss と value loss を計算する。"""
        policy_loss = self.losslayer.forward(out[:-1],args,np.zeros(0),indices)
        value_loss = self.losslayer2.forward(out[-1:],indices)
        return (policy_loss,value_loss)

    def _build_loss_indices(self, d_Lis):
        """Search2 loss 用に各サンプルの区切り index を作る。"""
        Indices = [0]
        N = 0
        for d in d_Lis:
            N += len(d.moves) + 1
            Indices.append(N)
        return Indices, N

    def _fill_loss_tensors(self, d_Lis, transformation, flip_inside, args, x):
        """Search2 学習データ列をまとめて入力 tensor に展開する。"""
        arg_index = 0
        state_index = 0
        for data_item in d_Lis:
            arg_index, state_index = self._append_loss_item_tensors(
                data_item,
                transformation,
                flip_inside,
                args,
                x,
                arg_index,
                state_index,
            )

    def _append_loss_item_tensors(
        self,
        data_item,
        transformation,
        flip_inside,
        args,
        x,
        arg_index,
        state_index,
    ):
        """Search2 データ 1 件分の入力 tensor を追記する。"""
        scramble, moves = self._transform_loss_moves(data_item, transformation, flip_inside)
        self._apply_scramble_for_loss(scramble)
        self._write_loss_move_args(moves,args,arg_index)
        x[:,state_index] = self.cube.makedata()
        next_state_index = self._apply_moves_and_collect(moves, x, state_index)
        return arg_index + len(moves), next_state_index

    def _write_loss_move_args(self, moves, args, start_index):
        """Search2 の move 列を policy 教師ラベル列へ書き込む。"""
        args[start_index:start_index + len(moves)] = np.array(
            [self.cube.key_to_num[m] for m in moves]
        )

    def _transform_loss_moves(self, d, transformation, flip_inside):
        """Search2 データ 1 件分の scramble / move を対称変換する。"""
        scramble = self.cube.transform(d.scramble,transformation,flip_inside)
        moves = self.cube.transform(d.moves,transformation,flip_inside)
        return scramble, moves

    def _apply_scramble_for_loss(self, scramble):
        """loss 計算前に cube を指定 scramble 状態へ戻す。"""
        self.cube.reset()
        self.cube.scramble(0,scramble)

    def _apply_moves_and_collect(self, moves, x, start_index):
        """move を順に適用しながら途中局面の特徴量を追記する。"""
        i = 1
        for m in moves:
            self.cube.make_move(m)
            x[:,start_index + i] = self.cube.makedata()
            i += 1
        return start_index + len(moves) + 1

    def learn(self,transformation = 0,flip_inside = False, progress_callback = None):
        training_result = self._run_training_epochs(
            indices = self.indices,
            data_source = self.datas,
            train_batch = self._train_batch,
            transformation = transformation,
            flip_inside = flip_inside,
            progress_callback = progress_callback,
        )
        err, err2, new_indices, original_len, epoch_num, l1_max = training_result

        self.indices = new_indices
        self.set_perfect_val()
        if original_len > 0:
            self.lr_C = min(1,err/original_len/10)

        if epoch_num == 0:
            return (0,0,0,0,0)

        self._finalize_training(progress_callback = progress_callback)
        return (err / epoch_num,err2 / epoch_num,len(self.indices),original_len)

    def loss_search3(self,d_Lis,transformation = 0,flip_inside = False):
        search3_inputs = self._build_search3_loss_inputs(
            d_Lis,
            transformation = transformation,
            flip_inside = flip_inside,
        )
        out = self._predict_loss_outputs(search3_inputs['x'])
        return self._compute_search3_losses(
            out,
            search3_inputs['policy_targets'],
            search3_inputs['value_targets'],
            search3_inputs['sample_weights'],
        )

    def _build_search3_loss_inputs(self, d_lis, transformation = 0, flip_inside = False):
        """Search3 学習用の入力テンソル群を構築する。"""
        x, policy_targets, value_targets, sample_weights = self._build_search3_tensors(
            d_lis,
            transformation = transformation,
            flip_inside = flip_inside,
        )
        return {
            'x': x,
            'policy_targets': policy_targets,
            'value_targets': value_targets,
            'sample_weights': sample_weights,
        }

    def _compute_search3_losses(self, out, policy_targets, value_targets, sample_weights):
        """Search3 用の policy loss と value loss を計算する。"""
        policy_loss = self.losslayer4.forward(out[:-1],policy_targets,sample_weights)
        value_predictions = self.search3_value_sigmoid.forward(out[-1:])
        value_loss = self.losslayer3.forward(value_predictions,value_targets,sample_weights)
        return (policy_loss,value_loss)

    def _build_search3_tensors(self, d_Lis, transformation = 0, flip_inside = False):
        """Search3 学習用の state / policy / value tensor をまとめて作る。"""
        total_steps = self._search3_total_steps(d_Lis)
        x = np.zeros((self.ips,total_steps),dtype = 'f')
        policy_targets = np.zeros((self.ops,total_steps),dtype = 'f')
        value_targets = np.zeros((1,total_steps),dtype = 'f')
        sample_weights = np.ones((1,total_steps),dtype = 'f')
        step_index = 0

        for data_item in d_Lis:
            step_index = self._append_search3_item_tensors(
                data_item,
                x,
                policy_targets,
                value_targets,
                sample_weights,
                step_index,
                transformation = transformation,
                flip_inside = flip_inside,
            )

        return x, policy_targets, value_targets, sample_weights

    def _append_search3_item_tensors(
        self,
        data_item,
        x,
        policy_targets,
        value_targets,
        sample_weights,
        step_index,
        transformation = 0,
        flip_inside = False,
    ):
        """1 件分の Search3 学習データをテンソルへ追記する。"""
        scramble, moves = self._transform_search3_item(data_item,transformation,flip_inside)
        if len(moves) == 0:
            return step_index

        rewards = self._search3_rewards_array(data_item)
        self._reset_cube_to_search3_scramble(scramble)

        for move_index, move_label in enumerate(moves):
            self._write_search3_step_tensors(
                data_item,
                moves,
                rewards,
                move_index,
                x,
                policy_targets,
                value_targets,
                sample_weights,
                step_index,
                transformation = transformation,
                flip_inside = flip_inside,
            )
            self.cube.make_move(move_label)
            step_index += 1

        return step_index

    def _transform_search3_item(self, data_item, transformation, flip_inside):
        """Search3 データ 1 件分の scramble と move を対称変換する。"""
        scramble = self.cube.transform(data_item.scramble,transformation,flip_inside)
        moves = self.cube.transform(data_item.moves,transformation,flip_inside)
        return scramble, moves

    def _search3_rewards_array(self, data_item):
        """Search3 value target 計算に使う rewards 配列を整形する。"""
        return np.array(data_item.rewards,dtype = 'f').reshape(-1)

    def _reset_cube_to_search3_scramble(self, scramble):
        """Search3 学習データの開始局面へ cube を戻す。"""
        self.cube.reset()
        self.cube.scramble(0,scramble)

    def _write_search3_step_tensors(
        self,
        data_item,
        moves,
        rewards,
        move_index,
        x,
        policy_targets,
        value_targets,
        sample_weights,
        step_index,
        transformation = 0,
        flip_inside = False,
    ):
        """Search3 の 1 手分の特徴量と target を書き込む。"""
        x[:,step_index] = self.cube.makedata()
        policy_targets[:,step_index] = self._search3_policy_target(
            data_item,
            moves,
            move_index,
            transformation,
            flip_inside,
        )
        value_targets[0,step_index] = self._search3_value_target(
            data_item,
            rewards,
            move_index,
            len(moves),
        )
        sample_weights[0,step_index] = self._search3_step_weight(data_item,move_index)

    def _search3_total_steps(self, d_Lis):
        """Search3 データ全体で必要な step 数を数える。"""
        total_steps = 0
        for data_item in d_Lis:
            total_steps += len(data_item.moves)
        return total_steps

    def _normalize_search3_policy_target(self, policy_target):
        """policy target を確率分布に正規化する。"""
        if policy_target is None:
            return self._uniform_search3_policy_target()
        normalized_target = np.array(policy_target,dtype = 'f').reshape(-1)
        total = np.sum(normalized_target)
        if total <= 0:
            return self._uniform_search3_policy_target()
        return normalized_target / total

    def _uniform_search3_policy_target(self):
        """Search3 の policy target が無いときの一様分布を返す。"""
        return np.ones(self.ops,dtype = 'f') / self.ops

    def _search3_policy_target(self, data_item, moves, move_index, transformation, flip_inside):
        if self._use_soft_search3_policy_target(
            data_item,
            move_index,
            transformation,
            flip_inside,
        ):
            return self._transform_search3_policy_target(
                data_item.policy_target,
                transformation,
                flip_inside,
            )
        return self._one_hot_search3_policy(moves[move_index])

    def _use_soft_search3_policy_target(self, data_item, move_index, transformation, flip_inside):
        """soft target をそのまま使う条件か判定する。"""
        return (
            data_item.search_mode == 'search3'
            and move_index == 0
            and data_item.policy_target is not None
        )

    def _transform_search3_policy_target(self, policy_target, transformation, flip_inside):
        """対称変換後の move 空間に合わせて soft policy target を並べ替える。"""
        normalized_target = self._normalize_search3_policy_target(policy_target)
        if transformation == 0 and not flip_inside:
            return normalized_target

        transformed_target = np.zeros_like(normalized_target)
        move_index_map = self._search3_policy_move_index_map(transformation,flip_inside)
        for original_index, transformed_index in move_index_map.items():
            transformed_target[transformed_index] = normalized_target[original_index]
        return transformed_target

    def _search3_policy_move_index_map(self, transformation, flip_inside):
        """move index を対称変換後の index へ写す対応表を返す。"""
        cache_key = (transformation, bool(flip_inside))
        if cache_key in self._search3_policy_transform_cache:
            return self._search3_policy_transform_cache[cache_key]

        move_index_map = {}
        for move_label in self.cube.move_keys:
            transformed_move = self.cube.transform((move_label,),transformation,flip_inside)
            transformed_label = transformed_move[0]
            move_index_map[self.cube.key_to_num[move_label]] = self.cube.key_to_num[transformed_label]

        self._search3_policy_transform_cache[cache_key] = move_index_map
        return move_index_map

    def _one_hot_search3_policy(self, move_label):
        """指定手を one-hot の policy target に変換する。"""
        policy_target = np.zeros((self.ops,),dtype = 'f')
        policy_target[self.cube.key_to_num[move_label]] = 1.0
        return policy_target

    def _search3_value_target(self, data_item, rewards, move_index, move_count):
        explicit_target = self._explicit_search3_value_target(data_item,move_index)
        if explicit_target is not None:
            return explicit_target
        return self._fallback_search3_value_target(data_item,rewards,move_index,move_count)

    def _explicit_search3_value_target(self, data_item, move_index):
        """data_item に value_targets があればそこから target を取る。"""
        value_targets = getattr(data_item,'value_targets',None)
        if value_targets is None:
            return None
        normalized_targets = np.array(value_targets,dtype = 'f').reshape(-1)
        if move_index < normalized_targets.size:
            return normalized_targets[move_index]
        if normalized_targets.size > 0:
            return normalized_targets[-1]
        return None

    def _fallback_search3_value_target(self, data_item, rewards, move_index, move_count):
        """value_targets が無い場合の reward/value_trace/gamma fallback を返す。"""
        reward_target = self._reward_based_search3_value_target(rewards,move_index)
        if reward_target is not None:
            return reward_target

        bootstrap_target = self._bootstrap_search3_value_target(data_item)
        if bootstrap_target is not None:
            return bootstrap_target

        return self._discounted_search3_value_target(move_count,move_index)

    def _reward_based_search3_value_target(self, rewards, move_index):
        """reward 列があれば、その step に対応する target を返す。"""
        if move_index < rewards.size:
            return rewards[move_index]
        if rewards.size > 0:
            return rewards[-1]
        return None

    def _bootstrap_search3_value_target(self, data_item):
        """value_trace から bootstrap 用 target を取り出す。"""
        if len(data_item.value_trace) > 0:
            return data_item.value_trace[-1]
        return None

    def _discounted_search3_value_target(self, move_count, move_index):
        """明示 target が無い場合の gamma fallback を返す。"""
        return self.value_target_gamma ** (move_count - move_index - 1)

    def _search3_step_weight(self, data_item, move_index):
        """Search3 学習の 1 手分 sample weight を返す。"""
        sample_weight = getattr(data_item,'sample_weight',1.0)
        if data_item.search_mode == 'search3' and move_index > 0:
            return sample_weight * 0.7
        return sample_weight

    def learn_search3(self,transformation = 0,flip_inside = False, progress_callback = None):
        training_result = self._run_training_epochs(
            indices = self.indices_search3,
            data_source = self.datas_search3,
            train_batch = self._train_batch_search3,
            transformation = transformation,
            flip_inside = flip_inside,
            progress_callback = progress_callback,
        )
        err, err2, new_indices, original_len, epoch_num, l1_max = training_result

        self.indices_search3 = new_indices
        if epoch_num == 0:
            return (0,0,0,0)

        self.set_perfect_val()
        if original_len > 0:
            self.lr_C = min(1,err/original_len/10)

        self._finalize_training(progress_callback = progress_callback)
        return (err / epoch_num,err2 / epoch_num,len(self.indices_search3),original_len,l1_max)

    def _run_training_epochs(self, indices, data_source, train_batch, transformation, flip_inside, progress_callback = None):
        """index 列を batch 学習して、残す index と誤差集計を返す。"""
        batch_size = 100
        epoch_state = self._init_training_epoch_state(indices,batch_size)

        for epoch_index, batch_indices in self._iter_training_batches(epoch_state['indices'],batch_size,epoch_state['epoch_num']):
            if epoch_index % 20 == 0:
                self._report_training_progress(progress_callback, epoch_index // 20)
            batch_data = [data_source[n] for n in batch_indices]
            losses, epoch_state = train_batch(
                batch_data,
                batch_indices,
                transformation,
                flip_inside,
                epoch_state,
            )
            epoch_state['err'] += losses[0]
            epoch_state['err2'] += losses[1]
            if self._should_keep_training_batch(losses):
                epoch_state['new_indices'] += batch_indices

        epoch_state['new_indices'] += epoch_state['indices'][batch_size * epoch_state['epoch_num']:]
        return (
            epoch_state['err'],
            epoch_state['err2'],
            epoch_state['new_indices'],
            epoch_state['original_len'],
            epoch_state['epoch_num'],
            epoch_state['l1_max'],
        )

    def _report_training_progress(self, progress_callback, block_index):
        """学習進捗を callback 経由で通知する。"""
        if progress_callback is not None:
            progress_callback(f'epoch-block {block_index}')

    def _init_training_epoch_state(self, indices, batch_size):
        """学習 epoch の集計用状態を初期化する。"""
        shuffled_indices = list(indices)
        random.shuffle(shuffled_indices)
        return {
            'indices': shuffled_indices,
            'original_len': len(shuffled_indices),
            'epoch_num': len(shuffled_indices) // batch_size,
            'err': 0.0,
            'err2': 0.0,
            'new_indices': [],
            'l0_max': 0.0,
            'l1_max': 0.0,
            'l1_indices': [],
        }

    def _iter_training_batches(self, indices, batch_size, epoch_num):
        """学習対象 index を batch 単位で順に返す。"""
        for epoch_index in range(epoch_num):
            start = epoch_index * batch_size
            end = (epoch_index + 1) * batch_size
            yield epoch_index, indices[start:end]

    def _should_keep_training_batch(self, losses):
        """誤差が大きい batch を次 epoch に残すか判定する。"""
        return losses[0] > 1.0 or losses[1] > 0.01

    def _finalize_training(self, progress_callback = None):
        """学習後の BN 更新、ログ出力、cache 破棄をまとめて行う。"""
        if self.Batch_Normalize:
            self._refresh_bn_stats()
        self._log_weight_stats(progress_callback = progress_callback)
        self.mark_params_dirty()
        self.clear_training_cache()

    def _train_batch_search3(self, d_lis, batch_indices, transformation, flip_inside, epoch_state):
        L = self.loss_search3(d_lis,transformation = transformation,flip_inside = flip_inside)
        L0 = L[0] / len(d_lis)
        L1 = L[1] / len(d_lis)
        epoch_state = self._update_training_maxima(L0,L1,batch_indices,epoch_state)

        dO = self._backprop_policy_search3()
        dO2 = self._backprop_value_search3()
        dO += dO2
        self._backprop_trunk(dO)
        self._update_output_momentum()
        self._update_affine_momentum()
        self._update_bn_momentum()
        self._apply_param_updates()
        return (L0,L1), epoch_state

    def _train_batch(self, d_lis, batch_indices, transformation, flip_inside, epoch_state):
        L = self.loss(d_lis,transformation = transformation,flip_inside = flip_inside)
        L0 = L[0] / len(d_lis)
        L1 = L[1] / len(d_lis)
        epoch_state = self._update_training_maxima(L0,L1,batch_indices,epoch_state)

        dO = self._backprop_policy()
        dO2 = self._backprop_value()
        dO += dO2
        self._backprop_trunk(dO)
        self._update_output_momentum()
        self._update_affine_momentum()
        self._update_bn_momentum()
        self._apply_param_updates()
        return (L0,L1), epoch_state

    def _update_training_maxima(self, l0, l1, batch_indices, epoch_state):
        """最大損失 batch の記録を更新する。"""
        if l0 > epoch_state['l0_max']:
            epoch_state['l0_max'] = l0
        if l1 > epoch_state['l1_max']:
            epoch_state['l1_max'] = l1
            epoch_state['l1_indices'] = batch_indices.copy()
        return epoch_state

    def _backprop_policy(self):
        dO = self.losslayer.backward()
        dO = self.policy_layer.backward(dO)
        dO = self.policy_act.backward(dO)
        if self.Batch_Normalize:
            dO = self.policy_BN.backward(dO)
        dO = self.policy_mid.backward(dO)
        return dO

    def _backprop_value(self):
        dO2 = self.losslayer2.backward() * self.PV_ratio
        dO2 = self.value_layer.backward(dO2)
        dO2 = self.value_act.backward(dO2)
        if self.Batch_Normalize:
            dO2 = self.value_BN.backward(dO2)
        dO2 = self.value_mid.backward(dO2)
        return dO2

    def _backprop_policy_search3(self):
        dO = self.losslayer4.backward()
        dO = self.policy_layer.backward(dO)
        dO = self.policy_act.backward(dO)
        if self.Batch_Normalize:
            dO = self.policy_BN.backward(dO)
        dO = self.policy_mid.backward(dO)
        return dO

    def _backprop_value_search3(self):
        dO2 = self.losslayer3.backward() * self.PV_ratio
        dO2 = self.search3_value_sigmoid.backward(dO2)
        dO2 = self.value_layer.backward(dO2)
        dO2 = self.value_act.backward(dO2)
        if self.Batch_Normalize:
            dO2 = self.value_BN.backward(dO2)
        dO2 = self.value_mid.backward(dO2)
        return dO2

    def _backprop_trunk(self, dO):
        reverse_key = list(self.layers)
        reverse_key.reverse()
        for key in reverse_key:
            dO = self.layers[key].backward(dO)

    def _update_output_momentum(self):
        self._accumulate_affine_optimizer_state(self.policy_layer,'WO_P','BO_P')
        self._accumulate_affine_optimizer_state(self.value_layer,'WO_V','BO_V',update_bias = False)
        self._accumulate_affine_optimizer_state(self.policy_mid,'WM_P','BM_P')
        self._accumulate_affine_optimizer_state(self.value_mid,'WM_V','BM_V')

        if self.Batch_Normalize:
            self._accumulate_bn_optimizer_state(self.policy_BN,'BNgP','BNbP')
            self._accumulate_bn_optimizer_state(self.value_BN,'BNgV','BNbV')

    def _update_affine_momentum(self):
        if self.weight_decay:
            self._apply_weight_decay('WO_P')
            self._apply_weight_decay('WO_V')
            self._apply_weight_decay('WM_P')
        
        for key in self.affines:
            if self.weight_decay:
                self._apply_weight_decay('W' + key[-1])
            self._accumulate_affine_optimizer_state(
                self.layers[key],
                'W' + key[-1],
                'B' + key[-1],
            )

    def _update_bn_momentum(self):
        for key in self.BNs:
            self._accumulate_bn_optimizer_state(
                self.layers[key],
                'BNg' + key[-1],
                'BNb' + key[-1],
            )

    def _apply_param_updates(self):
        for key in self.v.keys():
            self.params[key] -= self._optimizer_step(key)
            self.v[key] *= self.lr_v
            self.h[key] *= self.lr_h

    def _accumulate_affine_optimizer_state(self, layer, weight_key, bias_key, update_bias = True):
        """Affine layer の勾配を optimizer 状態へ加算する。"""
        self._accumulate_weight_optimizer_state(weight_key,layer.dW)
        if update_bias:
            self._accumulate_weight_optimizer_state(bias_key,layer.dB)

    def _accumulate_bn_optimizer_state(self, layer, gamma_key, beta_key):
        """BatchNorm layer の勾配を optimizer 状態へ加算する。"""
        self._accumulate_weight_optimizer_state(gamma_key,layer.dg)
        self._accumulate_weight_optimizer_state(beta_key,layer.db)

    def _accumulate_weight_optimizer_state(self, key, grad):
        """1 パラメータ分の一次/二次モーメントを更新する。"""
        self.v[key] += self.lr * grad
        self.h[key] += grad ** 2

    def _apply_weight_decay(self, key):
        """対象 weight に weight decay を適用する。"""
        self.params[key] -= self.wdlr * self.params[key]

    def _optimizer_step(self, key):
        """現在の optimizer 設定に応じた 1 step 分の更新量を返す。"""
        if self.adam:
            return self.v[key] / (np.sqrt(self.h[key]) + 1)
        return self.v[key]

    def _refresh_bn_stats(self):
        for key in self.BNs:
            self.layers[key].set_ms()
        self.policy_BN.set_ms()
        self.value_BN.set_ms()

    def _log_weight_stats(self, progress_callback = None):
        for key in self.v.keys():
            if key[0] == "W":
                if self.adam:
                    message = (
                        key + ":" + str(np.log10(np.average(self.v[key] ** 2 / (self.h[key] + 1))))
                        + ", " + str(np.max(self.h[key]))
                    )
                else:
                    message = (
                        key + ":" + str(np.log10(np.average(self.v[key] ** 2)))
                        + ", " + str(np.max(self.h[key]))
                    )
                self._report_training_progress(progress_callback, message)
        

    def search2(self,N):
        return self.search2_engine.search2(N)
    
    def search3(self,N):
        return self.search3_engine.search3(N,C = self.search3_C)

    def search(self, progress_callback = None):
        if self.search_mode == 'search2':
            result = self.search2(self.search_num2)
            if progress_callback is not None:
                progress_callback(result)
            return result
        elif self.search_mode == 'search3':
            return self._search3_with_repeats(progress_callback = progress_callback)
        else:
            raise ValueError(self.search_mode)

    def _search3_with_repeats(self, progress_callback = None):
        last_result = None
        attempt_results = []
        for attempt_index in range(self.search_repeat3):
            last_result = self.search3(self.search_num3)
            last_result.attempt_index = attempt_index + 1
            attempt_results.append(last_result)
            if progress_callback is not None:
                progress_callback(last_result)
            if last_result.end_reason == 'solved':
                last_result.attempt_results = attempt_results
                return last_result
        if last_result is not None:
            last_result.attempt_results = attempt_results
        return last_result

    def _predict_search2(self, X):
        if torch is None or self.Batch_Normalize:
            return self.predict(X,policy = True,value = True)
        return self._torch_predict(X)

    def _torch_predict(self, X):
        device = self._torch_device()
        params = self._torch_params_from_numpy(device)
        with torch.no_grad():
            X_t = torch.as_tensor(X, dtype = torch.float32, device = device)
            out = self._torch_forward_policy_value(X_t, params)
        return out.cpu().numpy()

    def _torch_device(self):
        if hasattr(self, "_torch_device_cache"):
            return self._torch_device_cache
        device_name = "mps" if torch.backends.mps.is_available() else "cpu"
        self._torch_device_cache = torch.device(device_name)
        return self._torch_device_cache

    def _torch_params_from_numpy(self, device):
        if self._torch_params_cache is not None and not self._torch_params_dirty and self._torch_params_device == device:
            return self._torch_params_cache
        params = {
            key: torch.as_tensor(value, dtype = torch.float32, device = device)
            for key, value in self.params.items()
        }
        self._torch_params_cache = params
        self._torch_params_device = device
        self._torch_params_dirty = False
        return params

    def _torch_forward_policy_value(self, X, params):
        out = X
        for i in range(1, len(self.Mid) + 1):
            W = params['W' + str(i)]
            B = params['B' + str(i)]
            out = W @ out + B.unsqueeze(1)
            out = F_torch.relu(out)

        p = self._torch_forward_head(out, params, mid_key = 'WM_P', mid_bias_key = 'BM_P', out_key = 'WO_P', out_bias_key = 'BO_P')
        v = self._torch_forward_head(out, params, mid_key = 'WM_V', mid_bias_key = 'BM_V', out_key = 'WO_V', out_bias_key = 'BO_V')

        return torch.cat([p, v], dim = 0)

    def _torch_forward_head(self, trunk_out, params, mid_key, mid_bias_key, out_key, out_bias_key):
        """policy/value head を 1 本分だけ順伝播する。"""
        head_out = params[mid_key] @ trunk_out + params[mid_bias_key].unsqueeze(1)
        head_out = self._torch_head_act(head_out)
        return params[out_key] @ head_out + params[out_bias_key].unsqueeze(1)

    def _torch_head_act(self, x):
        if self.activation == 'ReLU':
            return F_torch.relu(x)
        elif self.activation == 'Hard_Sigmoid':
            return F_torch.hardsigmoid(x)
        else:
            return torch.sigmoid(x)
