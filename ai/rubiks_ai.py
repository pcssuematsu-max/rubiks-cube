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
        self.value_target_gamma = 0.95
        




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
        self.search_batch3 = 100
        self.search3_C = 0.05
        self.perfect_val = 1.0
        self._torch_params_cache = None
        self._torch_params_dirty = True
        self._torch_params_device = None
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
        out = x.copy()
        for key in self.layers.keys():
            if loss and key[:2] == 'BN':
                out = self.layers[key].forward(out,True)
            else:
                out = self.layers[key].forward(out)

        out_m = out

        if policy and not value:
            out = self.policy_mid.forward(out_m)
            if self.Batch_Normalize:
                out = self.policy_BN.forward(out,loss)
            out = self.policy_act.forward(out)
            return self.policy_layer.forward(out)
        
        elif not policy and value:
            out = self.value_mid.forward(out_m)
            if self.Batch_Normalize:
                out = self.value_BN.forward(out,loss)
            out = self.value_act.forward(out)
            return self.value_layer.forward(out)
        else:
            out_p = self.policy_mid.forward(out_m)
            if self.Batch_Normalize:
                out_p = self.policy_BN.forward(out_p,loss)
            out_p = self.policy_act.forward(out_p)
            
            out_v = self.value_mid.forward(out_m)
            if self.Batch_Normalize:
                out_v = self.value_BN.forward(out_v,loss)
            out_v = self.value_act.forward(out_v)
            
            return np.r_[self.policy_layer.forward(out_p),self.value_layer.forward(out_v)]

    def grad(self,x,layer = "WO_V",index = 0):
        self.predict(x,policy = True,value = True,loss = False)

        if layer == "WO_V":
            dO = np.ones((1,x.shape[1]),dtype = 'f')
            dO = self.value_layer.backward(dO)
            dO = self.value_act.backward(dO)
            dO = self.value_mid.backward(dO)

            reverse_key = list(self.layers)
            reverse_key.reverse()
            for key in reverse_key:
                dO = self.layers[key].backward(dO)

        elif layer == "WO_P":
            dO = np.zeros((self.ops,x.shape[1]),dtype = "f")
            dO[index] = 1
            dO = self.policy_layer.backward(dO)
            dO = self.policy_act.backward(dO)
            dO = self.policy_mid.backward(dO)
            

            reverse_key = list(self.layers)
            reverse_key.reverse()
            for key in reverse_key:
                dO = self.layers[key].backward(dO)

        else:
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
        
    def integrated_grad(self,x,steps = 200,layer = "WO_V",index = 0):
        X = np.zeros((self.ips,steps),dtype = 'f')
        for i in range(steps):
            X[:,i] = i / steps * self.cube.perfect_data + (1 - i / steps) * x

        dO = self.grad(X,layer = layer,index = index)

        return np.average(dO,axis = 1)

    

    def loss(self,d_Lis,transformation = 0,flip_inside = False):
        Indices, total_steps = self._build_loss_indices(d_Lis)
        args = np.zeros(total_steps - len(d_Lis),dtype = 'i')
        x = np.zeros((self.ips,total_steps))
        self._fill_loss_tensors(d_Lis, transformation, flip_inside, args, x)
        out = self.predict(x,policy = True,value = True,loss = True)
        l = self.losslayer.forward(out[:-1],args,np.zeros(0),Indices)
        l2 = self.losslayer2.forward(out[-1:],Indices)
        return (l,l2)

    def _build_loss_indices(self, d_Lis):
        Indices = [0]
        N = 0
        for d in d_Lis:
            N += len(d.moves) + 1
            Indices.append(N)
        return Indices, N

    def _fill_loss_tensors(self, d_Lis, transformation, flip_inside, args, x):
        N_args = 0
        N_x = 0
        for d in d_Lis:
            scramble, moves = self._transform_loss_moves(d, transformation, flip_inside)
            self._apply_scramble_for_loss(scramble)
            args[N_args:N_args + len(moves)] = np.array([self.cube.key_to_num[m] for m in moves])
            x[:,N_x] = self.cube.makedata()
            N_x = self._apply_moves_and_collect(moves, x, N_x)
            N_args += len(moves)

    def _transform_loss_moves(self, d, transformation, flip_inside):
        scramble = self.cube.transform(d.scramble,transformation,flip_inside)
        moves = self.cube.transform(d.moves,transformation,flip_inside)
        return scramble, moves

    def _apply_scramble_for_loss(self, scramble):
        self.cube.reset()
        self.cube.scramble(0,scramble)

    def _apply_moves_and_collect(self, moves, x, start_index):
        i = 1
        for m in moves:
            self.cube.make_move(m)
            x[:,start_index + i] = self.cube.makedata()
            i += 1
        return start_index + len(moves) + 1

    def learn(self,transformation = 0,flip_inside = False):
        err = 0
        err2 = 0
        new_indices = []
        random.shuffle(self.indices)
        Len = len(self.indices)
        Batch_Size = 100
        Epoch_Num = Len // Batch_Size
        l0_max = 0.0
        l1_max = 0.0
        l1_indices = []

        for i in range(Epoch_Num):
            if i % 20 == 0:
                print(i // 20)
            batch_indices = self.indices[i*Batch_Size:(i+1)*Batch_Size]
            d_lis = [self.datas[n] for n in batch_indices]
            L0, L1, l0_max, l1_max, l1_indices = self._train_batch(d_lis, batch_indices, transformation, flip_inside, l0_max, l1_max, l1_indices)
            err += L0
            err2 += L1
            if L0 > 1.0 or L1 > 0.01:
                new_indices += batch_indices

        self.indices = new_indices + self.indices[Batch_Size * Epoch_Num:]
        self.set_perfect_val()
        self.lr_C = min(1,err/Len/10)

        if Epoch_Num == 0:
            return (0,0,0,0,0)

        if self.Batch_Normalize:
            self._refresh_bn_stats()

        self._log_weight_stats()
        self.mark_params_dirty()
        self.clear_training_cache()
        return (err / Epoch_Num,err2 / Epoch_Num,len(self.indices),Len)

    def loss_search3(self,d_Lis,transformation = 0,flip_inside = False):
        x, policy_targets, value_targets, sample_weights = self._build_search3_tensors(d_Lis,transformation = transformation,flip_inside = flip_inside)
        out = self.predict(x,policy = True,value = True,loss = True)
        l0 = self.losslayer4.forward(out[:-1],policy_targets,sample_weights)
        value_predictions = self.search3_value_sigmoid.forward(out[-1:])
        l1 = self.losslayer3.forward(value_predictions,value_targets,sample_weights)
        return (l0,l1)

    def _build_search3_tensors(self, d_Lis, transformation = 0, flip_inside = False):
        total_steps = self._search3_total_steps(d_Lis)
        x = np.zeros((self.ips,total_steps),dtype = 'f')
        policy_targets = np.zeros((self.ops,total_steps),dtype = 'f')
        value_targets = np.zeros((1,total_steps),dtype = 'f')
        sample_weights = np.ones((1,total_steps),dtype = 'f')
        step_index = 0

        for data_item in d_Lis:
            scramble = self.cube.transform(data_item.scramble,transformation,flip_inside)
            moves = self.cube.transform(data_item.moves,transformation,flip_inside)
            if len(moves) == 0:
                continue
            self.cube.reset()
            self.cube.scramble(0,scramble)
            rewards = np.array(data_item.rewards,dtype = 'f').reshape(-1)
            for move_index, move_label in enumerate(moves):
                x[:,step_index] = self.cube.makedata()
                policy_targets[:,step_index] = self._search3_policy_target(
                    data_item,
                    moves,
                    move_index,
                    transformation,
                    flip_inside,
                )
                value_targets[0,step_index] = self._search3_value_target(data_item,rewards,move_index,len(moves))
                sample_weights[0,step_index] = self._search3_step_weight(data_item,move_index)
                self.cube.make_move(move_label)
                step_index += 1

        return x, policy_targets, value_targets, sample_weights

    def _search3_total_steps(self, d_Lis):
        total_steps = 0
        for data_item in d_Lis:
            total_steps += len(data_item.moves)
        return total_steps

    def _normalize_search3_policy_target(self, policy_target):
        if policy_target is None:
            return np.ones(self.ops,dtype = 'f') / self.ops
        normalized_target = np.array(policy_target,dtype = 'f').reshape(-1)
        total = np.sum(normalized_target)
        if total <= 0:
            return np.ones(self.ops,dtype = 'f') / self.ops
        return normalized_target / total

    def _search3_policy_target(self, data_item, moves, move_index, transformation, flip_inside):
        use_soft_target = (
            data_item.search_mode == 'search3'
            and move_index == 0
            and data_item.policy_target is not None
            and transformation == 0
            and not flip_inside
        )
        if use_soft_target:
            return self._normalize_search3_policy_target(data_item.policy_target)
        return self._one_hot_search3_policy(moves[move_index])

    def _one_hot_search3_policy(self, move_label):
        policy_target = np.zeros((self.ops,),dtype = 'f')
        policy_target[self.cube.key_to_num[move_label]] = 1.0
        return policy_target

    def _search3_value_target(self, data_item, rewards, move_index, move_count):
        value_targets = getattr(data_item,'value_targets',None)
        if value_targets is not None:
            value_targets = np.array(value_targets,dtype = 'f').reshape(-1)
            if move_index < value_targets.size:
                return value_targets[move_index]
            if value_targets.size > 0:
                return value_targets[-1]
        if move_index < rewards.size:
            return rewards[move_index]
        if rewards.size > 0:
            return rewards[-1]
        if len(data_item.value_trace) > 0:
            return data_item.value_trace[-1]
        return self.value_target_gamma ** (move_count - move_index - 1)

    def _search3_step_weight(self, data_item, move_index):
        sample_weight = getattr(data_item,'sample_weight',1.0)
        if data_item.search_mode == 'search3' and move_index > 0:
            return sample_weight * 0.7
        return sample_weight

    def learn_search3(self,transformation = 0,flip_inside = False):
        err = 0
        err2 = 0
        new_indices = []
        random.shuffle(self.indices_search3)
        Len = len(self.indices_search3)
        Batch_Size = 100
        Epoch_Num = Len // Batch_Size
        l0_max = 0.0
        l1_max = 0.0
        l1_indices = []

        for i in range(Epoch_Num):
            if i % 20 == 0:
                print(i // 20)
            batch_indices = self.indices_search3[i*Batch_Size:(i+1)*Batch_Size]
            d_lis = [self.datas_search3[n] for n in batch_indices]
            L, l0_max, l1_max, l1_indices = self._train_batch_search3(d_lis, batch_indices, transformation, flip_inside, l0_max, l1_max, l1_indices)
            err += L[0]
            err2 += L[1]
            if L[0] > 1.0 or L[1] > 0.01:
                new_indices += batch_indices

        self.indices_search3 = new_indices + self.indices_search3[Batch_Size * Epoch_Num:]
        if Epoch_Num == 0:
            return (0,0,0,0)

        self.set_perfect_val()
        self.lr_C = min(1,err/Len/10)

        if self.Batch_Normalize:
            self._refresh_bn_stats()

        self._log_weight_stats()
        self.mark_params_dirty()
        self.clear_training_cache()
        return (err / Epoch_Num,err2 / Epoch_Num,len(self.indices_search3),Len,l1_max)

    def _train_batch_search3(self, d_lis, batch_indices, transformation, flip_inside, l0_max, l1_max, l1_indices):
        L = self.loss_search3(d_lis,transformation = transformation,flip_inside = flip_inside)
        L0 = L[0] / len(d_lis)
        L1 = L[1] / len(d_lis)
        if L0 > l0_max:
            l0_max = L0
        if L1 > l1_max:
            l1_max = L1
            l1_indices = batch_indices.copy()

        dO = self._backprop_policy_search3()
        dO2 = self._backprop_value_search3()
        dO += dO2
        self._backprop_trunk(dO)
        self._update_output_momentum()
        self._update_affine_momentum()
        self._update_bn_momentum()
        self._apply_param_updates()
        return (L0,L1), l0_max, l1_max, l1_indices

    def _train_batch(self, d_lis, batch_indices, transformation, flip_inside, l0_max, l1_max, l1_indices):
        L = self.loss(d_lis,transformation = transformation,flip_inside = flip_inside)
        L0 = L[0] / len(d_lis)
        L1 = L[1] / len(d_lis)
        if L0 > l0_max:
            l0_max = L0
        if L1 > l1_max:
            l1_max = L1
            l1_indices = batch_indices.copy()

        dO = self._backprop_policy()
        dO2 = self._backprop_value()
        dO += dO2
        self._backprop_trunk(dO)
        self._update_output_momentum()
        self._update_affine_momentum()
        self._update_bn_momentum()
        self._apply_param_updates()
        return L0, L1, l0_max, l1_max, l1_indices

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
        self.v['WO_P'] += self.lr * self.policy_layer.dW
        self.v['BO_P'] += self.lr * self.policy_layer.dB
        self.v['WO_V'] += self.lr * self.value_layer.dW

        self.v['WM_P'] += self.lr * self.policy_mid.dW
        self.v['WM_V'] += self.lr * self.value_mid.dW
        self.v['BM_P'] += self.lr * self.policy_mid.dB
        self.v['BM_V'] += self.lr * self.value_mid.dB

        self.h['WO_P'] += self.policy_layer.dW ** 2
        self.h['BO_P'] += self.policy_layer.dB ** 2
        self.h['WO_V'] += self.value_layer.dW ** 2

        self.h['WM_P'] += self.policy_mid.dW ** 2
        self.h['BM_P'] += self.policy_mid.dB ** 2
        self.h['WM_V'] += self.value_mid.dW ** 2
        self.h['BM_V'] += self.value_mid.dB ** 2

        if self.Batch_Normalize:
            self.v['BNgP'] += self.lr * self.policy_BN.dg
            self.v['BNbP'] += self.lr * self.policy_BN.db
            self.v['BNgV'] += self.lr * self.value_BN.dg
            self.v['BNbV'] += self.lr * self.value_BN.db

    def _update_affine_momentum(self):
        if self.weight_decay:
            self.params['WO_P'] -= self.wdlr * self.params['WO_P']
            self.params['WO_V'] -= self.wdlr * self.params['WO_V']
            self.params['WM_P'] -= self.wdlr * self.params['WM_P']
        
        for key in self.affines:
            if self.weight_decay:
                self.params['W' + key[-1]] -= self.wdlr * self.params['W' + key[-1]]
                

            self.v['W' + key[-1]] += self.lr * self.layers[key].dW
            self.v['B' + key[-1]] += self.lr * self.layers[key].dB

            self.h['W' + key[-1]] += self.layers[key].dW ** 2
            self.h['B' + key[-1]] += self.layers[key].dB ** 2

    def _update_bn_momentum(self):
        for key in self.BNs:
            self.v['BNg' + key[-1]] += self.lr * self.layers[key].dg
            self.v['BNb' + key[-1]] += self.lr * self.layers[key].db

    def _apply_param_updates(self):
        for key in self.v.keys():
            if self.adam:
                self.params[key] -= self.v[key] / (np.sqrt(self.h[key]) + 1)
            else:
                self.params[key] -= self.v[key]
            self.v[key] *= self.lr_v
            self.h[key] *= self.lr_h

    def _refresh_bn_stats(self):
        for key in self.BNs:
            self.layers[key].set_ms()
        self.policy_BN.set_ms()
        self.value_BN.set_ms()

    def _log_weight_stats(self):
        for key in self.v.keys():
            if key[0] == "W":
                if self.adam:
                    print(key + ":" + str(np.log10(np.average(self.v[key] ** 2 / (self.h[key] + 1)))) + ",",str(np.max(self.h[key])))
                else:
                    print(key + ":" + str(np.log10(np.average(self.v[key] ** 2))) + ",",str(np.max(self.h[key])))
        

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
        if torch.backends.mps.is_available():
            self._torch_device_cache = torch.device("mps")
        else:
            self._torch_device_cache = torch.device("cpu")
        return self._torch_device_cache

    def _torch_params_from_numpy(self, device):
        if self._torch_params_cache is not None and not self._torch_params_dirty and self._torch_params_device == device:
            return self._torch_params_cache
        params = {}
        for key in self.params.keys():
            params[key] = torch.as_tensor(self.params[key], dtype = torch.float32, device = device)
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

        p = params['WM_P'] @ out + params['BM_P'].unsqueeze(1)
        p = self._torch_head_act(p)
        p = params['WO_P'] @ p + params['BO_P'].unsqueeze(1)

        v = params['WM_V'] @ out + params['BM_V'].unsqueeze(1)
        v = self._torch_head_act(v)
        v = params['WO_V'] @ v + params['BO_V'].unsqueeze(1)

        return torch.cat([p, v], dim = 0)

    def _torch_head_act(self, x):
        if self.activation == 'ReLU':
            return F_torch.relu(x)
        elif self.activation == 'Hard_Sigmoid':
            return F_torch.hardsigmoid(x)
        else:
            return torch.sigmoid(x)
