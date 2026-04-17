import sys
import os
import numpy as np
import random
try:
    import torch
    import torch.nn.functional as F_torch
except Exception:
    torch = None
    F_torch = None
from collections import OrderedDict,Counter
import math
import cProfile
import tkinter as Tk
from functools import reduce
import threading
import pickle
import gc

from heapdict import heapdict

np.set_printoptions(suppress=True)

inside_size = {2:50,3:36,4:26,5:22,6:17,7:14}
outside_size = {2:50,3:36,4:28,5:26,6:26,7:26}

perfect_val = 1.0e+8

R_Nums = {}
R_Nums[2] = np.array([[1,2],
                      [0,3]])

R_Nums[3] = np.array([[1,6,2],
                      [5,8,7],
                      [0,4,3]],dtype = 'i')

R_Nums[4] = np.array([[ 1,10, 6, 2],
                      [ 5,13,14,11],
                      [ 9,12,15, 7],
                      [ 0, 4, 8, 3]])

R_Nums[5] = np.array([[ 1,14, 6,10, 2],
                      [ 9,17,22,18,15],
                      [ 5,21,24,23, 7],
                      [13,16,20,19,11],
                      [ 0, 8, 4,12, 3]]
                      ,dtype = 'i')
R_Nums[6] = np.array([[ 1,10,18,14, 6, 2],
                      [ 5,21,30,26,22,11],
                      [13,25,33,34,31,19],
                      [17,29,32,35,27,15],
                      [ 9,20,24,28,23, 7],
                      [ 0, 4,12,16, 8, 3]])



R_Nums[7] = np.array([[ 1,14,22, 6,18,10, 2],
                      [ 9,25,38,30,34,26,15],
                      [17,33,41,46,42,39,23],
                      [ 5,29,45,48,47,31, 7],
                      [21,37,40,44,43,35,19],
                      [13,24,32,28,36,27,11],
                      [ 0, 8,16, 4,20,12, 3]],dtype = 'i')

edge_num = {}
edge_num[2] = []
edge_num[3] = ([(4,),(5,),(6,),(7,)])
edge_num[4] = [(8,4),(9,5),(10,6),(11,7)]
edge_num[5] = [(4,8,12),(5,9,13),(6,10,14),(7,11,15)]
edge_num[6] = [(4,8,12,16),(5,9,13,17),(6,10,14,18),(7,11,15,19)]
edge_num[7] = [(16,8,0,9,17),(18,10,2,11,19),(20,12,4,13,21),(22,14,6,15,23)]


AB = {}
AB[2] = []
AB[3] = [(1,1)]
AB[4] = [(1,2),(2,1)]
AB[5] = [(1,1),(2,3),(3,2)]
AB[6] = [(1,2),(2,1),(3,4),(4,3)]
AB[7] = [(1,1),(2,3),(3,2),(4,5),(5,4)]



Group_Nums = {}
Group_Nums[2] = {'A':list(range(4)),'B':[],'C':[],'c':[],'D':[],'d':[],'E':[],'e':[],'F':[],'f':[],'G':[]}
Group_Nums[3] = {'A':list(range(4)),'B':list(range(4,8)),'C':[],'c':[],'D':[],'d':[],'E':[],'e':[],'F':[],'f':[],'G':[8]}
Group_Nums[4] = {'A':list(range(4)),'B':[],'C':list(range(4,12)),'c':[],'D':list(range(12,16)),'d':[],'E':[],'e':[],'F':[],'f':[],'G':[]}
Group_Nums[5] = {'A':list(range(4)),'B':list(range(4,8)),'C':list(range(8,16)),'c':[],'D':list(range(16,20)),'d':[],'E':list(range(20,24)),'e':[],'F':[],'f':[],'G':[24]}
Group_Nums[6] = {'A':list(range(4)),'B':[],'C':[4,5,6,7,8,9,10,11],'c':[12,13,14,15,16,17,18,19],'D':[20,21,22,23],'d':[32,33,34,35],'E':[],'e':[],'F':[24,25,26,27],'f':[28,29,30,31],'G':[]}
Group_Nums[7] = {'A':list(range(4)),'B':list(range(4,8)),'C':[8,9,10,11,12,13,14,15],'c':[16,17,18,19,20,21,22,23],'D':[24,25,26,27],'d':[40,41,42,43],'E':[28,29,30,31],'e':[44,45,46,47],'F':[32,33,34,35],'f':[36,37,38,39],'G':[48]}




# Layout of Cube
#
#   W
# G R B O
#   Y
#
#   
# Position of zero:
# R:South
# O:North 
# Y:North
# W:South
# B:East
# G:West


            #self.Nums['R'] = R_Nums[size]
            #self.Nums['O'] = self.Nums['R'][::-1,::-1] + self.surface_num
            #self.Nums['B'] = self.Nums['R'][::-1,::-1] + self.surface_num * 2
            #self.Nums['G'] = self.Nums['R'] + self.surface_num * 3
            #self.Nums['Y'] = np.flip(self.Nums['R'].T,axis = 0) + self.surface_num * 4
            #self.Nums['W'] = np.flip(self.Nums['R'].T,axis = 1) + self.surface_num * 5



class Frame(Tk.Frame):
    def __init__(self,cube_size = 7,F2L = False,OLL = False,Centers = False,Edges = False,Cross = False):
        self.cube_size = cube_size
        Tk.Frame.__init__(self,None)
        self.master.title('Rubiks')
        self.cube = Rubiks_3(size = cube_size,F2L = F2L,OLL = OLL,Centers = Centers,Edges = Edges,Cross = Cross)

        SX = []
        S0 = []
        S1 = []
        S2 = []
        S3 = []
        S4 = []
        S5 = []

        Lis_B = []
        Lis_C = []
        Lis_D = []
        Lis_E = []


        Lis_A = [              

                 
                 ]


        #[0,2,17,18,31,32,37,43]         

        if self.cube_size >= 4:
            Lis_B = [


                     
                     
                     
                     
                

                  


                     ]





                     
            

        if self.cube_size % 2 == 1:
            Lis_C = [





                     
                     ]

        if self.cube_size >= 6:
            Lis_D = [
    
                ]

        if self.cube_size in [5,7]:
            Lis_E = [        
                 ]

            

        
        

        if self.cube_size == 7:
            Lis_F = [
                 ]

        

        if self.cube_size == 2:
            SX = Lis_A
            SX = [
                 
                  ]
            
        elif self.cube_size == 3 and not (F2L or OLL or Cross):
            SX = Lis_A + Lis_C


            SX = [(" F ",),
                  (" R ",),
                  (" U ",),
                  (" M ",),
                  (" F2",),
                  (" R2",),
                  (" U2",),
                  (" M2",),
                  (" y ",),
                  (" y2",),
                  (" x "," y "),
                  (" x2"," y "),
                  (' L2', " D'", " L'", ' D ', " L'", ' F2', ' R ', " U'", " R'", ' F2', ' M2', ' U ', " M'", ' U2', ' M ', ' U ', ' M2'),
                  (" S "," E2"," S'"," E2"),
                  (" R "," U "," R'"," U'"),
                  (" R "," U'"," R'"," U "),
                  self.cube.myperms['SuperFlip00'],
                  self.cube.myperms['SuperDiagFlip00'],
                  self.cube.myperms['CP-A03-00'],
                  self.cube.myperms['CP-B03-00'],
                  self.cube.myperms['CP-B08-00'],
                  self.cube.myperms['CP-C00-00'],
                  self.cube.myperms['CP-C01-00'],
                  self.cube.myperms['CP-C02-00'],

                  
                  

                  

                ]

            S0 = [(" U "," M'"," U2"," M "," U "),
                  
                  ]

            
            S1 = [
                ]
            S2 = []
            

            
        elif F2L or OLL:
            SX = [
                  ]

        elif Cross:
            SX = [                
                  ]

        elif Centers:
            SX = [
                  


                  ]

            S0 = []
            S1 = []

        elif Edges:
            SX = [
                  
                  
                  ]

            S0 = []
                  
            S1 = []

        elif self.cube_size == 4:
            SX = Lis_A + Lis_B

            
            SX = [


                
                    
                  ]

            S0 = [

                ]
            S1 = [
                                    
                  

                ]

            S2 = [
                ]
            
        elif self.cube_size == 5:
            SX = Lis_A + Lis_B + Lis_C + Lis_E

            SX = [
         
                ]

            S0 = [
      
                  ]

            
            S1 = []
            
            S2 = []


            
        elif self.cube_size == 6:
            SX = Lis_A + Lis_B + Lis_D

            SX = [
                  ]
            
        elif self.cube_size == 7:
            SX = Lis_A + Lis_B + Lis_C + Lis_D + Lis_E + Lis_F
        

            SX = [(" R ","2U "),
                  ("3F ","2R "),
                  ("2R ","3F "),
                  (" y "," R'"," F "),
                  (" x "," y "," E "," M "),
                  (" y ","2U "," R2"," F2"),
                  (" y2","2U "," R2"," F2"),
                  (" R "," U "," M "," U2"," M'"," U "," R'"),
                  (" R "," U "," M "," U2"," M'"," U "," R'") + self.cube.myperms['ParitySwap-A0-00'],
                  self.cube.invert_moves(self.cube.myperms['BigQA00']),
                  self.cube.invert_moves(self.cube.myperms['BigQB00']),
                  self.cube.invert_moves(self.cube.myperms['BigQG00']),
                  self.cube.invert_moves(self.cube.myperms['BigQH00']),
                  self.cube.invert_moves(self.cube.myperms['BigQC(0)00']),
                  self.cube.invert_moves(self.cube.myperms['BigQD(0)00']),
                  self.cube.invert_moves(self.cube.myperms['BigQE(0)00']),
                  self.cube.invert_moves(self.cube.myperms['BigQF(0)00']),
                  self.cube.invert_moves(self.cube.myperms['BigQC(0)00']),
                  self.cube.invert_moves(self.cube.myperms['BigQD(0)00']),
                  self.cube.invert_moves(self.cube.myperms['BigQE(0)00']),
                  self.cube.invert_moves(self.cube.myperms['BigQF(0)00']),

                  self.cube.invert_moves(self.cube.myperms['BigRA00']),
                  self.cube.invert_moves(self.cube.myperms['BigRB00']),
                  self.cube.invert_moves(self.cube.myperms['BigRF00']),
                  self.cube.invert_moves(self.cube.myperms['BigRK00']),
                  self.cube.invert_moves(self.cube.myperms['BigRJ(0)00']),
                  self.cube.invert_moves(self.cube.myperms['BigRJ(1)00']),
                  self.cube.invert_moves(self.cube.myperms['BigRJ(2)00']),


                ]
            


            
            S0 = [self.cube.myperms['Wing3-N04-00'],
                  ("2U "," R2","2U'"," L2","2U "," R2","2U'"," L2"),
                  
                  
            
                  
                  
                  
                  
                  
                ]

            
            S1 = [
                  
                  
                  ]

            
            S2 = []

            S3 = [
                  ]

            S4 = []
            

            
            
                  


                
        else:
            SX = []





        self.transform_random = False
        self.cube.create_new_set()
        self.cube.create_new_set()
        self.cube.create_new_set() 
        self.cube.create_new_set()
        self.cube.create_new_set()
        self.cube.create_new_set() 
        self.cube.create_new_set()
        for k in SX:
            self.cube.my_scrambles2[0][k[-1]].add(k)
        for k in S0:
            self.cube.my_scrambles2[1][k[-1]].add(k)
        for k in S1:
            self.cube.my_scrambles2[2][k[-1]].add(k)
        for k in S2:
            self.cube.my_scrambles2[3][k[-1]].add(k)
        for k in S3:
            self.cube.my_scrambles2[4][k[-1]].add(k)
        for k in S4:
            self.cube.my_scrambles2[5][k[-1]].add(k)
        for k in S5:
            self.cube.my_scrambles2[6][k[-1]].add(k)


        #self.scramble_mode = ['inside','outside','out-to-in','in-to-out','alternate','2-1-2','double','']
        self.scramble_mode = ['myperms']

        self.stage = 0
        self.stage_num = len(self.scramble_mode)
        self.N = 0
        self.AI_idx = 0
        self.value_target_gamma = 0.5 ** (1/20)
        
        self.perf_num = np.zeros(self.stage_num,dtype = 'i')
        

        Mid_Size = [512] * 8

        self.AIs = [Rubiks_3_AI(Mid_Size,cube_size = cube_size,Activation = 'ReLU',cube = self.cube,search_mode = 'search2'),
                    Rubiks_3_AI(Mid_Size,cube_size = cube_size,Activation = 'ReLU',cube = self.cube,search_mode = 'search2'),
                    Rubiks_3_AI(Mid_Size,cube_size = cube_size,Activation = 'ReLU',cube = self.cube,search_mode = 'search2'),
                    Rubiks_3_AI(Mid_Size,cube_size = cube_size,Activation = 'ReLU',cube = self.cube,search_mode = 'search2'),
                    Rubiks_3_AI(Mid_Size,cube_size = cube_size,Activation = 'ReLU',cube = self.cube,search_mode = 'search2'),
                    Rubiks_3_AI(Mid_Size,cube_size = cube_size,Activation = 'ReLU',cube = self.cube,search_mode = 'search2'),
                    Rubiks_3_AI(Mid_Size,cube_size = cube_size,Activation = 'ReLU',cube = self.cube,search_mode = 'search2'),
                    Rubiks_3_AI(Mid_Size,cube_size = cube_size,Activation = 'ReLU',cube = self.cube,search_mode = 'search2'),
                    Rubiks_3_AI(Mid_Size,cube_size = cube_size,Activation = 'ReLU',cube = self.cube,search_mode = 'search2'),
                    Rubiks_3_AI(Mid_Size,cube_size = cube_size,Activation = 'ReLU',cube = self.cube,search_mode = 'search2'),
                    Rubiks_3_AI(Mid_Size,cube_size = cube_size,Activation = 'ReLU',cube = self.cube,search_mode = 'search3'),
                    Rubiks_3_AI(Mid_Size,cube_size = cube_size,Activation = 'ReLU',cube = self.cube,search_mode = 'search3'),
                    Rubiks_3_AI(Mid_Size,cube_size = cube_size,Activation = 'ReLU',cube = self.cube,search_mode = 'search3'),
                    Rubiks_3_AI(Mid_Size,cube_size = cube_size,Activation = 'ReLU',cube = self.cube,search_mode = 'search3'),
                    Rubiks_3_AI(Mid_Size,cube_size = cube_size,Activation = 'ReLU',cube = self.cube,search_mode = 'search3'),
                    Rubiks_3_AI(Mid_Size,cube_size = cube_size,Activation = 'ReLU',cube = self.cube,search_mode = 'search3'),
                    Rubiks_3_AI(Mid_Size,cube_size = cube_size,Activation = 'ReLU',cube = self.cube,search_mode = 'search3'),
                    Rubiks_3_AI(Mid_Size,cube_size = cube_size,Activation = 'ReLU',cube = self.cube,search_mode = 'search3'),
                    Rubiks_3_AI(Mid_Size,cube_size = cube_size,Activation = 'ReLU',cube = self.cube,search_mode = 'search3'),
                    Rubiks_3_AI(Mid_Size,cube_size = cube_size,Activation = 'ReLU',cube = self.cube,search_mode = 'search3'),]

        #self.AIs = self.AIs[:10]
        



                
        self.AInum = len(self.AIs)
        self.level = 1 * np.ones((self.AInum,self.stage_num),dtype = 'i')
        self.success = np.zeros((self.AInum,),dtype = 'i')
        self.myval_AI = Rubiks_3_AI([2],cube_size = cube_size,cube = self.cube,Batch_Normalize = True)
        self.myval_AI.params['BNg1'][:] = 1
        self.myval_AI.params['BNb1'][:] = 0
        self.myval_AI.params['BNgV'][:] = 1
        self.myval_AI.params['BNbV'][:] = 0
        self.myval_AI.params['W1'][:] = 0
        self.myval_AI.params['B1'][:] = 0
        self.myval_AI.params['WO_V'][:] = 1
        self._sync_value_target_gamma()


        self.move_keys = self.cube.move_keys




        self.myval_AI.params['W1'][0] = self.cube.makedata()
        #self.myval_AI.params['W1'][0,-192:] *= 1.01
        self.myval_AI.params['WM_V'] *= 0
        for i in range(self.myval_AI.params['WM_V'].shape[0]):
            self.myval_AI.params['WM_V'][i,i] = 1

        self.flip_rotate = ['r120','r240','fUD','rUD','fFB','rFB','fLR','rLR','s','n']
        self.myval_AI.mark_params_dirty()
        #self.flip_rotate = ['','','','','','','','','','']


        self.my_scramble = []


        #self.my_scramble = SX
        if False:
            self.AI_idx = -1
        else:
            self.my_scramble = []
            self.AI_idx = 0




        #self.level[0,0] = 8
          
        self.priority_list = [
            ['G','F','E','D','f','e','d','C','c','A','B'],
            ['c','C','B','A','D','E','F','d','e','f','G'],
            ] * 10
         



        for i in range(self.AInum):
            if i > 0:
                self.AIs[i].datas = self.AIs[0].datas
            self.AIs[i].cube = self.cube




        self.myval_AI.cube = self.cube
        self.myval_AI.datas = self.AIs[0].datas


    

        x = self.cube.makedata()
        X = np.zeros((0,x.shape[0]),dtype = 'f')
        for m in self.move_keys:
            self.cube.make_move(m)
            X = np.r_[X,self.cube.makedata().reshape(1,-1)]
            self.cube.make_move(self.cube.invert_str(m))

        

        B0 = 36 * (self.cube.size - 2) ** 2
        B1 = B0 + len(self.cube.edge_index) * 24
        Bound = 6 * (self.cube.size - 2) ** 2
        x = self.cube.makedata()
        x0 = x.copy()
        x1 = x.copy()
        x2 = x.copy()
        x3 = x.copy()
        x4 = x.copy()
        x5 = np.zeros_like(x)
        x6 = np.zeros_like(x)
        x7 = np.zeros_like(x)
        
        x0[B0 // 3:] *= 0
        x1[:B0 // 3] *= 0
        x1[2 * B0 // 3:] *= 0
        x2[:2 * B0 // 3] *= 0
        x2[B0:] *= 0
        x3[:B0] *= 0
        x3[B1:] *= 0
        x4[:B1] *= 0
        x5[1:B0//6:6] = 1
        x5[0 + B0 // 6:2 * B0//6:6] = 1
        x6[3 + 2 * B0 // 6:3 * B0//6:6] = 1
        x6[2 + 3 * B0 // 6:4 * B0//6:6] = 1
        x7[5 + 4 * B0 // 6:5 * B0//6:6] = 1
        x7[4 + 5 * B0 // 6:6 * B0//6:6] = 1
    
        for i in range(self.AInum):
            self.AIs[i].myperms = {k:self.cube.myperms[k] for k in self.cube.myperms}

            
            self.AIs[i].lr = 5.0e-5
            self.AIs[i].PV_ratio = 4
            self.AIs[i].lr_v = 0.99
            self.AIs[i].lr_h = 0.99
            self.AIs[i].wdlr = 5.0e-4
            self.AIs[i].out_C = 1.0
            self.AIs[i].skip_search = True
            self.AIs[i].weight_decay = True

                
            if i in [2,3,4,5,6,7]:
                self.AIs[i].weight_decay = False
                self.AIs[i].adam = False
                self.AIs[i].lr = 1.0e-6

            if i >= 10:
                self.AIs[i].lr = 1.0e-5
                self.AIs[i].wdlr = 1.0e-4
            
                
                





            for j in range(1,9):
                self.AIs[i].params['B' + str(j)] += 0.05

            self.AIs[i].params['BM_V'] += 0.25
            self.AIs[i].params['BM_P'] += 0.25






            self.AIs[i].mark_params_dirty()
            
            
            


            #self.initialize(i)

        self.AIs[10].search3_C = 0.07
        self.AIs[11].search3_C = 0.07
        self.AIs[12].search3_C = 0.07
        self.AIs[13].search3_C = 0.07
        self.AIs[14].search3_C = 0.07
        self.AIs[15].search3_C = 0.03
        self.AIs[16].search3_C = 0.03
        self.AIs[17].search3_C = 0.03
        self.AIs[18].search3_C = 0.03
        self.AIs[19].search3_C = 0.03

            




        self.myval_AI.myperms = {k:self.cube.myperms[k] for k in self.cube.myperms}
        #self.AIs[2].myperms = {k:self.cube.myperms[k] for k in self.cube.myperms}
        #self.AIs[6].myperms = {k:self.cube.myperms[k] for k in self.cube.myperms}
        #self.AIs[3].myperms = {k:self.cube.myperms[k] for k in self.cube.myperms}
        #self.AIs[7].myperms = {k:self.cube.myperms[k] for k in self.cube.myperms}            

        
        self.myperms_keys = sorted(list(self.cube.myperms.keys()))
        self.myperms_vals = set(self.cube.myperms.values())
        self.myperms_len = len(self.cube.myperms)
        

        self.myperms_col = {}
        for key in self.cube.myperms.keys():
            for m in self.cube.invert_moves(self.cube.myperms[key]):
                self.cube.make_move(m)

            s = reduce(lambda x,y: x+y,self.cube.state)
            if s not in self.myperms_col:
                self.myperms_col[s] = key

            for m in self.cube.myperms[key]:
                self.cube.make_move(m)

        Datas = []
       
        if self.cube_size >= 4:
            Datas += [("2L'","2R'",'2D2','2R ',' U ',"2R'",'2D2','2R '," U'"),
                      ("2B ","2R ","2U ","2R'"," U'","2R ","2U'","2R'"," U "),
                      ("2U ","2D ","2R2","2U ","2D'","2R2"),
                      ] * 10
  
        if self.cube_size in [5,7]:
            Datas += [("2L'","2R'",' E2','2R ',' U ',"2R'",' E2','2R '," U'"), 
                      ("2B ","2R "," E'","2R'"," U'","2R "," E ","2R'"," U "),
                      ("2U ","2D "," M2","2U ","2D'"," M2"),
                      ] * 10
            

        if self.cube_size >= 6:
            Datas += [("2L'","2R'",'3D2','2R ',' U ',"2R'",'3D2','2R '," U'"),
                      ("2B ","2R ","3U ","2R'"," U'","2R ","3U'","2R'"," U "),
                      ("2U ","2D ","3R2","2U ","2D'","3R2"),
                      ] * 10
   
        Datas = Datas + [self.cube.transform(x,48) for x in Datas] + [self.cube.transform(x,24) for x in Datas] + [self.cube.transform(x,72) for x in Datas]

      

        if True:
            for x in Datas:
                d = data(x,self.cube.invert_moves(x),None)
                d.succeeded = True
                self.AIs[0].datas.append(d)

        for i in range(self.AInum):
            self.AIs[i].indices = list(range(len(self.AIs[0].datas)))

        self.grad_index = 0
        self.grad_mode = "IG"
        self.grad_layer = "WO_V"

        self.param_manager = ParamManager(self)
        self.learn_manager = LearnManager(self)
        self.last_perms_reporter = LastPermsReporter(self)
        self.debug_analysis_manager = DebugAnalysisManager(self)
        self.solve_session_manager = SolveSessionManager(self)
        self.search_data_manager = SearchDataManager(self)
        self.myperm_manager = MyPermManager(self)
        self.solve_state = SolveSessionState()
        self.control_panel = ControlPanel(self,self)
        self.control_buttons = self.control_panel
        self.control_panel.grid(row = 0,column = 0,columnspan = 4,sticky = 'ew')
        self._bind_control_panel_aliases()
        font = self.control_panel.font

        self.move_window = Tk.Toplevel(self)
        self.move_window.title('Manual Moves')
        self.move_window.protocol('WM_DELETE_WINDOW',self.hide_move_pad)
        self.move_window.withdraw()
        self.move_buttons = Tk.Frame(self.move_window,relief = Tk.RIDGE,bd = 4)
        self.move_buttons.pack(fill = 'both',expand = True)
        self.close_move_pad_button = Tk.Button(self.move_buttons,text = 'Close',font = font,padx = 1,pady = 1,command = self.hide_move_pad)
        self.close_move_pad_button.grid(row = 0,column = 0,columnspan = len(self.move_keys) // 9 + 1,sticky = 'ew')


        self.movebuttons = {}        
        for i in range(len(self.move_keys)):
            self.movebuttons[self.move_keys[i]] = Move_Button(self.move_buttons,self.move_keys[i],self.cube,font,self)
            self.movebuttons[self.move_keys[i]].grid(row = i % 9 + 1,column = i // 9)


        self.SV = State_viewer(self,cube_size)
        self.SV.grid(row = 1,column = 0,columnspan = 2)
        self.grad_viewer_positive = State_viewer(self,cube_size,mini_mode = True)
        self.grad_viewer_positive.grid(row = 2,column = 0)
        self.grad_viewer_negative = State_viewer(self,cube_size,mini_mode = True)
        self.grad_viewer_negative.grid(row = 2,column = 1)
        self.MV = Move_viewer(self)
        self.MV.grid(row = 1,column = 2,columnspan = 2)

        self.PV = Prob_viewer(self,self.move_keys)
        self.PV.grid(row = 2,column = 2,sticky = 'nw')
        self.success_viewer = SuccessViewer(self,self.AInum)
        self.success_viewer.grid(row = 2,column = 3,sticky = 'nsew')
        self.success_viewer.put_summary(self.success,self.N,self.AI_idx)
    

        self.stop = False

        self.last_perms = {}

        self.solve_state.reset_session()

        if self.cube.F2L or self.cube.OLL or self.cube.Cross or Centers or Edges:
            if self.cube_size >= 6:
                self.transform_idx = [0,48,48,0,48,0,48,0,0,48]
            else:
                self.transform_idx = [0,0,0,0,0,0,0,0,0,0] 
        elif self.cube_size >= 6:
            self.transform_idx = [0,1,50,3,52,5,54,7,56,64]
        else:
            self.transform_idx = [0,1,2,3,4,5,6,7,8,16]

        self.flip_inside_idx = [False,True] * 5

        self.transform_idx += [0] * 10
        self.flip_inside_idx += [False] * 10
        
            

        self.data_len = len(self.AIs[0].datas)
        
        
    def initialize(self,N):
        #for key in ['W1','W2','W3','W4','W5','W6','W7','W8','WM_P','WM_V']:
        for key in ['W1']:
            if key in self.AIs[N].params:
                Z = np.linalg.svd(self.AIs[N].params[key])
                Z[1][8:] = 0
                A = np.zeros_like(self.AIs[N].params[key],dtype = 'f')
                size = Z[1].shape[0]
                A[:size,:size] = np.diag(Z[1])
                self.AIs[N].params[key][:] = Z[0] @ A @ Z[2]
                self.AIs[N].v[key] *= 0
                

    def toggle_move_pad(self):
        if self.move_window.state() == 'withdrawn':
            self.show_move_pad()
        else:
            self.hide_move_pad()

    def show_move_pad(self):
        self.move_window.deiconify()
        self.move_window.lift()
        self.open_move_pad_button.configure(text = 'hide manual moves')

    def hide_move_pad(self):
        self.move_window.withdraw()
        self.open_move_pad_button.configure(text = 'manual moves')

    def _bind_control_panel_aliases(self):
        alias_names = [
            'reset_button',
            'stopper_button',
            'my_solve_button',
            'loadparams_all_button',
            'saveparams_all_button',
            'make_myperm_button',
            'lpk_button',
            'param_index_var',
            'param_index_entry',
            'loadparams_selected_button',
            'saveparams_selected_button',
            'sum_and_var_button',
            'level_var',
            'level_entry',
            'set_level_button',
            'show_counter_button',
            'lp_show_button',
            'open_move_pad_button',
            'grad_index_var',
            'grad_index_entry',
            'grad_mode_var',
            'grad_mode_menu',
            'grad_layer_var',
            'grad_layer_entry',
            'show_debug_viewer_button',
        ]
        for alias_name in alias_names:
            setattr(self, alias_name, getattr(self.control_panel, alias_name))

    def _selected_param_indices(self):
        return self.param_manager.selected_indices(self.param_index_var.get())

    def loadparams_selected(self, keylis = None):
        self.param_manager.load_selected(self.param_index_var.get(), keylis = keylis)

    def saveparams_selected(self, keylis = None):
        self.param_manager.save_selected(self.param_index_var.get(), keylis = keylis)

    def sum_and_var_from_entry(self):
        for index in self._selected_param_indices():
            self.sum_and_var(index)

    def show_counter_from_entry(self):
        text = self.level_var.get().strip()
        if text == '':
            return
        try:
            counter_index = int(text)
        except ValueError:
            return
        self.show_counter(counter_index)

    def set_value_target_gamma(self, gamma):
        try:
            self.value_target_gamma = float(gamma)
        except ValueError:
            return False
        self._sync_value_target_gamma()
        return True

    def _sync_value_target_gamma(self):
        for ai in self.AIs:
            ai.value_target_gamma = self.value_target_gamma
        self.myval_AI.value_target_gamma = self.value_target_gamma

    def set_level_from_entry(self):
        text = self.level_var.get().strip()
        if text == '':
            return
        try:
            level = int(text)
        except ValueError:
            return
        self.set_level(level)

    def show_debug_viewer_from_entry(self):
        self.debug_analysis_manager.update_viewer_settings(
            self.grad_index_var.get(),
            self.grad_mode_var.get(),
            self.grad_layer_var.get(),
        )
        self.debug_analysis_manager.show_current_viewer(self.AI_idx,self.cube_size ** 2)

    def set_level(self,N):
        #self.load_lists()
        self.level[:] = N

    def myperms_col_key(self,M):
        return self.myperm_manager.myperms_col_key(M)
        

    def sum_and_var(self,i):
        self.debug_analysis_manager.sum_and_var(i)


    def save_lists(self):
        f = open('Datas.binaryfile','wb')
        pickle.dump(self.AIs[0].datas,f)
        f.close()


    def load_lists(self):
        f = open('Datas.binaryfile','rb')
        L = pickle.load(f)
        f.close()

        for i in range(self.AInum):
            self.AIs[i].datas = L
            self.AIs[i].indices = list(range(len(L)))

    def max_val(self,T0 = (),T1 = (),head = '',Top = True,Num = 1):
        self.debug_analysis_manager.max_val(T0 = T0,T1 = T1,head = head,Top = Top,Num = Num)

    def lpk(self):
        self.last_perms_reporter.lpk()
                

    def lp_show(self,key,N = None):
        self.last_perms_reporter.lp_show(key,N = N)

    def show_counter(self,N):
        self.last_perms_reporter.show_counter(N)

    def search_myperms(self,T0,T1,head):
        return self.myperm_manager.search_myperms(T0,T1,head)

    def normalize(self,i):
        self.debug_analysis_manager.normalize(i)
                
                    
    def re_activate(self,i):
        self.debug_analysis_manager.re_activate(i)
                    



    def set_color(self,S):
        self.SV.set_color(S)
    
    def reset(self):
        self.cube.reset()
        self.set_color(self.cube.state)

    def make_myperm(self):
        self.myperm_manager.open_apply_dialog()
    
    def lp_show_by_button(self):
        Frame = Tk.Toplevel(self)
        Frame.title('show lp')
        E = Tk.Entry(master = Frame,width = 20)
        E.grid(row = 0,column = 0)
        B = lp_show_key(Frame,self,E)
        B.grid(row = 1,column = 0)


    def my_solve(self):
        self.solve_session_manager.my_solve()

    def _schedule_next_solve(self):
        if self.cube.is_perfect():
            self.after(10,self.my_solve)
        else:
            self.after(10,self.my_solve)

    def learn(self):
        self.learn_manager.learn_all()
        
    def AIlearn(self,Indices):
        self.learn_manager.learn_indices(Indices)
    
    def stopper(self):
        self.stop = not self.stop
        if self.stop:
            self.stopper_button.configure(text = 'restart')
            self.my_solve_button.configure(state = Tk.NORMAL)
            for k in self.move_keys:
                self.movebuttons[k].configure(state = Tk.NORMAL)
        else:
            self.stopper_button.configure(text = 'stop')
                    
    def loadparams(self,N,keylis = None):
        self.param_manager.load(N, keylis = keylis)

    def saveparams(self,N,keylis = None):
        self.param_manager.save(N, keylis = keylis)

    def loadparams_all(self,keylis = None):
        self.param_manager.load_all(keylis = keylis)
    
    def saveparams_all(self,keylis = None):
        self.param_manager.save_all(keylis = keylis)

    def myfunc(self):
        self.last_perms_reporter.myfunc()

    def myfunc2(self,N = 0):
        self.last_perms_reporter.myfunc2(N = N)

    def myviewer(self,AInum,i,N = 1,SVD = False,Grad = False,IG = False,layer = "WO_V"):
        self.debug_analysis_manager.myviewer(AInum,i,N = N,SVD = SVD,Grad = Grad,IG = IG,layer = layer)

        
            
class make_myperm_OK(Tk.Button):
    def __init__(self,master,frame,entry):
        Tk.Button.__init__(self,master,text = 'OK',command = self.make_myperm)
        self.frame = frame
        self.entry = entry
        self.master = master

    def make_myperm(self):
        text = self.entry.get()
        self.frame.myperm_manager.apply_named_myperm(text)
        self.master.destroy()


class lp_show_key(Tk.Button):
    def __init__(self,master,frame,entry):
        Tk.Button.__init__(self,master,text = 'Show',command = self.show_key)
        self.frame = frame
        self.entry = entry
        self.master = master

    def show_key(self):
        text = self.entry.get()
        self.frame.lp_show(text)
        self.master.destroy()


class MyPermManager:
    """mypermの検索・適用・色キー変換を担当する。"""

    def __init__(self, frame):
        self.frame = frame

    def myperms_col_key(self, moves):
        """手順を色配置キーへ変換し、登録済みmyperm色キーがあれば返す。"""
        self.frame.cube.reset()
        for move in self.frame.cube.invert_moves(moves):
            self.frame.cube.make_move(move)

        state_key = reduce(lambda left,right: left + right,self.frame.cube.state)
        self.frame.cube.reset()
        if state_key in self.frame.myperms_col:
            return self.frame.myperms_col[state_key]
        return ''

    def search_myperms(self, prefix_moves, suffix_moves, head):
        """先頭条件・末尾条件・head文字列でmypermキーを絞り込む。"""
        if suffix_moves != ():
            return [
                key for key in self.frame.cube.myperms
                if key[:len(head)] == head
                and self.frame.cube.myperms[key][-len(suffix_moves):] == suffix_moves
                and self.frame.cube.myperms[key][:len(prefix_moves)] == prefix_moves
            ]
        return [
            key for key in self.frame.cube.myperms
            if key[:len(head)] == head
            and self.frame.cube.myperms[key][:len(prefix_moves)] == prefix_moves
        ]

    def open_apply_dialog(self):
        """myperm名を入力して適用するための小さなダイアログを開く。"""
        dialog = Tk.Toplevel(self.frame)
        dialog.title('make myperm')
        entry = Tk.Entry(master = dialog,width = 20)
        entry.grid(row = 0,column = 0)
        button = make_myperm_OK(dialog,self.frame,entry)
        button.grid(row = 1,column = 0)

    def apply_named_myperm(self, myperm_key):
        """指定されたmyperm名の手順を実行してStateViewerを更新する。"""
        if myperm_key not in self.frame.myperms_keys:
            return
        for move in self.frame.cube.myperms[myperm_key]:
            self.frame.cube.make_move(move)
        self.frame.set_color(self.frame.cube.state)


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
        perfect_key = '0'
        state_key = ''.join(self.frame.cube.state)
        if state_key not in F.myperms_col:
            for key in ['A','B','C','c','D','d','E','e','F','f','G']:
                value = self.frame.cube.total_val[key] - (self.frame.cube.group_val[key] @ x)[0][0]
                if value > 0.01:
                    perfect_key += key + str(int(round(value,0)))
        else:
            perfect_key = F.myperms_col[state_key][:-2]
            simplified_lis = self.frame.cube.transform(simplified_lis,int(F.myperms_col[state_key][-2:]))
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
        """優先順位に従って、次に注目するgroup keyを選ぶ。"""
        top_group = 'A'
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
        myperms_key = set([])
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
        state.val_lis.append(perfect_val)
        state.key_lis.append(perfect_key)
        state.val_lis2.append([])
        state.move_lis.append(AI.myperms[perfect_key])
        state.display_key_lis.append(perfect_key)
        state.display_move_lis.append(AI.myperms[perfect_key])
        state.display_root_lis.append(state.display_val_lis[-1])
        state.display_val_lis.append(perfect_val)
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

    def _viewer_states(self, vector, N):
        """ベクトルの上位N個と下位N個を、それぞれStateViewer用の状態に変換する。"""
        positive_state = np.zeros(6 * self.frame.cube.surface_num,dtype = str)
        negative_state = np.zeros(6 * self.frame.cube.surface_num,dtype = str)
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


class ParamManager:
    """AIパラメータの保存・読込と、対象AI indexの解釈を担当する。"""

    def __init__(self, frame):
        self.frame = frame

    def selected_indices(self, text):
        """カンマ区切りの入力文字列から、有効なAI indexだけを重複なしで取り出す。"""
        if text.strip() == '':
            return []
        indices = []
        for part in text.split(','):
            index = self._parse_index(part)
            if index is not None and index not in indices:
                indices.append(index)
        return indices

    def _parse_index(self, text):
        """1つの文字列をAI indexとして解釈し、範囲外や不正値ならNoneを返す。"""
        text = text.strip()
        if text == '':
            return None
        try:
            index = int(text)
        except ValueError:
            return None
        if 0 <= index < self.frame.AInum:
            return index
        return None

    def load(self, index, keylis = None):
        """指定AIのパラメータ・optimizer状態をAIdatasから読み込む。"""
        ai = self.frame.AIs[index]
        data_dir = self._data_dir(index)
        for key in self._target_keys(ai, keylis):
            self._load_param_set(ai, data_dir, key)
        self._after_load(ai)

    def save(self, index, keylis = None):
        """指定AIのパラメータ・optimizer状態をAIdatasへ保存する。"""
        ai = self.frame.AIs[index]
        data_dir = self._data_dir(index)
        for key in self._target_keys(ai, keylis):
            self._save_param_set(ai, data_dir, key)

    def load_all(self, keylis = None):
        """全AIのパラメータを順番に読み込む。"""
        for index in range(self.frame.AInum):
            self.load(index, keylis = keylis)

    def save_all(self, keylis = None):
        """全AIのパラメータを順番に保存する。"""
        for index in range(self.frame.AInum):
            self.save(index, keylis = keylis)

    def load_selected(self, text, keylis = None):
        """入力欄で指定されたAI indexだけを読み込む。"""
        for index in self.selected_indices(text):
            self.load(index, keylis = keylis)

    def save_selected(self, text, keylis = None):
        """入力欄で指定されたAI indexだけを保存する。"""
        for index in self.selected_indices(text):
            self.save(index, keylis = keylis)

    def _data_dir(self, index):
        """AI indexに対応する保存ディレクトリ名を作る。"""
        return './AIdatas' + str(index)

    def _target_keys(self, ai, keylis):
        """除外リストに含まれないパラメータkeyだけを列挙する。"""
        skipped_keys = set([] if keylis is None else keylis)
        return [key for key in ai.params.keys() if key not in skipped_keys]

    def _load_param_set(self, ai, data_dir, key):
        """1つのkeyについて、重み・v・hを読み込む。"""
        ai.params[key][:] = np.load(os.path.join(data_dir,key + '.npy'))
        ai.v[key][:] = np.load(os.path.join(data_dir,key + '_v.npy'))
        ai.h[key][:] = np.load(os.path.join(data_dir,key + '_h.npy'))

    def _save_param_set(self, ai, data_dir, key):
        """1つのkeyについて、重み・v・hを保存する。"""
        np.save(os.path.join(data_dir,key + '.npy'),ai.params[key])
        np.save(os.path.join(data_dir,key + '_v.npy'),ai.v[key])
        np.save(os.path.join(data_dir,key + '_h.npy'),ai.h[key])

    def _after_load(self, ai):
        """読込後に完成状態の評価値と推論キャッシュを更新する。"""
        ai.set_perfect_val()
        ai.mark_params_dirty()


class LearnManager:
    """FrameからAI学習の実行順序とSearch2/Search3の呼び分けを切り出す。"""

    def __init__(self, frame):
        self.frame = frame

    def learn_all(self):
        """登録されている全AIを学習する。"""
        self.learn_indices(range(self.frame.AInum))

    def learn_indices(self, indices):
        """指定されたAI index群だけを順番に学習する。"""
        for index in indices:
            if self.should_learn(index):
                result = self.learn_one(index)
                self.log_result(index,result)

    def should_learn(self, index):
        """指定AIを学習対象にするか判定する。現状は既存条件をそのまま維持する。"""
        return len(self.frame.AIs[index].indices) >= 0

    def learn_one(self, index):
        """1つのAIを学習し、学習後処理を行って結果を返す。"""
        ai = self.frame.AIs[index]
        result = self.run_learning(index,ai)
        self.after_learning(ai)
        return result

    def run_learning(self, index, ai):
        """AIのsearch_modeに応じてSearch2型またはSearch3型の学習を呼び分ける。"""
        if self.uses_search2_learning(ai):
            return ai.learn(
                transformation = self.transformation_for(index),
                flip_inside = self.flip_inside_for(index),
            )

        return ai.learn_search3(
            transformation = self.transformation_for(index),
            flip_inside = self.flip_inside_for(index),
        )

    def uses_search2_learning(self, ai):
        """このAIがSearch2型の学習を使うか判定する。"""
        return ai.search_mode == 'search2'

    def transformation_for(self, index):
        """指定AIに対応するキューブ変換indexを返す。"""
        return self.frame.transform_idx[index]

    def flip_inside_for(self, index):
        """指定AIに対応する内側反転フラグを返す。"""
        return self.frame.flip_inside_idx[index]

    def after_learning(self, ai):
        """学習後に完成状態の評価値を再計算する。"""
        ai.set_perfect_val()

    def log_result(self, index, result):
        """学習結果を標準出力へ表示する。"""
        print(index,result)


class LastPermsReporter:
    """last_permsや探索済み手順の長さを比較・表示する診断処理を担当する。"""

    def __init__(self, frame):
        self.frame = frame

    def lpk(self):
        """last_permsの最短手数を既存mypermsと比較して表示する。"""
        length_dict,set_dict = self._last_perm_lengths()
        self._print_length_comparison(length_dict,set_dict)

    def lp_show(self, key, N = None):
        """指定keyのlast_permsから、指定手数または最短手数の手順を表示する。"""
        if N == None:
            N = self._minimum_length(key)
        for moves in self.frame.last_perms[key]:
            if len(moves) == N:
                print(moves)

    def show_counter(self, N):
        """cube.counter[N]に記録された手順と回数を優先度順に表示する。"""
        counter_dict = self._counter_heap(N)
        while len(counter_dict) > 0:
            moves,count = counter_dict.popitem()
            print(moves,count)

    def myfunc(self):
        """my_scrambles2に登録された各keyの手順数を深さごとに表示する。"""
        scramble_table = self.frame.cube.my_scrambles2
        for key in scramble_table[0].keys():
            length_limit = min(21,len(scramble_table))
            lengths = np.zeros(length_limit,dtype = 'i')
            for index in range(length_limit):
                lengths[index] = len(scramble_table[index][key])

            print(key,lengths)

    def myfunc2(self, N = 0):
        """my_scrambles2[N]の各手順について、先頭手と末尾手だけを表示する。"""
        for key in self.frame.cube.my_scrambles2[N].keys():
            for moves in self.frame.cube.my_scrambles2[N][key]:
                print(moves[0],moves[-1])

    def _last_perm_lengths(self):
        """last_permsからkeyごとの全手数リストと最短手数heapを作る。"""
        length_dict = heapdict()
        set_dict = {}
        for key in sorted(self.frame.last_perms.keys()):
            lengths = [len(moves) for moves in self.frame.last_perms[key]]
            set_dict[key] = lengths
            length_dict[key] = min(lengths)
        return length_dict,set_dict

    def _print_length_comparison(self, length_dict, set_dict):
        """最短手数heapを取り出しながら、keyごとの比較結果を表示する。"""
        while len(length_dict) > 0:
            key,value = length_dict.popitem()
            self._print_key_length_comparison(key,value,set_dict[key])

    def _print_key_length_comparison(self, key, value, lengths):
        """1つのkeyについて、last_perms側と登録済みmyperms側の手数を比較表示する。"""
        myperms_key = key + '00'
        if myperms_key not in self.frame.cube.myperms:
            print(key,value,set(lengths))
            return

        current_length = value
        registered_length = len(self.frame.cube.myperms[myperms_key])
        marker = self._comparison_marker(current_length,registered_length)
        if marker == '':
            print(key,current_length,registered_length,lengths)
        else:
            print(key,current_length,registered_length,marker,lengths)

    def _comparison_marker(self, current_length, registered_length):
        """手数比較の結果を表示用マーカーに変換する。"""
        if current_length < registered_length:
            return '<-----------------'
        if current_length == registered_length:
            return '================='
        return ''

    def _minimum_length(self, key):
        """指定keyに対するlast_perms内の最短手数を返す。"""
        return min([len(moves) for moves in self.frame.last_perms[key]])

    def _counter_heap(self, N):
        """counterの内容を値順に取り出せるheapdictへ詰め替える。"""
        counter_dict = heapdict()
        for moves in self.frame.cube.counter[N]:
            counter_dict[moves] = self.frame.cube.counter[N][moves]
        return counter_dict


class ControlPanel(Tk.Frame):
    """Frame上部の操作ボタン・入力欄をまとめて配置する。"""

    def __init__(self,master,frame):
        Tk.Frame.__init__(self,master,relief = Tk.RIDGE,bd = 4)
        self.frame = frame
        self.font = ('Century Gothic',14,'bold')
        self._build_buttons()
        self._configure_columns()

    def _build_buttons(self):
        """操作ボタンと入力欄を生成し、grid上に配置する。"""
        self.reset_button = Tk.Button(self,text = 'Reset',font = self.font,padx = 1,pady = 1,command = self.frame.reset)
        self.reset_button.grid(row = 0,column = 0,sticky = 'ew')
        self.stopper_button = Tk.Button(self,text = 'Stop',font = self.font,padx = 1,pady = 1,command = self.frame.stopper)
        self.stopper_button.grid(row = 0,column = 1,sticky = 'ew')
        self.my_solve_button = Tk.Button(self,text = 'start solving',font = self.font,padx = 1,pady = 1,command = self.frame.my_solve)
        self.my_solve_button.grid(row = 0,column = 2,columnspan = 2,sticky = 'ew')
        self.loadparams_all_button = Tk.Button(self,text = 'loadparams all',font = self.font,padx = 1,pady = 1,command = self.frame.loadparams_all)
        self.loadparams_all_button.grid(row = 0,column = 4,sticky = 'ew')
        self.saveparams_all_button = Tk.Button(self,text = 'saveparams all',font = self.font,padx = 1,pady = 1,command = self.frame.saveparams_all)
        self.saveparams_all_button.grid(row = 0,column = 5,sticky = 'ew')
        self.make_myperm_button = Tk.Button(self,text = 'make myperm',font = self.font,padx = 1,pady = 1,command = self.frame.make_myperm)
        self.make_myperm_button.grid(row = 0,column = 6,sticky = 'ew')
        self.lpk_button = Tk.Button(self,text = 'lpk',font = self.font,padx = 1,pady = 1,command = self.frame.lpk)
        self.lpk_button.grid(row = 0,column = 7,sticky = 'ew')

        self.param_index_label = Tk.Label(self,text = 'idx',font = self.font)
        self.param_index_label.grid(row = 1,column = 0,sticky = 'e')
        self.param_index_var = Tk.StringVar(value = '0')
        self.param_index_entry = Tk.Entry(self,font = self.font,textvariable = self.param_index_var)
        self.param_index_entry.grid(row = 1,column = 1,sticky = 'ew')
        self.loadparams_selected_button = Tk.Button(self,text = 'loadparams sel',font = self.font,padx = 1,pady = 1,command = self.frame.loadparams_selected)
        self.loadparams_selected_button.grid(row = 1,column = 2,sticky = 'ew')
        self.saveparams_selected_button = Tk.Button(self,text = 'saveparams sel',font = self.font,padx = 1,pady = 1,command = self.frame.saveparams_selected)
        self.saveparams_selected_button.grid(row = 1,column = 3,sticky = 'ew')
        self.sum_and_var_button = Tk.Button(self,text = 'sum&var',font = self.font,padx = 1,pady = 1,command = self.frame.sum_and_var_from_entry)
        self.sum_and_var_button.grid(row = 1,column = 8,sticky = 'ew')
        self.level_label = Tk.Label(self,text = 'level',font = self.font)
        self.level_label.grid(row = 1,column = 4,sticky = 'e')
        self.level_var = Tk.StringVar(value = '0')
        self.level_entry = Tk.Entry(self,font = self.font,textvariable = self.level_var)
        self.level_entry.grid(row = 1,column = 5,sticky = 'ew')
        self.set_level_button = Tk.Button(self,text = 'set level',font = self.font,padx = 1,pady = 1,command = self.frame.set_level_from_entry)
        self.set_level_button.grid(row = 1,column = 6,sticky = 'ew')
        self.show_counter_button = Tk.Button(self,text = 'show counter',font = self.font,padx = 1,pady = 1,command = self.frame.show_counter_from_entry)
        self.show_counter_button.grid(row = 1,column = 7,sticky = 'ew')
        self.lp_show_button = Tk.Button(self,text = 'lp show',font = self.font,padx = 1,pady = 1,command = self.frame.lp_show_by_button)
        self.lp_show_button.grid(row = 0,column = 8,sticky = 'ew')
        self.open_move_pad_button = Tk.Button(self,text = 'manual moves',font = self.font,padx = 1,pady = 1,command = self.frame.toggle_move_pad)
        self.open_move_pad_button.grid(row = 2,column = 8,sticky = 'ew')

        self.grad_index_label = Tk.Label(self,text = 'grad idx',font = self.font)
        self.grad_index_label.grid(row = 2,column = 0,sticky = 'e')
        self.grad_index_var = Tk.StringVar(value = str(self.frame.grad_index))
        self.grad_index_entry = Tk.Entry(self,font = self.font,textvariable = self.grad_index_var)
        self.grad_index_entry.grid(row = 2,column = 1,sticky = 'ew')
        self.grad_mode_label = Tk.Label(self,text = 'mode',font = self.font)
        self.grad_mode_label.grid(row = 2,column = 2,sticky = 'e')
        self.grad_mode_var = Tk.StringVar(value = self.frame.grad_mode)
        self.grad_mode_menu = Tk.OptionMenu(self,self.grad_mode_var,'W1','SVD','Grad','IG')
        self.grad_mode_menu.configure(font = self.font)
        self.grad_mode_menu.grid(row = 2,column = 3,sticky = 'ew')
        self.grad_layer_label = Tk.Label(self,text = 'layer',font = self.font)
        self.grad_layer_label.grid(row = 2,column = 4,sticky = 'e')
        self.grad_layer_var = Tk.StringVar(value = self.frame.grad_layer)
        self.grad_layer_entry = Tk.Entry(self,font = self.font,textvariable = self.grad_layer_var)
        self.grad_layer_entry.grid(row = 2,column = 5,sticky = 'ew')
        self.show_debug_viewer_button = Tk.Button(self,text = 'show viewer',font = self.font,padx = 1,pady = 1,command = self.frame.show_debug_viewer_from_entry)
        self.show_debug_viewer_button.grid(row = 2,column = 6,columnspan = 2,sticky = 'ew')

    def _configure_columns(self):
        """ControlPanel内の各列を横方向に均等に伸縮させる。"""
        for column_index in range(9):
            self.grid_columnconfigure(column_index, weight = 1)


class SuccessViewer(Tk.Frame):
    """AIごとの成功数と、直近のソルブ結果を表示する。"""

    def __init__(self, master, ai_count):
        Tk.Frame.__init__(self,master,relief = Tk.RIDGE,bd = 4,bg = '#303030')
        self.ai_count = ai_count
        self.history = []
        self.history_limit = 200
        self.history_columns = 40
        self.history_block = 5
        self.font = ('Century Gothic',9,'bold')
        self._build_widgets()

    def _build_widgets(self):
        """成功数・現在回数・履歴表示用のWidgetを作る。"""
        self.title_label = Tk.Label(self,text = 'Success',font = self.font,fg = '#F0F0F0',bg = '#303030')
        self.title_label.grid(row = 0,column = 0,sticky = 'w')
        self.current_label = Tk.Label(self,text = '',font = self.font,fg = '#F0F0F0',bg = '#303030')
        self.current_label.grid(row = 0,column = 1,sticky = 'w')
        self.total_label = Tk.Label(self,text = '',font = self.font,fg = '#F0F0F0',bg = '#303030')
        self.total_label.grid(row = 0,column = 2,sticky = 'w')
        self.ai_label = Tk.Label(self,text = '',font = self.font,fg = '#F0F0F0',bg = '#303030',anchor = 'w',justify = Tk.LEFT)
        self.ai_label.grid(row = 1,column = 0,columnspan = 3,sticky = 'ew')
        self.history_canvas = Tk.Canvas(self,width = 300,height = 36,bg = '#202020',highlightthickness = 0)
        self.history_canvas.grid(row = 2,column = 0,columnspan = 3,sticky = 'ew')
        for column_index in range(3):
            self.grid_columnconfigure(column_index, weight = 1)

    def put_summary(self, success_counts, solve_index, ai_index):
        """成功数配列と現在のソルブ位置を表示する。"""
        self._update_labels(success_counts,solve_index,ai_index,None)
        self._draw_history()

    def put_result(self, success_counts, solve_index, ai_index, succeeded):
        """1回分のソルブ結果を履歴へ追加し、成功数表示を更新する。"""
        self.history.append((solve_index,ai_index,bool(succeeded)))
        if len(self.history) > self.history_limit:
            self.history = self.history[-self.history_limit:]
        self._update_labels(success_counts,solve_index,ai_index,succeeded)
        self._draw_history()

    def _update_labels(self, success_counts, solve_index, ai_index, succeeded):
        """現在回数・直近結果・AIごとの成功数をLabelへ反映する。"""
        result_text = self._result_text(succeeded)
        self.current_label.configure(text = 'N: ' + str(solve_index) + '  AI: ' + str(ai_index) + result_text)
        self.total_label.configure(text = 'total: ' + str(int(np.sum(success_counts))))
        self.ai_label.configure(text = self._success_counts_text(success_counts))

    def _result_text(self, succeeded):
        """直近結果を表示用文字列へ変換する。"""
        if succeeded is None:
            return ''
        if succeeded:
            return '  OK'
        return '  NG'

    def _success_counts_text(self, success_counts):
        """AIごとの成功数を横並びの短い文字列にする。"""
        parts = []
        for index,count in enumerate(success_counts):
            parts.append(str(index) + ':' + str(int(count)))
        return '  '.join(parts[:10]) + '\n' + '  '.join(parts[10:])

    def _draw_history(self):
        """直近ソルブ履歴を色付きの小さいブロックで描画する。"""
        self.history_canvas.delete('history')
        block_size = self.history_block
        margin = 4
        for index,result in enumerate(self.history[-self.history_limit:]):
            column_index = index % self.history_columns
            row_index = index // self.history_columns
            x0 = margin + column_index * (block_size + 2)
            y0 = margin + row_index * (block_size + 2)
            x1 = x0 + block_size
            y1 = y0 + block_size
            color = self._history_color(result[2])
            self.history_canvas.create_rectangle(x0,y0,x1,y1,fill = color,outline = '#101010',tags = 'history')

    def _history_color(self, succeeded):
        """成功/失敗を履歴ブロック用の色に変換する。"""
        if succeeded:
            return Red
        return Blue


class State_viewer(Tk.Canvas):
    def __init__(self,master,cube_size = 3,mini_mode = False):
        self.cube_size = cube_size
        self.surface_num = cube_size ** 2
        self._init_size_parameters(mini_mode)
        self.coordinates = self._build_coordinates()
        self.r_size = self.coordinates[-2 - self.cube_size] + self.blank
        self.c_size = self.coordinates[-1] + self.blank
        self._init_color_maps()
        Tk.Canvas.__init__(self,master,relief = Tk.FLAT , bd = 0,width = self.c_size,height = self.r_size,bg = '#5F5F5F')
        self._init_surface_positions()

    def _init_size_parameters(self, mini_mode):
        if mini_mode:
            self.margin = 0.25
            self.outside_size = 0.5 * outside_size[self.cube_size] + self.margin
            self.inside_size = 0.5 * inside_size[self.cube_size] + self.margin
            self.blank = 5.5
            self.corner_radius = 2
            self.bd_width = 5
        else:
            self.margin = 0.5
            self.outside_size = outside_size[self.cube_size] + 2 * self.margin
            self.inside_size = inside_size[self.cube_size] + 2 * self.margin
            self.blank = 11
            self.corner_radius = 4
            self.bd_width = 10

    def _build_coordinates(self):
        coordinates = np.zeros(4 * self.cube_size + 5,dtype = 'i')
        for index in range(1,4 * self.cube_size + 5):
            coordinates[index] = coordinates[index - 1] + self._coordinate_step(index)
        return coordinates

    def _coordinate_step(self, index):
        if index % (self.cube_size + 1) == 1:
            return self.blank
        if index % (self.cube_size + 1) == 2 or index % (self.cube_size + 1) == 0:
            return self.outside_size
        return self.inside_size

    def _init_color_maps(self):
        self.color = {'R':'#7F0000','W':'#BFBFBF','B':'#0000BF','G':'#007F00','Y':'#BFBF00','O':'#FF7F00','':'#7F7F7F','X':'#7F7F7F'}
        self.bd_color = {'R':'#5F0000','W':'#9F9F9F','B':'#00009F','G':'#005F00','Y':'#9F9F00','O':'#BF5F00','':'#5F5F5F','X':'#5F5F5F'}

    def _init_surface_positions(self):
        self.C = np.zeros(6 * self.surface_num,dtype = 'i')
        self.R = np.zeros(6 * self.surface_num,dtype = 'i')
        args = np.argsort(R_Nums[self.cube_size].reshape(-1))
        for index in range(self.surface_num):
            self._set_surface_position(index, args[index])

    def _set_surface_position(self, index, sorted_index):
        cube_stride = self.cube_size + 1
        row_offset = sorted_index // self.cube_size + 1
        col_offset = sorted_index % self.cube_size + 1

        self.R[index] = cube_stride + row_offset
        self.C[index] = cube_stride + col_offset
        self.R[index + self.surface_num] = 2 * cube_stride - row_offset
        self.C[index + self.surface_num] = 4 * cube_stride - col_offset
        self.R[index + 2 * self.surface_num] = 3 * cube_stride - row_offset
        self.C[index + 2 * self.surface_num] = 2 * cube_stride - col_offset
        self.R[index + 3 * self.surface_num] = row_offset
        self.C[index + 3 * self.surface_num] = cube_stride + col_offset
        self.R[index + 4 * self.surface_num] = 2 * cube_stride - col_offset
        self.C[index + 4 * self.surface_num] = row_offset
        self.R[index + 5 * self.surface_num] = cube_stride + col_offset
        self.C[index + 5 * self.surface_num] = 3 * cube_stride - row_offset

    def set_color(self,S):
        self.delete('squares')
        self._draw_face_backgrounds()
        for index in range(6 * self.surface_num):
            self._draw_sticker(S, index)

    def _draw_face_backgrounds(self):
        cube_stride = self.cube_size + 1
        face_offsets = [(1,0),(0,1),(1,1),(2,1),(3,1),(1,2)]
        for row_offset, col_offset in face_offsets:
            self.create_rectangle(
                self.coordinates[1 + cube_stride * row_offset],
                self.coordinates[1 + cube_stride * col_offset],
                self.coordinates[cube_stride * (row_offset + 1)],
                self.coordinates[cube_stride * (col_offset + 1)],
                fill = '#000000',
                outline = '#000000',
                width = self.bd_width,
                tags = 'squares',
            )

    def _draw_sticker(self, state_text, index):
        c0, r0, c1, r1 = self._sticker_bounds(index)
        points = self._rounded_rectangle_points(c0, r0, c1, r1)
        sticker_color = state_text[index]
        self.create_polygon(points,fill = self.color[sticker_color],outline = self.bd_color[sticker_color],smooth = True,tags = 'squares')

    def _sticker_bounds(self, index):
        c0 = self.coordinates[self.C[index]]
        r0 = self.coordinates[self.R[index]]
        c1 = self.coordinates[self.C[index] + 1]
        r1 = self.coordinates[self.R[index] + 1]
        return c0, r0, c1, r1

    def _rounded_rectangle_points(self, c0, r0, c1, r1):
        return [
            c0 + self.corner_radius * 0.3,r0 + self.corner_radius * 0.3,
            c0,r0 + self.corner_radius,
            c0,r1 - self.corner_radius,
            c0 + self.corner_radius * 0.3,r1 - self.corner_radius * 0.3,
            c0 + self.corner_radius,r1,
            c1 - self.corner_radius,r1,
            c1 - self.corner_radius * 0.3,r1 - self.corner_radius * 0.3,
            c1,r1 - self.corner_radius,
            c1,r0 + self.corner_radius,
            c1 - self.corner_radius * 0.3,r0 + self.corner_radius * 0.3,
            c1 - self.corner_radius,r0,
            c0 + self.corner_radius,r0,
        ]


class Move_viewer(Tk.Canvas):
    def __init__(self,master):
        self.r_size = 400
        self.c_size = 700
        self.text_color = '#FFFFFF'
        self.move_color = '#000000'
        self.font = 'Century Gothic'
        self.font_size = 10
        self.words_in_a_row = 20
        self.c_start = 150
        self.r_start = 100
        self.c_start_cube_state = 100
        self.r_start_cube_state = 20
        self.c_dist = 20
        self.r_dist = 13
        Tk.Canvas.__init__(self,master,relief = Tk.RAISED, bd = 4,width = self.c_size,height = self.r_size,bg = '#000000')
        self.value_start = 600

    def set_str(
        self,
        scramble_state,
        move_rows,
        key_labels,
        root_values,
        leaf_values,
        step_values_per_row,
        solved_count,
        solve_count,
        search_mode,
    ):
        self.delete('text')
        self.delete('header')
        self.delete('squares')
        self._draw_cube_state(scramble_state, solved_count, solve_count)
        row_index = self._header_row_index(scramble_state)
        self._draw_header(row_index)
        row_index += 1
        for move_index in range(1,len(move_rows)):
            row_index = self._draw_log_row(
                move_index,
                move_rows,
                key_labels,
                root_values,
                leaf_values,
                step_values_per_row,
                search_mode,
                row_index,
            )

    def _draw_cube_state(self, state_text, scramble_num, total_num):
        for index, sticker in enumerate(state_text):
            self.create_text(
                self.c_start_cube_state + self.c_dist * (index % self.words_in_a_row),
                self.r_start_cube_state + self.r_dist * (index // self.words_in_a_row),
                text = sticker,
                tags = 'text',
                fill = self.text_color,
                font = (self.font,self.font_size,'bold'),
            )
        self.create_text(
            50,
            20,
            text = str(scramble_num) + '/' + str(total_num),
            tags = 'text',
            fill = self.text_color,
            font = (self.font,self.font_size,'bold'),
        )

    def _header_row_index(self, state_text):
        return max((len(state_text) - 1) // self.words_in_a_row - 4,0)

    def _draw_header(self, row_index):
        header_y = 80 + self.r_dist * row_index
        self.create_text(60,header_y,text = 'Key',tags = 'header',fill = self.text_color,font = (self.font,self.font_size,'bold'))
        self.create_text(self.value_start,header_y,text = 'Value',tags = 'header',fill = self.text_color,font = (self.font,self.font_size,'bold'))
        self.create_text(150,header_y,text = 'Moves',tags = 'header',fill = self.text_color,font = (self.font,self.font_size,'bold'),anchor = 'w')

    def _draw_log_row(self, move_index, move_rows, key_labels, root_values, leaf_values, step_values, search_mode, row_index):
        row_y = 100 + self.r_dist * row_index
        self.create_text(60,row_y,text = key_labels[move_index],tags = 'text',fill = self.text_color,font = (self.font,self.font_size,'bold'))
        self.create_text(self.value_start,row_y,text = self._format_value_text(root_values[move_index], leaf_values[move_index], step_values[move_index]),tags = 'text',fill = self.text_color,font = (self.font,self.font_size,'bold'))

        for step_index, move_label in enumerate(move_rows[move_index]):
            square_color = self._move_square_color(step_values[move_index], step_index, search_mode)
            self.create_rectangle(
                self.c_start + self.c_dist * (step_index % self.words_in_a_row - 0.475),
                self.r_start + self.r_dist * (row_index + step_index // self.words_in_a_row - 0.4),
                self.c_start + self.c_dist * (step_index % self.words_in_a_row + 0.475),
                self.r_start + self.r_dist * (row_index + step_index // self.words_in_a_row + 0.4),
                fill = square_color,
                width = 0,
                tags = 'squares'
            )
            self.create_text(
                self.c_start + self.c_dist * (step_index % self.words_in_a_row),
                self.r_start + self.r_dist * (row_index + step_index // self.words_in_a_row),
                text = move_label,
                tags = 'text',
                fill = self.move_color,
                font = (self.font,self.font_size,'bold'),
            )

        return row_index + self._row_height(move_rows[move_index])

    def _format_value_text(self, root_value, leaf_value, step_values):
        if len(step_values) != 0:
            return f'{root_value:.3f} -> {leaf_value:.3f}'
        return f'{leaf_value:.3f}'

    def _move_square_color(self, step_values, step_index, search_mode):
        if len(step_values) == 0:
            return self.text_color
        step_value = step_values[step_index + 1]
        if search_mode == 'search2':
            return set_color2(step_value)
        if search_mode == 'search3':
            return set_color3(step_value)
        return self.text_color

    def _row_height(self, move_row):
        if len(move_row) == 0:
            return 1
        return (len(move_row) - 1) // self.words_in_a_row + 1


class Prob_viewer(Tk.Canvas):
    def __init__(self,master,move_keys):
        self.r_size = 120
        self.c_size = 350
        self.font = ('Century Gothic',8,'bold')
        self.column_width = 55
        self.row_height = 9
        self.columns = 6

        Tk.Canvas.__init__(self,master,relief = Tk.RAISED, bd = 0,width = self.c_size,height = self.r_size,bg = '#000000')
        self.move_keys = move_keys
        self.move_len = len(self.move_keys)


    def put_val(self,W):
        self._clear_probability_text()
        rounded_probabilities = self._rounded_percentages(W)
        for move_index, move_key in enumerate(self.move_keys):
            self._draw_probability_entry(move_index, move_key, rounded_probabilities[move_index])

    def _clear_probability_text(self):
        self.delete('text')
        self.delete('move')

    def _rounded_percentages(self, probabilities):
        return np.round(probabilities * 100,2)

    def _draw_probability_entry(self, move_index, move_key, probability_value):
        column_index, row_index = self._entry_grid_position(move_index)
        label_x, value_x, row_y = self._entry_coordinates(column_index, row_index)
        self.create_text(label_x,row_y,font = self.font,text = move_key + ':',tags = 'move',fill = '#FFFFFF')
        self.create_text(value_x,row_y,font = self.font,text = str(probability_value) + '%',tags = 'text',fill = set_color(probability_value))

    def _entry_grid_position(self, move_index):
        return move_index % self.columns, move_index // self.columns

    def _entry_coordinates(self, column_index, row_index):
        label_x = (column_index + 0.5) * self.column_width
        value_x = label_x + self.column_width * 0.5
        row_y = self.row_height * (row_index + 1)
        return label_x, value_x, row_y



DeepRed = '#5F0000'
Red = '#BF0000'

DeepOrange = '#7F3F00'
Orange = '#FF7F00'

DeepYellow = '#5F5F00'
Yellow = '#BFBF00'

DeepLime = '#3F7F00'
Lime = '#7FFF00'

DeepGreen = '#005F00'
Green = '#00BF00'

DeepAqua = '#003F7F'
Aqua = '#007FFF'

DeepBlue = '#00007F'
Blue = '#0000FF'

DeepPurple = '#2F005F'
Purple = '#5F00BF'

DeepMagenta = '#7F003F'
Magenta = '#FF007F'

DeepSilver = '#3F3F3F'
Silver = '#7F7F7F'

LightSilver = '#BFBFBF'

White = '#FFFFFF'







def set_color(x):
    if x > 90:
        return Red
    elif x > 70:
        return Orange
    elif x > 50:
        return Yellow
    elif x > 30:
        return Lime
    elif x > 10:
        return Green
    elif x > 7:
        return Aqua
    elif x > 5:
        return Blue
    elif x > 3:
        return Purple
    elif x > 1:
        return Magenta
    elif x > 0.1:
        return Silver
    else:
        return LightSilver

def set_color2(x):
    if x > 0.0:
        return White
    elif x > -20.0:
        return Red
    elif x > -40.0:
        return Orange
    elif x > -60.0:
        return Yellow
    elif x > -80.0:
        return Lime
    elif x > -100.0:
        return Green
    elif x > -120.0:
        return Aqua
    elif x > -140.0:
        return Blue
    elif x > -160.0:
        return Purple
    elif x > -180.0:
        return Magenta
    elif x > -200.0:
        return Silver
    else:
        return LightSilver

def set_color3(x):
    if x > (0.5) ** (1/4):
        return Red
    elif x > (0.5) ** (1/2):
        return Orange
    elif x > (0.5) ** (3/4):
        return Yellow
    elif x > 0.5:
        return Lime
    elif x > (0.5) ** (5/4):
        return Green
    elif x > (0.5) ** (3/2):
        return Aqua
    elif x > (0.5) ** (7/4):
        return Blue
    elif x > (0.5) ** (2):
        return Purple
    elif x > (0.5) ** (3):
        return Magenta
    elif x > (0.5) ** (4):
        return Silver
    else:
        return LightSilver



class Move_Button(Tk.Button):
    def __init__(self,master,m,cube,font,frame):
        self.m = m
        Tk.Button.__init__(self,master,text = m,font = font,padx = 1,pady = 1,command = self.make_move)
        self.cube = cube
        self.frame = frame

    def make_move(self):
        self.cube.make_move(self.m)
        self.frame.SV.set_color(self.cube.state)

        

class MoveSequenceOps:
    """手順列の対称変換・反転・展開をまとめて扱う。"""

    def __init__(self, cube):
        self.cube = cube

    def flip_moves(self, moves, axis = None):
        """指定軸の鏡映ルールで手順列を変換する。"""
        if axis in self.cube.flip.keys():
            return tuple([x[0] + self.cube.flip[axis][x[1:]] for x in moves])
        return tuple(moves)

    def rotate_moves(self, moves, axis = None):
        """指定回転ルールで手順列を回転変換する。"""
        if axis in self.cube.rotate.keys():
            return tuple([x[0] + self.cube.rotate[axis][x[1:]] for x in moves])
        return tuple(moves)

    def diag_flip_moves(self, moves):
        """対角反転ルールで手順列を変換する。"""
        return tuple([x[0] + self.cube.diag_flip[x[1:]] for x in moves])

    def invert_str(self, move):
        """1手だけ逆回転に変換する。"""
        return move[:2] + self.cube.inverse[move[2]]

    def invert_moves(self, moves):
        """手順列を逆順・逆回転にした列を返す。"""
        return tuple([self.invert_str(x) for x in moves[::-1]])

    def swap_moves(self, moves):
        """2層・3層の手を入れ替える補助変換を適用する。"""
        return tuple([self.cube.swap_2_3(x) for x in moves])

    def flip_inside(self, move):
        """1手だけ内外反転ルールで変換する。"""
        if move[0] == ' ':
            return move
        return move[0] + self.cube.opposite[move[1]] + self.cube.inverse[move[2]]

    def flip_inside_moves(self, moves):
        """内外反転ルールで手順列を変換する。"""
        return tuple(self.flip_inside(x) for x in moves)

    def transform(self, moves, transform_index, flip_inside = False, invert = False):
        """変換indexに対応する対称変換を手順列へ適用する。"""
        transform_key = self._transformation_key(transform_index, invert = invert)
        transformed_moves = tuple(moves)
        for transform_step in transform_key:
            transformed_moves = self._apply_transform_step(transformed_moves, transform_step)

        if flip_inside:
            transformed_moves = self.flip_inside_moves(transformed_moves)

        return transformed_moves

    def _transformation_key(self, transform_index, invert = False):
        """変換indexから、実際に適用する変換手順列を取り出す。"""
        transform_key = self.cube.transformation_keys[transform_index]
        if not invert:
            return transform_key
        return tuple([self.cube.tf_invert[step] for step in transform_key[::-1]])

    def _apply_transform_step(self, moves, transform_step):
        """変換手順1つ分だけ手順列へ反映する。"""
        if transform_step in ['UD','FB','LR']:
            return self.flip_moves(moves, axis = transform_step)
        if transform_step == 'S':
            return self.swap_moves(moves)
        if transform_step in ['120','240']:
            return self.rotate_moves(moves, axis = transform_step)
        return self.diag_flip_moves(moves)

    def make_transformations(self, scramble_moves, solution_moves):
        """全ての対称変換について、scramble列とmove列の組を作る。"""
        scramble_list = []
        move_list = []
        for transform_index in range(len(self.cube.transformation_keys)):
            transformed_scramble = self.transform(scramble_moves, transform_index, invert = True)
            transformed_moves = self.transform(solution_moves, transform_index, invert = True)
            scramble_list.append(transformed_scramble)
            move_list.append(transformed_moves)

        return scramble_list, move_list

    def simplify(self, move_lis):
        """同じ面・同じ層の連続手をまとめて手順列を簡約する。"""
        simplified_moves = ()
        for move in move_lis:
            if len(simplified_moves) > 0 and simplified_moves[-1][:2] == move[:2]:
                combined_turn = self.cube.mult[simplified_moves[-1][2],move[2]]
                simplified_moves = simplified_moves[:-1]
                if combined_turn != 0:
                    simplified_moves += (move[:2] + combined_turn,)
            else:
                simplified_moves += (move,)

        return simplified_moves

    def conjugate(self, A, B):
        """共役 A B A^-1 を作って簡約した手順列を返す。"""
        return self.simplify(A + B + self.invert_moves(A))

    def commutator(self, A, B):
        """交換子 A B A^-1 B^-1 を作って簡約した手順列を返す。"""
        return self.simplify(A + B + self.invert_moves(A) + self.invert_moves(B))


class Rubiks_3:
    def __init__(self,S = '',size = 3,F2L = False,OLL = False,Centers = False,Edges = False,Cross = False):        
        
        self.size = size
        self.F2L = F2L and (size == 3)
        self.OLL = OLL and (size == 3)
        self.Centers = Centers
        self.Edges = Edges
        self.Cross = Cross
        if self.F2L:
            self.colors = ['X','O','Y','W','G','B']
        elif self.Centers:
            self.colors = ['R','O','Y','W','G','B']
        else:
            self.colors = ['R','O','Y','W','G','B']
        
        self.move = {}

        self.opposite = {"U":"D","D":"U","F":"B","B":"F","L":"R","R":"L","M":"M","S":"S","E":"E","x":"x","y":"y","z":"z"}


        self.inverse = {" ":"'","'":" ","2":"2"}
        self.mult = {(" "," "):"2",(" ","2"):"'",(" ","'"):0,
                     ("2"," "):"'",("2","2"):0,("2","'"):" ",
                     ("'"," "):0,("'","2"):" ",("'","'"):"2"}
                     

        self.flip = {}
        self.flip['UD'] = {"U ":"D'","D ":"U'","F ":"F'","B ":"B'","L ":"L'","R ":"R'",
                           "U'":"D ","D'":"U ","F'":"F ","B'":"B ","L'":"L ","R'":"R ",
                           "M ":"M'","S ":"S'","E ":"E ","M'":"M ","S'":"S ","E'":"E'",
                           "U2":"D2","D2":"U2","F2":"F2","B2":"B2","L2":"L2","R2":"R2",
                           "M2":"M2","S2":"S2","E2":"E2",
                           "x ":"x'","y ":"y ","z ":"z'","x'":"x ","y'":"y'","z'":"z ",
                           "x2":"x2","y2":"y2","z2":"z2"}
        
        self.flip['FB'] = {"U ":"U'","D ":"D'","F ":"B'","B ":"F'","L ":"L'","R ":"R'",
                           "U'":"U ","D'":"D ","F'":"B ","B'":"F ","L'":"L ","R'":"R ",
                           "M ":"M'","S ":"S ","E ":"E'","M'":"M ","S'":"S'","E'":"E ",
                           "U2":"U2","D2":"D2","F2":"B2","B2":"F2","L2":"L2","R2":"R2",
                           "M2":"M2","S2":"S2","E2":"E2",
                           "x ":"x'","y ":"y'","z ":"z ","x'":"x ","y'":"y ","z'":"z'",
                           "x2":"x2","y2":"y2","z2":"z2"}


        self.flip['LR'] = {"U ":"U'","D ":"D'","F ":"F'","B ":"B'","L ":"R'","R ":"L'",
                           "U'":"U ","D'":"D ","F'":"F ","B'":"B ","L'":"R ","R'":"L ",
                           "M ":"M ","S ":"S'","E ":"E'","M'":"M'","S'":"S ","E'":"E ",
                           "U2":"U2","D2":"D2","F2":"F2","B2":"B2","L2":"R2","R2":"L2",
                           "M2":"M2","S2":"S2","E2":"E2",
                           "x ":"x ","y ":"y'","z ":"z'","x'":"x'","y'":"y ","z'":"z ",
                           "x2":"x2","y2":"y2","z2":"z2"}

        self.rotate = {}
        self.rotate['UD'] = {"U ":"U ","D ":"D ","F ":"L ","B ":"R ","L ":"B ","R ":"F ",
                             "U'":"U'","D'":"D'","F'":"L'","B'":"R'","L'":"B'","R'":"F'",
                             "M ":"S'","S ":"M ","E ":"E ","M'":"S ","S'":"M'","E'":"E'",
                             "U2":"U2","D2":"D2","F2":"L2","B2":"R2","L2":"B2","R2":"F2",
                             "M2":"S2","S2":"M2","E2":"E2",
                             "x ":"z ","y ":"y ","z ":"x'","x'":"z'","y'":"y'","z'":"x ",
                             "x2":"z2","y2":"y2","z2":"x2"}


        self.rotate['FB']= {"U ":"R ","D ":"L ","F ":"F ","B ":"B ","L ":"U ","R ":"D ",
                            "U'":"R'","D'":"L'","F'":"F'","B'":"B'","L'":"U'","R'":"D'",
                            "M ":"E'","S ":"S ","E ":"M ","M'":"E ","S'":"S'","E'":"M'",
                            "U2":"R2","D2":"L2","F2":"F2","B2":"B2","L2":"U2","R2":"D2",
                            "M2":"E2","S2":"S2","E2":"M2",
                            "x ":"y'","y ":"x ","z ":"z ","x'":"y ","y'":"x'","z'":"z'",
                            "x2":"y2","y2":"x2","z2":"z2"}


        self.rotate['LR'] = {"U ":"B ","D ":"F ","F ":"U ","B ":"D ","L ":"L ","R ":"R ",
                             "U'":"B'","D'":"F'","F'":"U'","B'":"D'","L'":"L'","R'":"R'",
                             "M ":"M ","S ":"E'","E ":"S ","M'":"M'","S'":"E ","E'":"S'",
                             "U2":"B2","D2":"F2","F2":"U2","B2":"D2","L2":"L2","R2":"R2",
                             "M2":"M2","S2":"E2","E2":"S2",
                             "x ":"x ","y ":"z'","z ":"y ","x'":"x'","y'":"z ","z'":"y'",
                             "x2":"x2","y2":"z2","z2":"y2"}


        self.rotate['RL'] = {self.rotate['LR'][k]:k for k in self.rotate['LR']}


        self.rotate['120'] = {"U ":"R ","D ":"L ","F ":"U ","B ":"D ","L ":"B ","R ":"F ",
                              "U'":"R'","D'":"L'","F'":"U'","B'":"D'","L'":"B'","R'":"F'",
                              "M ":"S'","S ":"E'","E ":"M ","M'":"S ","S'":"E ","E'":"M'",
                              "U2":"R2","D2":"L2","F2":"U2","B2":"D2","L2":"B2","R2":"F2",
                              "M2":"S2","S2":"E2","E2":"M2",
                              "x ":"z ","y ":"x ","z ":"y ","x'":"z'","y'":"x'","z'":"y'",
                              "x2":"z2","y2":"x2","z2":"y2"}

        self.rotate['240'] = {"U ":"F ","D ":"B ","F ":"R ","B ":"L ","L ":"D ","R ":"U ",
                              "U'":"F'","D'":"B'","F'":"R'","B'":"L'","L'":"D'","R'":"U'",
                              "M ":"E ","S ":"M'","E ":"S'","M'":"E'","S'":"M ","E'":"S ",
                              "U2":"F2","D2":"B2","F2":"R2","B2":"L2","L2":"D2","R2":"U2",
                              "M2":"E2","S2":"M2","E2":"S2",
                              "x ":"y ","z ":"x ","y ":"z ","x'":"y'","z'":"x'","y'":"z'",
                              "x2":"y2","z2":"x2","y2":"z2"}


        self.diag_flip = {"U ":"U'","D ":"D'","F ":"R'","B ":"L'","L ":"B'","R ":"F'",
                          "U'":"U ","D'":"D ","F'":"R ","B'":"L ","L'":"B ","R'":"F ",
                          "M ":"S ","S ":"M ","E ":"E'","M'":"S'","S'":"M'","E'":"E ",
                          "U2":"U2","D2":"D2","F2":"R2","B2":"L2","L2":"B2","R2":"F2",
                          "M2":"S2","S2":"M2","E2":"E2",
                          "x ":"z'","z ":"x'","y ":"y'","x'":"z ","z'":"x ","y'":"y ",
                          "x2":"z2","z2":"x2","y2":"y2"}
                          


        self.transformation_keys = [(),("UD","FB","LR"),("UD","LR"),("FB",),("FB","LR"),("UD",),("UD","FB"),("LR",),
                                    ('120',),("UD","FB","LR",'120'),("UD","LR",'120'),("FB",'120'),("FB","LR",'120'),("UD",'120'),("UD","FB",'120'),("LR",'120'),
                                    ('240',),("UD","FB","LR",'240'),("UD","LR",'240'),("FB",'240'),("FB","LR",'240'),("UD",'240'),("UD","FB",'240'),("LR",'240'),
                                    ("XX",),("UD","FB","LR","XX"),("UD","LR","XX"),("FB","XX"),("FB","LR","XX"),("UD","XX"),("UD","FB","XX"),("LR","XX"),
                                    ('120',"XX"),("UD","FB","LR",'120',"XX"),("UD","LR",'120',"XX"),("FB",'120',"XX"),("FB","LR",'120',"XX"),("UD",'120',"XX"),("UD","FB",'120',"XX"),("LR",'120',"XX"),
                                    ('240',"XX"),("UD","FB","LR",'240',"XX"),("UD","LR",'240',"XX"),("FB",'240',"XX"),("FB","LR",'240',"XX"),("UD",'240',"XX"),("UD","FB",'240',"XX"),("LR",'240',"XX"),
                                    ]

        

        if self.size >= 6:
            self.transformation_keys = [x + y for y in [(),('S',)] for x in self.transformation_keys]


        self.tf_invert = {"UD":"UD","FB":"FB","LR":"LR","120":"240","240":"120","XX":"XX","S":"S"}

        self.move_ops = MoveSequenceOps(self)

        self.axis = {"L":"x","R":"x","M":"x","U":"y","D":"y","E":"y","F":"z","B":"z","S":"z"}
        
        self._init_myperm_containers()
        self._register_myperms2()
        self._expand_registered_myperms()

        self._init_cube_state_and_moves()
        self._init_color_keys_and_groups()
        self._init_myperms_index()

    def _init_myperm_containers(self):
        """myperm登録用の辞書とグループ情報を初期化する。"""
        self.myperms = {}
        self.myperms2 = {}
        self.Group_Nums = Group_Nums[self.size]

    def _register_myperms2(self):
        """myperms2へ固定手順と派生手順を登録する。"""
        self._register_myperms2_base()
        self._register_myperms2_x_perms()
        self._register_myperms2_odd_size()
        self._register_myperms2_general()
        self._register_myperms2_f2l_oll()

    def _register_myperms2_base(self):
        """基本パターンと大分類の手順を登録する。"""
        self.myperms2['Rotate-A'] = (" x ",)
        self.myperms2['Rotate-B'] = (" x2",)
        self.myperms2['Rotate-C'] = (" x "," y ")
        self.myperms2['Rotate-D'] = (" x "," y2")

        self.myperms2['SuperFlip'] = (" U "," R2"," F "," B "," R "," B2"," R "," U2"," L "," B2"," R "," U'"," D'"," R2"," F "," R'"," L "," B2"," U2"," F2")
        self.myperms2['SuperDiagFlip'] = (' U ', ' R2', ' F ', ' B ', ' R ', ' B2', ' R ', ' U2', ' L ', ' B2', ' R ', " U'", " D'", ' R2', ' F ', " L'", ' R ', ' U2', ' D2', ' B2', ' D2', ' B2')
        self.myperms2['SuperDiag'] = (" U2"," D2"," F2"," B2"," R2"," L2")

        self.myperms2['SuperTwist'] = (" U2"," B2"," D "," L2"," F'"," B'"," R2"," D "," F2"," D2"," B "," R2"," U'"," D'"," L2"," B ")
        self.myperms2['SuperTwist2'] = (" D'", ' L ', ' D ', ' R2', " D'", " L'", ' D ', ' R2', ' U2', " B'", ' D ', ' B ', ' U2', " B'", " D'", ' B ', " R'", ' U ', ' R ', ' D2', " R'", " U'", ' R ', ' D2', ' L2', " F'", ' R ', ' F ', ' L2', " F'", " R'", ' F ', ' R ', ' B2', " R'", ' D ', ' F2', " D'", ' R ', ' B2', " R'", ' D ', ' F2', " D'")
        self.myperms2['SuperRotate-A'] = (" L'"," R "," U "," D'"," F'"," B "," L'"," R ")
        self.myperms2['SuperRotate-B'] = (" L'"," R "," U2"," D2"," L'"," R "," F2"," B2")

        self.myperms2['Super-CubeInCube'] = (" F "," L "," F "," U'"," R "," U "," F2"," L2"," U'"," L'"," B "," D'"," B'"," L2"," U ")
        self.myperms2['Super-3Checker'] = (" F "," B2"," R'"," D2"," B "," R "," U "," D'"," R "," L'"," D'"," F'"," R2"," D "," F2"," B'") 
        self.myperms2['Super-6Checker'] = (" F "," B2"," R'"," D2"," B "," R "," U "," D'"," R "," L'"," D'"," F'"," R2"," D "," F2"," B'"," L2"," R2"," U2"," D2"," F2"," B2") 
        self.myperms2['Super-Cage'] = (" L "," U "," F2"," R "," L'"," U2"," B'"," U "," D "," B2"," L "," F "," B'"," R'"," L "," F'"," R ")
        self.myperms2['Super-Stripe'] = (" F "," U "," F "," R "," L2"," B "," D'"," R "," D2"," L "," D'"," B "," R2"," L "," F "," U "," F ")
        

        self.myperms2['Super-CrossA'] = (' R2', ' L2', " U'", ' R2', ' L2', ' U2', ' B2', ' F2', ' D ', ' B2', ' F2', ' U2')
        self.myperms2['Super-CrossB'] = (" L2"," U2"," D2"," F2"," U2"," D2"," L2"," R2"," B2"," R2")
        self.myperms2['Super-CrossC'] = (" R'", ' F2', ' B2', ' R ', ' D ', ' F2', ' B2', " D'", " U'", ' F2', ' B2', ' D ', ' B2', ' F2', ' R ', ' B2', ' F2', " L'")
        self.myperms2['Super-CrossD'] = (' U ', ' R2', ' U2', ' D2', ' B2', ' F2', ' L2', ' B2', ' F2', ' U ', ' D2')

        self.myperms2['Super-Crossa'] = self.myperms2['Super-CrossA'] + self.myperms2['SuperTwist']
        self.myperms2['Super-Crossb'] = self.myperms2['Super-CrossB'] + self.myperms2['SuperTwist']
        self.myperms2['Super-Crossc'] = self.myperms2['Super-CrossC'] + self.myperms2['SuperTwist']
        self.myperms2['Super-Crossd'] = self.myperms2['Super-CrossD'] + self.myperms2['SuperTwist']


        self.myperms2['BigQA'] = (" z'", ' L2', ' F ', " B'", " U'", ' B ', ' D ', ' B ', " D'", ' F ', " B'", ' L ', " B'", " L'", " F'", ' R ', ' F ', " R'", ' F2', ' R2', ' F ', ' B ', ' U ', " F'", " U'", " B'", ' R2', ' F ', " U'")
        self.myperms2['BigQB'] = (" R'", " F'", " D'", " B'", ' D ', " B'", ' F ', " L'", ' B ', ' L ', ' B ', ' R ', " B'", ' F ', " z'")
        self.myperms2['BigQG'] = (" L2"," z'", ' L2', ' F ', " B'", " U'", ' B ', ' D ', ' B ', " D'", ' F ', " B'", ' L ', " B'", " L'", " F'", ' R ', ' F ', " R'", ' F2', ' R2', ' F ', ' B ', ' U ', " F'", " U'", " B'", ' R2', ' F ', " U'"," L2")
        self.myperms2['BigQH'] = (" L2"," R'", " F'", " D'", " B'", ' D ', " B'", ' F ', " L'", ' B ', ' L ', ' B ', ' R ', " B'", ' F ', " z'", " L2")

        self.myperms2['BigQC(0)'] = (" F'"," L'"," R'", " F'", " D'", " B'", ' D ', " B'", ' F ', " L'", ' B ', ' L ', ' B ', ' R ', " B'", ' F ', " z'"," L "," F ")
        self.myperms2['BigQD(0)'] = (" F2"," L'"," R'", " F'", " D'", " B'", ' D ', " B'", ' F ', " L'", ' B ', ' L ', ' B ', ' R ', " B'", ' F ', " z'"," L "," F2")
        self.myperms2['BigQE(0)'] = (" F "," L'"," R'", " F'", " D'", " B'", ' D ', " B'", ' F ', " L'", ' B ', ' L ', ' B ', ' R ', " B'", ' F ', " z'"," L "," F'")
        self.myperms2['BigQF(0)'] = (" L'"," R'", " F'", " D'", " B'", ' D ', " B'", ' F ', " L'", ' B ', ' L ', ' B ', ' R ', " B'", ' F ', " z'"," L ")

        self.myperms2['BigQC(1)'] = self.invert_moves(self.myperms2['BigQC(0)'])
        self.myperms2['BigQD(1)'] = self.invert_moves(self.myperms2['BigQD(0)'])
        self.myperms2['BigQE(1)'] = self.invert_moves(self.myperms2['BigQE(0)'])
        self.myperms2['BigQF(1)'] = self.invert_moves(self.myperms2['BigQF(0)'])


        self.myperms2['BigRA'] = (" U'", " F'", " U'", ' F ', " z'", " B'", ' U ', ' F ', ' U ', " R'", ' F ', " B'", ' D ', ' B ', ' D ', " B'", " D'", ' B ', " F'", ' R ', ' B ', " R'", " B'", ' U2', ' L ', ' U ', " L'", ' U ', ' B2', " D'", ' R ', ' D ', ' B2')
        self.myperms2['BigRB'] = (" U'", " z'", " L'", " F'", " B'", ' F2', " U'", " F'", ' B ', " L'", ' D2', ' L2', " B'", ' F ', " U'", ' L ', " F'", ' L ', ' F2', " R'", ' F ', ' R ', ' F ', ' L ', " F'", ' R2', ' F ', " L'", " F'", ' R2', ' F2')
        self.myperms2['BigRF'] = (" U'", " F'", " U'", " z'", ' F ', " B'", ' U ', ' F ', ' U ', " R'", " B'", ' F ', ' D ', " F'", ' B ', ' D ', " B'", " D'", ' B ', ' R ', ' B ', " R'", " B'", ' U2', ' L ', ' U ', " L'", ' U ', ' B2', " D'", ' R ', ' D ', ' B2')
        self.myperms2['BigRJ(0)'] = (" L'", " F'", " U'", " B'", ' U ', ' F ', " B'", " R'", ' B ', ' R ', ' B ', ' L ', " B'", ' F ', " z'", ' D ', ' L ', " D'", " L'", " F'", " D'", " F'", ' D2', " R'", ' D2', ' R ', ' F2', ' R2', ' U ', " L'", " U'", ' R2', ' U ', ' L ', " U'")
        self.myperms2['BigRJ(1)'] = (' F2', " R'", ' F ', ' D2', " B'", ' L ', ' B ', ' D2', ' F ', " L'", ' F ', ' R ', " F'", ' L ') + self.myperms2['BigQA']
        self.myperms2['BigRJ(2)'] = (' U ', ' B ', ' R ', ' F ', " R'", ' F ', " B'", ' D ', " F'", " D'", " F'", " U'", " B'", ' F ', " U'", " z'", " U'", ' L ', ' U ', ' B ', " L'", " B'", " U'", ' F ', " U'", " F'", ' U2', " L'", ' U ', " R'", " U'", ' L ', ' U ', ' R ', " U'")
        self.myperms2['BigRK'] = (' U ', ' B ', ' R ', ' F ', " R'", " B'", ' F ', ' D ', " F'", " D'", " F'", " U'", ' F ', " B'", " z'", ' L ', ' U ', " L'", " U'", " F'", ' L ', ' F ', ' U ', " B'", ' U ', ' B ', ' U2', ' R2', ' B2', ' R ', ' F2', " R'", ' B2', ' R ', ' F2', ' R ')

        
        self.myperms2['SingleMove-OuterA'] = (" U2",)
        self.myperms2['SingleMove-OuterB'] = (" U ",)        
        if self.size >= 4:
            self.myperms2['SingleMove-InnerA'] = ("2U2",)
            self.myperms2['SingleMove-InnerB'] = ("2U ",)

    def _register_myperms2_x_perms(self):
        """ParitySwap系とその派生手順を登録する。"""
        if self.size <= 3:
            PLLParity = ()
        elif self.size <= 5:
            PLLParity = ("2F2"," R2"," U2","2F2"," U2"," R2","2F2")
        elif self.size <= 7:
            PLLParity = ("2F2","3F2"," R2"," U2","2F2","3F2"," U2"," R2","2F2","3F2")


        self.myperms2['ParitySwap-A0-'] = (' F ', " R'", ' F ', ' D2', " B'", ' L ', ' B ', ' D2', ' F2', ' R ') + PLLParity
        self.myperms2['ParitySwap-A1-'] = (" R'", ' F2', ' D2', " B'", " L'", ' B ', ' D2', " F'", ' R ', " F'") + PLLParity
        self.myperms2['ParitySwap-A2-'] = PLLParity + (" R'", ' F2', ' D2', " B'", " L'", ' B ', ' L ', ' D2', " L'", " F'", ' R ', ' F2', " L'", " F'", ' L ', ' F2')
        self.myperms2['ParitySwap-A3-'] = PLLParity + (' F2', " R'", ' F2', ' D2', " B'", " L'", ' B ', ' L ', ' D2', " L'", " F'", ' R ', ' F2', " L'", " F'", ' L ')
        self.myperms2['ParitySwap-A4-'] = PLLParity + (' F2', ' U2', ' F2', ' U2', ' F ', ' R ', " L'", ' U2', " R'", ' L ', " F'", ' B ', ' U ', " B'", ' U ', ' R2', " D'", ' F ', ' D ', ' R2')
        self.myperms2['ParitySwap-A5-'] = PLLParity + (' U2', ' F2', ' U2', ' F ', ' R ', " L'", ' U2', " R'", ' L ', " F'", ' B ', ' U ', " B'", ' U ', ' R2', " D'", ' F ', ' D ', ' R2', " F2")
        
        
        self.myperms2['ParitySwap-B0-'] = PLLParity + (" L2"," F2"," U2"," L'"," U2"," L2"," F2"," L'"," U2"," L2"," U2"," F2"," L'"," F2")
        self.myperms2['ParitySwap-B1-'] = PLLParity + (" F2"," L "," F2"," U2"," L2"," U2"," L "," F2"," L2"," U2"," L "," U2"," F2"," L2")
        
        self.myperms2['ParitySwap-B2-'] = (" R2", " U2", " B2", " R'", " B2", " R2", " U2", " R ", " B2", " R2", " B2", " U2", " R ", " U2") + PLLParity
        self.myperms2['ParitySwap-B3-'] = (" U2", " R'", " U2", " B2", " R2", " B2", " R'", " U2", " R2", " B2", " R ", " B2", " U2", " R2") + PLLParity

        self.myperms2['ParitySwap-F0-'] = PLLParity + (" R'", ' F ', ' D2', " B'", ' L ', ' B ', ' D2', ' F2', ' R ', " F ")
        self.myperms2['ParitySwap-F1-'] = PLLParity + (" F'", " R'", " F2", " D2", " B'", " L'", " B ", " D2", " F'", " R ")      
        self.myperms2['ParitySwap-F2-'] = (" B ", " L'", ' B2', ' D2', " F'", " R'", ' F ', ' D2', " B'", ' L ', " B2") + PLLParity
        self.myperms2['ParitySwap-F3-'] = (' B2', " L'", ' B ', ' D2', " F'", ' R ', ' F ', ' D2', ' B2', ' L ', " B'") + PLLParity
        self.myperms2['ParitySwap-F4-'] = (" U2", " R'", ' F ', ' D2', " B'", ' L ', ' B ', ' D2', ' F2', ' R ', " F ", " U2") + PLLParity
        self.myperms2['ParitySwap-F5-'] = (" U2", " F'", " R'", " F2", " D2", " B'", " L'", " B ", " D2", " F'", " R ", " U2") + PLLParity




        
        self.myperms2['ParitySwap-J0-'] = (' B2', " L'", ' B2', ' D2', " F'", " R'", ' F ', ' D2', " B'", ' L ', ' B ') + PLLParity
        self.myperms2['ParitySwap-J1-'] = (" B'", " L'", ' B ', ' D2', " F'", ' R ', ' F ', ' D2', ' B2', ' L ', ' B2') + PLLParity

        self.myperms2['ParitySwap-J2-'] = (' F2', " R'", ' F ', ' D2', " B'", ' L ', ' B ', ' D2', ' F ', " L'", ' F ', ' R ', " F'", ' L ') + PLLParity
        self.myperms2['ParitySwap-J3-'] = (" L'", ' F ', " R'", " F'", ' L ', " F'", ' D2', " B'", " L'", ' B ', ' D2', " F'", ' R ', ' F2') + PLLParity

        self.myperms2['ParitySwap-J4-'] = (' B2', ' L2', ' D2', ' F2', ' D2', ' L2', " B'", ' U2', ' L2', ' D ', ' F ', " D'", ' L2', ' U ', " B'", " U'") + PLLParity
        self.myperms2['ParitySwap-J5-'] = (' U ', ' B ', " U'", ' L2', ' D ', " F'", " D'", ' L2', ' U2', ' B ', ' L2', ' D2', ' F2', ' D2', ' L2', ' B2') + PLLParity
    
        self.myperms2['ParitySwap-K0-'] = (" R'", ' U2', ' L ', ' F2', " L'", ' F2', ' R2', ' U2', ' R ', ' U2', " R'", ' U2', ' F2', ' R2', ' F2') + PLLParity
        self.myperms2['ParitySwap-K1-'] = (' R2', ' F2', ' U2', ' R ', ' U2', " R'", ' U2', ' R2', ' F2', ' L ', ' F2', " L'", ' U2', ' R ', ' F2') + PLLParity

        self.myperms2['ParityCycle-QA0-'] = (" F "," R "," U "," R'"," U'"," R "," U'"," R'"," U'"," R "," U "," R'"," F'") + PLLParity
        self.myperms2['ParityCycle-QA1-'] = (" F "," R "," U'"," R'"," U "," R "," U "," R'"," U "," R "," U'"," R'"," F'") + PLLParity
        self.myperms2['ParityCycle-QB0-'] = (" F'"," R "," U "," R'"," U'"," R "," U'"," R'"," U'"," R "," U "," R'"," F ") + PLLParity
        self.myperms2['ParityCycle-QB1-'] = (" F'"," R "," U'"," R'"," U "," R "," U "," R'"," U "," R "," U'"," R'"," F ") + PLLParity
        self.myperms2['ParityCycle-QC0-'] = (" R "," U "," R'"," U'"," R "," U'"," R'"," U'"," R "," U "," R'") + PLLParity
        self.myperms2['ParityCycle-QC1-'] = (" R "," U'"," R'"," U "," R "," U "," R'"," U "," R "," U'"," R'") + PLLParity

 


        if self.size % 2 == 1:
            self.myperms2['CenterX00-'] = (" M "," E "," M'"," E'")
            self.myperms2['CenterX01-'] = (" M "," E2"," M'"," E2")
            self.myperms2['SingleMove-MiddleA'] = (" M2",)
            self.myperms2['SingleMove-MiddleB'] = (" M ",)

        self.myperms2['ParitySwap-XB-'] = self.conjugate((" U "," F'"," R "),self.myperms2['ParitySwap-A0-'])
        self.myperms2['ParitySwap-XC-'] = (' F2', ' R ') + PLLParity + (' F ', " R'", ' F ', ' D2', " B'", ' L ', ' B ', ' D2')
        self.myperms2['ParitySwap-XD-'] = (' F ', ' R ') + PLLParity + ( ' F ', " R'", ' F ', ' D2', " B'", ' L ', ' B ', ' D2', ' F ')
        self.myperms2['ParitySwap-XE-'] = (' R ',) + PLLParity + ( ' F ', " R'", ' F ', ' D2', " B'", ' L ', ' B ', ' D2', " F2")
        self.myperms2['ParitySwap-XF-'] = (" F'", ' R ') + PLLParity + ( ' F ', " R'", ' F ', ' D2', " B'", ' L ', ' B ', ' D2', " F'")
        self.myperms2['ParitySwap-XG-'] = self.conjugate((" R2",),self.myperms2['ParitySwap-A0-'])
        self.myperms2['ParitySwap-XH-'] = self.conjugate((" U'"," F'"," R "),self.myperms2['ParitySwap-A0-'])
        

        self.myperms2['ParitySwap-YA-'] = PLLParity + (" R "," U "," R'"," U'"," R'"," F "," R2"," U'"," R'"," U'"," R "," U "," R'"," F'")
        self.myperms2['ParitySwap-YB-'] = self.conjugate((" U "," F'"," R "),self.myperms2['ParitySwap-YA-'])
        self.myperms2['ParitySwap-YC-'] = self.conjugate((" F2"," R "),self.myperms2['ParitySwap-YA-'])
        self.myperms2['ParitySwap-YD-'] = self.conjugate((" F "," R "),self.myperms2['ParitySwap-YA-'])
        self.myperms2['ParitySwap-YE-'] = self.conjugate((" R ",),self.myperms2['ParitySwap-YA-'])
        self.myperms2['ParitySwap-YF-'] = self.conjugate((" F'"," R "),self.myperms2['ParitySwap-YA-'])
        self.myperms2['ParitySwap-YG-'] = self.conjugate((" R2",),self.myperms2['ParitySwap-YA-'])
        self.myperms2['ParitySwap-YH-'] = self.conjugate((" R'"," U'"," F "," U "),self.myperms2['ParitySwap-YA-'])


        
        self.myperms2['ParitySwap-ZA-'] = PLLParity + (' U2', " B'", ' U2', ' B ', ' U2',' D2', " R'", " B'", ' R ', ' D2', " L'", ' F ', " L'", " F'", ' L2')
        self.myperms2['ParitySwap-ZB-'] = self.conjugate((" F'"," U "," L'"),self.myperms2['ParitySwap-ZA-'])
        self.myperms2['ParitySwap-ZC-'] = self.conjugate((" U2"," L "),self.myperms2['ParitySwap-ZA-'])
        self.myperms2['ParitySwap-ZD-'] = self.conjugate((" U "," L "),self.myperms2['ParitySwap-ZA-'])
        self.myperms2['ParitySwap-ZE-'] = self.conjugate((" L ",),self.myperms2['ParitySwap-ZA-'])
        self.myperms2['ParitySwap-ZF-'] = self.conjugate((" U'"," L "),self.myperms2['ParitySwap-ZA-'])
        self.myperms2['ParitySwap-ZG-'] = self.conjugate((" L2",),self.myperms2['ParitySwap-ZA-'])
        self.myperms2['ParitySwap-ZH-'] = self.conjugate((" F "," U "," L'"),self.myperms2['ParitySwap-ZA-'])
        
        

    def _register_myperms2_odd_size(self):
        """奇数サイズで使うQ/P/R系の手順を登録する。"""
        if self.size % 2 == 1:
            self.myperms2['CenterMidEdgeSwap-QA'] = (' S ', ' D ', ' S ', " D'", ' S ', " D'", ' S ', ' D ', ' S2', " D'", ' S ', ' D2', ' L2', " S'", " D'", " S'", ' D ', ' L2', " D'")
            self.myperms2['CenterMidEdgeSwap-QB'] = (' S ', " D'", ' S ', ' D2', ' L2', " D'", ' S ', " D'", ' S ', ' D2', ' L2', " D'", ' S ')
            self.myperms2['CenterMidEdgeSwap-QC(0)'] = (' R2', " S'", ' R2', ' S2', " U'", ' S ', ' U ', ' S ', ' U ', ' S ', " U'", ' S2', ' D ', ' M ', ' D2', " M'", ' D ', " S'")
            self.myperms2['CenterMidEdgeSwap-QD(0)'] = (' R2', " S'", ' R2', ' S2', " U'", ' R2', ' S ', ' U ', ' S ', ' U ', ' S ', " U'", ' S ', " U'", ' R2', ' U ')
            self.myperms2['CenterMidEdgeSwap-QE(0)'] = (' S ', " D'", ' S ', ' D ', ' S ', ' D ', ' S ', " D'", ' S ', ' M ', ' U ', ' M ', ' U2', " M'", ' U ', " M'")
            self.myperms2['CenterMidEdgeSwap-QF(0)'] = (' S ', ' D ', ' S ', ' D2', ' L2', ' D ', ' S ', ' D ', ' S ', " D'", ' S ', " D'", ' L2', ' D ')
            self.myperms2['CenterMidEdgeSwap-QC(1)'] = self.invert_moves(self.myperms2['CenterMidEdgeSwap-QC(0)'])
            self.myperms2['CenterMidEdgeSwap-QD(1)'] = self.invert_moves(self.myperms2['CenterMidEdgeSwap-QD(0)'])
            self.myperms2['CenterMidEdgeSwap-QE(1)'] = self.invert_moves(self.myperms2['CenterMidEdgeSwap-QE(0)'])
            self.myperms2['CenterMidEdgeSwap-QF(1)'] = self.invert_moves(self.myperms2['CenterMidEdgeSwap-QF(0)'])
            self.myperms2['CenterMidEdgeSwap-QG'] = (' S ', ' R ', ' S ', " R'", ' S ', " R'", ' L2', ' S ', ' R ', ' L2', ' S2', " R'", ' U2', ' R ', " S'", " R'", ' U2', ' R ')
            self.myperms2['CenterMidEdgeSwap-QH'] = (' D ', ' S ', " D'", ' S ', ' D ', ' S ', ' D ', ' S ', " D'", ' S ', " D'", ' S ', ' U2', " S'", ' U2')


            self.myperms2['CenterMidEdgeSwap-PA'] = (" S'", " U'", " S'", ' U ', " S'", ' U ', " S'", " U'", ' S2', ' U ', ' R2', " U'", ' S ', ' U ', " S'", ' R2', ' U2', ' S ', ' U ')
            self.myperms2['CenterMidEdgeSwap-PB'] = (" E'", " M'", ' E ', ' D ', " M'", ' D2', ' F2', ' D ', " M'", ' D ', " M'", ' D2', ' F2', ' D ', " M'")
            self.myperms2['CenterMidEdgeSwap-PX'] = (" E'", ' B ', " E'", " B'", " E'", " B'", " E'", ' B ', ' M ', " E'", " F'", ' M ', ' F2', ' D2', " M'", " F'", " M'", ' F ', ' D2', " F'")
            self.myperms2['CenterMidEdgeSwap-PY'] = (' E ', ' R2', " E'", ' R ', " S'", ' L ', " S'", " L'", " S'", " L'", " S'", ' L ', " S'", ' R ')
            self.myperms2['CenterMidEdgeSwap-PC'] = (' R ', " S'", ' U ', " S'", " U'", ' S ', ' U2', " S'", ' U2', " S'", " U'", " S'", ' U ', ' S2', ' R2', ' S ', ' R ')
            self.myperms2['CenterMidEdgeSwap-PD'] = (" F'", ' U2', ' F ', ' M ', ' F ', ' M ', " F'", ' M ', " F'", ' M ', ' U2', ' F ', ' E ', ' M ', " E'", ' M ', ' U2', " M'", ' U2')
            self.myperms2['CenterMidEdgeSwap-PE'] = (' M ', " E'", " M'", ' F ', " E'", " F'", " E'", " F'", " E'", ' F ', " E'", " M'", " B'", " M'", ' B2', ' M ', " B'", ' M ')
            self.myperms2['CenterMidEdgeSwap-PF'] = (' M ', " E'", " M'", ' F ', " E'", " F'", " E'", " F'", " E'", ' F ', " E'", ' B ', ' M ', ' B2', " M'", ' B ')
            self.myperms2['CenterMidEdgeSwap-PG'] = (" D'", " S'", ' U ', " S'", " U'", " S'", " U'", " S'", ' U ', " S'", " D'", " M'", " F'", " M'", ' F ', ' D2', " F'", ' M ', ' F ', ' M ')
            self.myperms2['CenterMidEdgeSwap-PH'] = (" D'", " S'", ' U ', " S'", " U'", " S'", " U'", " S'", ' U ', " S'", ' D ', ' M ', ' D2', " M'", ' D2')



            



            self.myperms2['CenterCornerSwap-RA(0)'] = self.myperms2['ParitySwap-A0-'] + self.myperms2['CenterMidEdgeSwap-QA']
            self.myperms2['CenterCornerSwap-RA(1)'] = self.myperms2['ParitySwap-A1-'] + self.myperms2['CenterMidEdgeSwap-QA']
            self.myperms2['CenterCornerSwap-RB(0)'] = self.myperms2['ParitySwap-B0-'] + self.myperms2['CenterMidEdgeSwap-QA']
            self.myperms2['CenterCornerSwap-RB(1)'] = self.myperms2['ParitySwap-B1-'] + self.myperms2['CenterMidEdgeSwap-QA']
            self.myperms2['CenterCornerSwap-RF(0)'] = self.myperms2['ParitySwap-F0-'] + self.myperms2['CenterMidEdgeSwap-QA']
            self.myperms2['CenterCornerSwap-RF(1)'] = self.myperms2['ParitySwap-F1-'] + self.myperms2['CenterMidEdgeSwap-QA']           
            self.myperms2['CenterCornerSwap-RJ(0)'] = self.myperms2['ParitySwap-J0-'] + self.myperms2['CenterMidEdgeSwap-QA']
            self.myperms2['CenterCornerSwap-RJ(1)'] = self.myperms2['ParitySwap-J1-'] + self.myperms2['CenterMidEdgeSwap-QA']
            self.myperms2['CenterCornerSwap-RJ(2)'] = self.myperms2['ParitySwap-J2-'] + self.myperms2['CenterMidEdgeSwap-QA']
            self.myperms2['CenterCornerSwap-RJ(3)'] = self.myperms2['ParitySwap-J3-'] + self.myperms2['CenterMidEdgeSwap-QA']
            self.myperms2['CenterCornerSwap-RJ(4)'] = self.myperms2['ParitySwap-J4-'] + self.myperms2['CenterMidEdgeSwap-QA']
            self.myperms2['CenterCornerSwap-RJ(5)'] = self.myperms2['ParitySwap-J5-'] + self.myperms2['CenterMidEdgeSwap-QA']
            self.myperms2['CenterCornerSwap-RK(0)'] = self.myperms2['ParitySwap-ZA-'] + self.myperms2['CenterMidEdgeSwap-QA']
            self.myperms2['CenterCornerSwap-RK(1)'] = self.myperms2['ParitySwap-ZA-'] + self.myperms2['CenterMidEdgeSwap-QA']

            

    def _register_myperms2_general(self):
        """通常モードで使う汎用手順群を登録する。"""
        self._register_myperms2_classic_perms()
        self._register_myperms2_midedge_general()
        self._register_myperms2_edge_general()

    def _register_myperms2_classic_perms(self):
        """小サイズで使うPLL系の基本手順を登録する。"""
        if self.size <= 1:
            self.myperms2['G-Perm-A'] = (" R2"," U'"," R "," U'"," R "," U "," R'"," U "," R2"," U "," D'"," R "," U'"," R'"," D ")
            self.myperms2['G-Perm-B'] = (" D'"," R "," U "," R'"," D "," U'"," R2"," U'"," R "," U'"," R'"," U "," R'"," U "," R2")
            
            self.myperms2['T-Perm'] = (" R "," U "," R'"," U'"," R'"," F "," R2"," U'"," R'"," U'"," R "," U "," R'"," F'")
            self.myperms2['N-Perm'] = (" R'"," U "," R "," U'"," R'"," F'"," U'"," F "," R "," U "," R'"," F "," R'"," F'"," R "," U'"," R ")
            self.myperms2['F-Perm'] = (" R'"," U'"," F'"," R "," U "," R'"," U'"," R'"," F "," R2"," U'"," R'"," U'"," R "," U "," R'"," U "," R ")

            #self.myperms2['J-Perm'] = (" R "," U "," R'"," F'"," R "," U "," R'"," U'"," R'"," F "," R2"," U'"," R'"," U'")
            self.myperms2['J-Perm'] = (" R "," U2"," R'"," U'"," R "," U2"," L'"," U "," R'"," U'"," L ",)
            self.myperms2['Y-Perm'] = (" F "," R "," U'"," R'"," U'"," R "," U "," R'"," F'"," R "," U "," R'"," U'"," R'"," F "," R "," F'")
            self.myperms2['R-Perm'] = (" U "," R2"," F "," R "," U "," R "," U'"," R'"," F'"," R "," U2"," R'"," U2"," R ")
            self.myperms2['V-Perm'] = (" R "," U'"," R "," U "," R'"," D "," R "," D'"," R "," U'"," D "," R2"," U "," R2"," D'"," R2")

    def _register_myperms2_midedge_general(self):
        """奇数サイズ向けのMidEdge系手順を登録する。"""
        if self.size % 2 == 1:           
            self.myperms2['MidEdge3-I-A'] = (' M ', ' D2', " M'", ' D2')
            self.myperms2['MidEdge3-I-B'] = (" U'", " M'", ' U ', ' F2', " U'", ' M ', ' U ', ' F2')
            self.myperms2['MidEdge3-I-C'] = (" F'", " E'", " F'", ' D2', ' F ', ' E ', " F'", ' D2', ' F2')
            self.myperms2['MidEdge3-I-D'] = (' D2', " B'", ' M ', ' B ', ' D2', " B'", " M'", ' B ')

            self.myperms2['MidEdge4-II-A'] = (' M2', ' D2', ' M2', " D'", " M'", " D'", ' B2', ' D ', ' M ', " D'", ' B2')
            self.myperms2['MidEdge4-II-B'] = (" U'", " M'", ' U ', ' F2', " U'", ' M ', ' U ', " M'", " U'", " M'", ' U ', ' F2', " U'", ' M ', " U'", ' M ', ' U2')
            self.myperms2['MidEdge4-II-C'] = (' U2', ' M ', ' U2', ' D2', " B'", ' M ', ' B ', ' D2', " B'", " M'", ' B ', " M'")
            self.myperms2['MidEdge4-II-D'] = (' M ', ' D2', ' B ', ' M ', " B'", ' D2', ' B ', " M'", ' B ', " M'", ' B2')


            self.myperms2['MidEdge4-H-A'] = (" M2"," U "," M2"," U2"," M2"," U "," M2")
            self.myperms2['MidEdge4-H-B'] = (' M2', " U'", ' M ', ' U2', " M'", " U'", ' M ', ' U ', ' B2', " U'", " M'", ' U ', ' B2', " U'", ' M2')
            self.myperms2['MidEdge4-H-C'] = (' S2', " U'", ' S ', ' U2', ' L2', " S'", " U'", ' S ', ' U ', ' L2', " U'", ' S ')
            self.myperms2['MidEdge4-H-D'] = (" M'", ' U ', ' B2', " U'", " M'", ' U ', ' M2', ' B2', ' M2', ' B2', " U'", ' M ', ' U ', ' B2', " U'", ' M ')

            self.myperms2['MidEdge4-T-A'] = (" U'", ' S2', ' U2', ' S2', " U'")
            self.myperms2['MidEdge4-T-B'] = (' D ', ' M ', ' D2', " M'", ' D ', ' M ', " D'", ' F2', ' D ', " M'", " D'", ' F2', ' D ')
            self.myperms2['MidEdge4-T-C'] = (' S ', " U'", ' L2', ' U ', " S'", " U'", ' S ', ' L2', ' U2', " S'", " U'")
            self.myperms2['MidEdge4-T-D'] = (' S ', ' U ', ' L2', " U'", ' S2', ' U ', ' R2', " U'", ' S ', ' U ', ' L2', ' R2', " U'")



            self.myperms2['MidEdge3-U-A'] = (" M2"," U'"," M "," U2"," M'"," U'"," M2")
            self.myperms2['MidEdge3-U-B'] = (" M ", ' U ', " M'", ' U2', ' M ', ' U ', " M'")
            self.myperms2['MidEdge3-U-C'] = (' S2', " U'", ' R2', ' U ', " S'", " U'", ' R2', ' U ', " S'")
            self.myperms2['MidEdge3-U-D'] = (" S'", ' U ', ' L2', " U'", " S'", ' U ', ' L2', " U'", ' S2')

            self.myperms2['MidEdge3-V-A'] = (" D'", ' M ', ' D2', " M'", " D'")
            self.myperms2['MidEdge3-V-B'] = (" M'", ' D ', " M'", ' D2', ' M ', ' D ', ' M ')
            self.myperms2['MidEdge3-V-C'] = (' U ', ' L2', " U'", ' S ', ' U ', ' L2', " U'", " S'")
            self.myperms2['MidEdge3-V-D'] = (" S'", " U'", ' R2', ' U ', ' S ', " U'", ' R2', ' U ')


            self.myperms2['MidEdge4-UU-A'] = (" M'", " U'", ' B2', ' U ', " M'", " U'", ' B2', ' M2', ' U2', ' M2', " U'", ' M2')
            self.myperms2['MidEdge4-UU-B'] = (' M2', " U'", ' M2', ' U2', ' M2', ' B2', " U'", ' M ', ' U ', ' B2', " U'", ' M ')
            self.myperms2['MidEdge4-UU-C'] = (" S'", " U'", ' L2', ' U ', " S'", " U'", ' L2', " S'", ' U2', ' S ', " U'", ' S2')
            self.myperms2['MidEdge4-UU-D'] = (' S2', ' U ', ' R2', " U'", " S'", ' U ', ' R2', " U'", ' S2', ' U ', ' S ', ' U2', " S'", ' U ', ' S ')


            self.myperms2['MidEdge4-VV-A'] = (' M ', " D'", ' F2', ' D ', " M'", " D'", ' F2', ' M2', ' D2', ' M2', " D'")
            self.myperms2['MidEdge4-VV-B'] = (" D'", ' M2', ' D2', ' M2', ' F2', " D'", ' M ', ' D ', ' F2', " D'", " M'")
            self.myperms2['MidEdge4-VV-C'] = (" S'", ' U ', ' R2', " U'", ' S ', ' U ', ' R2', ' S ', ' U2', " S'", ' U ')
            self.myperms2['MidEdge4-VV-D'] = (' S ', " U'", ' S ', ' U2', " S'", " U'", ' S2', ' U ', ' R2', " U'", ' S ', ' U ', ' R2', " U'")

            self.myperms2['MidEdge3-P-A'] = (' S ', ' R ', ' E ', ' R2', " E'", ' R ', " S'")
            self.myperms2['MidEdge3-P-B'] = (" R'"," E "," R2"," E'"," R "," S "," R2"," S'")
            self.myperms2['MidEdge3-P-C'] = (' S ', " L'", ' U2', ' L ', " S'", " L'", ' U2', ' L ')
            self.myperms2['MidEdge3-P-D'] = (" L'", ' U ', " M'", " U'", ' L ', ' U ', ' M ', " U'")
            self.myperms2['MidEdge3-P-E'] = self.invert_moves(self.myperms2['MidEdge3-P-A'])
            self.myperms2['MidEdge3-P-F'] = self.invert_moves(self.myperms2['MidEdge3-P-B'])
            self.myperms2['MidEdge3-P-G'] = self.invert_moves(self.myperms2['MidEdge3-P-C'])
            self.myperms2['MidEdge3-P-H'] = self.invert_moves(self.myperms2['MidEdge3-P-D'])

            self.myperms2['MidEdge3-R-A'] = (' L2', " D'", ' M ', ' D2', " M'", " D'", ' L2')
            self.myperms2['MidEdge3-R-B'] = (' S2', ' R ', ' F ', " R'", ' S2', ' R ', " F'", " R'")
            self.myperms2['MidEdge3-R-C'] = (' L2', ' U ', ' L2', " U'", ' S ', ' U ', ' L2', " U'", " S'", ' L2')
            self.myperms2['MidEdge3-R-D'] = (" D'", ' M ', " D'", " S'", ' D2', ' S ', " D'", " M'", ' D ')
            self.myperms2['MidEdge3-R-E'] = self.invert_moves(self.myperms2['MidEdge3-R-A'])
            self.myperms2['MidEdge3-R-F'] = self.invert_moves(self.myperms2['MidEdge3-R-B'])
            self.myperms2['MidEdge3-R-G'] = self.invert_moves(self.myperms2['MidEdge3-R-C'])
            self.myperms2['MidEdge3-R-H'] = self.invert_moves(self.myperms2['MidEdge3-R-D'])


            self.myperms2['MidEdge3-N-A'] = (" R "," M2"," U'"," M "," U2"," M'"," U'"," M2"," R'")
            self.myperms2['MidEdge3-N-B'] = (" R'", ' S2', ' R ', ' F ', " R'", ' S2', ' R ', " F'")
            self.myperms2['MidEdge3-N-C'] = (' R ', ' S ', " R'", ' F ', ' R ', " S'", " R'", " F'")
            self.myperms2['MidEdge3-N-D'] = (' E ', " L'", ' B ', " M'", ' B2', ' M ', ' B ', ' L ', " E'")

            
            self.myperms2['MidEdge3-Q-A'] = (' U ', ' L ', ' E2', " L'", " U'", ' L ', ' E2', " L'")
            self.myperms2['MidEdge3-Q-B'] = (" L'", ' B ', " M'", ' B2', ' M ', ' B ', ' L ')
            self.myperms2['MidEdge3-Q-C'] = (" F'", ' E2', ' F ', " U'", " F'", ' E2', ' F ', ' U ')
            self.myperms2['MidEdge3-Q-D'] = (" S'", ' R ', " D'", ' M ', ' D2', " M'", " D'", " R'", ' S ')


            self.myperms2['MidEdge3-Y-A'] = (" S2"," L'"," E "," R "," U'"," R'"," E'"," R "," U "," R'"," L "," S2")
            self.myperms2['MidEdge3-Y-B'] = (' E2', ' R ', " B'", " M'", ' B2', ' M ', " B'", " R'", ' E2')
            self.myperms2['MidEdge3-O-A'] = (" R'", ' S ', ' D ', ' R2', " D'", " S'", ' D ', ' R2', " D'", ' R ')
            self.myperms2['MidEdge3-O-B'] = (' B ', " L'", ' S ', ' L2', " S'", " L'", " B'")


            self.myperms2['MidEdge4-Z-A'] = (" M2"," U'"," F2"," M2"," F2"," M2"," U "," M2")
            self.myperms2['MidEdge4-Z-B'] = (' M2', ' U ', ' M ', ' U2', " M'", ' U ', " M'", " U'", ' F2', ' U ', ' M ', " U'", ' F2', ' U ', ' M2')
            self.myperms2['MidEdge4-Z-C'] = (' M2', " U'", " M'", ' F2', ' U2', ' M ', " U'", " M'", " U'", ' F2', ' U ', " M'")
            self.myperms2['MidEdge4-Z-D'] = (' M2', " U'", " M'", ' U2', ' M ', " U'", " M'", " U'", " M'", ' U2', ' M ', " U'", " M'")
            self.myperms2['MidEdge4-Z-E'] = (" S'", " U'", ' S ', ' U2', " S'", " U'", ' S2', ' U ', " S'", ' U2', ' S ', ' U ', " S'")


            self.myperms2['MidEdge4-S-A'] = (" D'"," F2"," M2"," F2"," M2"," D ")
            self.myperms2['MidEdge4-S-B'] = (' D ', ' M ', ' D2', " M'", ' D ', " M'", " D'", ' B2', ' D ', ' M ', " D'", ' B2', ' D ')
            self.myperms2['MidEdge4-S-C'] = (' U ', ' S ', ' U2', " S'", ' U ', " M'", ' D ', " M'", ' D2', ' M ', ' D ', ' M ')
            self.myperms2['MidEdge4-S-D'] = (" M'", ' D ', " M'", ' D2', ' M2', ' B2', " M'", ' D ', ' M ', " D'", ' B2', ' D ')
            self.myperms2['MidEdge4-S-E'] = (" M'", ' D ', " M'", ' D2', ' M ', ' D ', ' M2', " D'", ' M ', ' D2', " M'", " D'", " M'")


            self.myperms2['MidEdge4-F-A'] = (" M2"," U2"," M2"," U2")
            self.myperms2['MidEdge4-F-B'] = (' M ', ' D2', ' B ', ' M ', " B'", ' D2', ' B ', " M'", " B'", ' D2', " M'", ' D2')
            self.myperms2['MidEdge4-F-C'] = (' D2', ' M ', " B'", ' M ', ' B ', ' D2', " B'", " M'", ' B ', ' F2', " M'", ' F2')
            self.myperms2['MidEdge4-F-D'] = (" M'", " B'", " M'", ' B ', ' U2', " B'", ' M ', ' B ', ' F2', ' M ', ' F2', ' U2')
            self.myperms2['MidEdge4-F-E'] = (' F2', " D'", ' M ', ' D ', ' F2', " D'", " M'", ' D ', ' U ', " M'", " U'", ' F2', ' U ', ' M ', " U'", ' F2')        

            self.myperms2['MidEdge4-X-A'] = (" F2"," M2"," U2"," M2"," U2"," F2")
            self.myperms2['MidEdge4-X-B'] = (" F'", " M'", ' F ', ' D2', " F'", ' M ', ' F ', ' D2', ' M ', ' D2', " M'", ' D2')
            self.myperms2['MidEdge4-X-C'] = (" M'", ' F2', ' U ', " M'", " U'", ' F2', ' U ', ' M ', " U'", ' B2', ' M ', ' B2')
            self.myperms2['MidEdge4-X-D'] = (' B ', ' M ', " B'", ' D2', ' B ', " M'", " B'", ' F ', " M'", " F'", ' D2', ' F ', ' M ', " F'")
        

            self.myperms2['MidEdge4-B-A'] = (' L2', " D'", " M'", ' D2', ' M ', " D'", ' L2', ' R2', " U'", " M'", ' U2', ' M ', " U'", ' R2')
            self.myperms2['MidEdge4-B-B'] = (" U'", " M'", ' U2', ' M ', " U'", " S'", ' U2', ' S ', ' U2', ' M ', ' U ', ' B2', " U'", ' M ', ' U ', " M'", ' B2', ' U2', ' M ', ' U ', ' M2')
            self.myperms2['MidEdge4-B-C'] = (' M ', " U'", " S'", ' U2', ' S ', " U'", ' B2', " M'", ' B2', ' L2', " D'", " M'", ' D2', ' M ', " D'", ' L2')
            self.myperms2['MidEdge4-B-D'] = (" M'", " U'", " S'", ' U2', ' S ', ' U ', ' M ', ' U2', ' S2', " U'", " S'", ' U2', ' S ', " U'", ' S2')
            self.myperms2['MidEdge4-B-E'] = (" M'", " D'", ' M ', ' D2', " M'", " D'", ' M ', " S'", " D'", " M'", ' D2', ' M ', ' D ', ' S ', ' D2')
            
            self.myperms2['MidEdge4-C-A'] = (' U ', " M'", ' U2', ' M ', ' U ', ' S2', ' D2', ' S2', " D'", " M'", ' D2', ' M ', ' D ')
            self.myperms2['MidEdge4-C-B'] = (' L2', ' D ', ' R2', " D'", ' S ', ' D ', ' R2', " D'", " S'", ' L2', " U'", ' S ', ' U2', " S'", " U'", " M'", ' U2', ' M ', ' U2')
            self.myperms2['MidEdge4-C-C'] = (' S ', ' U ', " S'", ' U2', ' S ', ' U ', " S'", " M'", ' U2', ' M ', ' U2', ' R2', " D'", " M'", ' D2', ' M ', " D'", ' R2')
            self.myperms2['MidEdge4-C-D'] = (' M ', " D'", ' S ', ' D2', " S'", " D'", ' F2', " M'", ' U ', ' S ', ' U2', " S'", ' U ', ' F2')
            self.myperms2['MidEdge4-C-E'] = (" S'", " D'", " S'", ' D2', ' S ', " D'", ' U ', " S'", ' U2', ' S ', ' U ', ' S ', ' M2', ' D2', ' M2', ' D2')

            self.myperms2['MidEdge4-A-A'] = (" S'", ' U2', ' S ', ' U2', ' M ', " U'", ' M2', ' U2', ' M2', " U'", " M'")
            self.myperms2['MidEdge4-A-B'] = (' S2', " D'", ' L2', ' D ', ' S ', " D'", ' L2', ' D ', ' S ', " M'", " U'", " S'", ' U2', ' S ', " U'", ' M ')
            self.myperms2['MidEdge4-A-C'] = (" D2"," L2"," B2",' S2', " U'", ' S ', ' U2', ' L2', " S'", " U'", ' S ', ' U ', ' L2', " U'", ' S '," B2"," L2"," D2")
            self.myperms2['MidEdge4-A-D'] = (" S'", ' U2', ' S ', ' U2', ' S2', ' U ', ' S2', ' U2', ' S2', ' U ', ' S2', ' B ', " M'", " B'", ' U2', ' B ', ' M ', " B'", ' U2')
            self.myperms2['MidEdge4-A-E'] = (" D2"," L2"," B2"," M'", ' U ', ' B2', " U'", " M'", ' U ', ' M2', ' B2', ' M2', ' B2', " U'", ' M ', ' U ', ' B2', " U'", ' M '," B2"," L2"," D2")

            self.myperms2['MidEdge4-D-A'] = (" L2"," B2"," M2"," U "," M2"," U2"," M2"," U "," M2"," B2"," L2")
            self.myperms2['MidEdge4-D-B'] = (" L2"," B2",' S2', " U'", ' S ', ' U2', ' L2', " S'", " U'", ' S ', ' U ', ' L2', " U'", ' S '," B2"," L2", " S'", ' R ', " S'", " R'", ' D2', ' R ', ' S ', ' R ', ' S ', ' R2', ' D2')
            self.myperms2['MidEdge4-D-C'] = (" L2"," B2",' S2', " U'", ' S ', ' U2', ' L2', " S'", " U'", ' S ', ' U ', ' L2', " U'", ' S '," B2"," L2")
            self.myperms2['MidEdge4-D-D'] = (" L2"," B2",' M2', " U'", ' M ', ' U2', " M'", " U'", ' M ', ' U ', ' B2', " U'", " M'", ' U ', ' B2', " U'", ' M2'," B2"," L2")
            self.myperms2['MidEdge4-D-E'] = (" L2"," B2"," M'", ' U ', ' B2', " U'", " M'", ' U ', ' M2', ' B2', ' M2', ' B2', " U'", ' M ', ' U ', ' B2', " U'", ' M '," B2"," L2")

            

            self.myperms2['MidEdgeFlip-A2'] = (' U2', " M'", ' U ', " M'", ' U ', ' F2', " U'", " M ", ' U ', " M ", ' F2')
            self.myperms2['MidEdgeFlip-B2'] = (' M ', ' U ', " M'", ' U2', ' B2', ' M ', ' U ', ' M ', " U'", ' B2', ' U ', ' M2')
            self.myperms2['MidEdgeFlip-C2'] = (' E ', ' F ', ' E ', ' F2', ' R2', " E'", ' F ', " E'", " F'", ' R2', ' F ')
            self.myperms2['MidEdgeFlip-D2'] = (' E ', ' R ', ' E ', " R'", ' F2', ' R ', " E'", ' R ', " E'", ' R2', ' F2')
            self.myperms2['MidEdgeFlip-E4'] = (' M ', ' D ', " M'", ' D2', ' M ', ' D ', " M'", ' S2', ' D ', ' S ', ' D2', " S'", ' L2', ' D ', " S'", " D'", ' L2', ' D ', " S'")
            self.myperms2['MidEdgeFlip-F4'] = (' F2', " M'", " F'", " M'", " F'", ' D2', ' F ', ' M ', " F'", ' M2', " B'", ' M ', ' B ', ' D2', " B'", " M'", " B'", " M'", ' B2')
            self.myperms2['MidEdgeFlip-G4'] = (" M'", " U'", " M'", ' U2', ' M ', " U'", ' M2', ' U ', ' B2', " U'", " M'", ' U ', ' B2', ' M ', ' D2', " M'", ' D2', " U'")

            self.myperms2['MidEdgeFlip-A2I'] = self.invert_moves(self.myperms2['MidEdgeFlip-A2'])
            self.myperms2['MidEdgeFlip-B2I'] = self.invert_moves(self.myperms2['MidEdgeFlip-B2'])
            self.myperms2['MidEdgeFlip-C2I'] = self.invert_moves(self.myperms2['MidEdgeFlip-C2'])
            self.myperms2['MidEdgeFlip-D2I'] = self.invert_moves(self.myperms2['MidEdgeFlip-D2'])
            self.myperms2['MidEdgeFlip-E4I'] = self.invert_moves(self.myperms2['MidEdgeFlip-E4'])
            self.myperms2['MidEdgeFlip-F4I'] = self.invert_moves(self.myperms2['MidEdgeFlip-F4'])
            self.myperms2['MidEdgeFlip-G4I'] = self.invert_moves(self.myperms2['MidEdgeFlip-G4'])
            








            

    def _register_myperms2_edge_general(self):
        """4x4以上で使うEdge系・派生手順を登録する。"""
        if self.size >= 4:
            






            
        

            self.myperms2['Wing3-Parallel-I00-'] = (" U2", ' B2', ' U ', "2B'", " U'", ' B2', ' U ', '2B ', " U ")
            self.myperms2['Wing3-Parallel-I01-'] = self.invert_moves(self.myperms2['Wing3-Parallel-I00-'])
            self.myperms2['Wing3-Parallel-I02-'] = (" U2", ' B2', " U'", "2F'", ' U ', ' B2', " U'", '2F ', " U'")
            self.myperms2['Wing3-Parallel-I03-'] = self.invert_moves(self.myperms2['Wing3-Parallel-I02-'])

            

            

            self.myperms2['Wing3-Parallel-J00-'] = (' B2', ' U ', "2B'", " U'", ' B2', ' U ', '2B ', " U'")
            self.myperms2['Wing3-Parallel-J01-'] = self.invert_moves(self.myperms2['Wing3-Parallel-J00-'])
            self.myperms2['Wing3-Parallel-J02-'] = (' B2', " U'", "2F'", ' U ', ' B2', " U'", '2F ', ' U ')
            self.myperms2['Wing3-Parallel-J03-'] = self.invert_moves(self.myperms2['Wing3-Parallel-J02-'])
            self.myperms2['Wing3-Parallel-J04-'] = (" B'", '2D ', " F'", "2D'", ' B2', '2D ', ' F ', "2D'", " B'")
            self.myperms2['Wing3-Parallel-J05-'] = self.invert_moves(self.myperms2['Wing3-Parallel-J04-'])
            self.myperms2['Wing3-Parallel-J06-'] = (' B ', '2U ', ' F ', "2U'", ' B2', '2U ', " F'", "2U'", ' B ')
            self.myperms2['Wing3-Parallel-J07-'] = self.invert_moves(self.myperms2['Wing3-Parallel-J06-'])
 
            


            self.myperms2['Wing3-Parallel-K00-'] = ("2F "," L2","2F'", ' L ', '2D ', " L'", ' U2', ' L ', "2D'", " L'", ' U2', '2F '," L2","2F'")
            self.myperms2['Wing3-Parallel-K01-'] = ("2F "," L2","2F'", ' U2', ' L ', '2D ', " L'", ' U2', ' L ', "2D'", " L'", '2F '," L2","2F'")
            self.myperms2['Wing3-Parallel-K02-'] = ("2F "," L2","2F'", " L'", '2U ', ' L ', ' U2', " L'", "2U'", ' L ', ' U2', '2F '," L2","2F'")
            self.myperms2['Wing3-Parallel-K03-'] = ("2F "," L2","2F'", ' U2', " L'", '2U ', ' L ', ' U2', " L'", "2U'", ' L ', '2F '," L2","2F'")
            self.myperms2['Wing3-Parallel-K04-'] = ("2F "," R2",'2F2', ' R2', " D'", "2L'", ' D ', ' R2', " D'", '2L ', ' D ', '2F2'," R2","2F'")
            self.myperms2['Wing3-Parallel-K05-'] = ("2F "," R2",'2F2', " D'", "2L'", ' D ', ' R2', " D'", '2L ', ' D ', ' R2', '2F2'," R2","2F'")
            self.myperms2['Wing3-Parallel-K06-'] = ("2F "," R2",'2F2', ' R2', ' D ', "2R'", " D'", ' R2', ' D ', '2R ', " D'", '2F2'," R2","2F'")
            self.myperms2['Wing3-Parallel-K07-'] = ("2F "," R2",'2F2', ' D ', "2R'", " D'", ' R2', ' D ', '2R ', " D'", ' R2', '2F2'," R2","2F'")
            self.myperms2['Wing3-Parallel-K08-'] = ("2B "," R2",'2B2', ' R2', ' D ', '2L ', " D'", ' R2', ' D ', "2L'", " D'", '2B2'," R2","2B'")
            self.myperms2['Wing3-Parallel-K09-'] = ("2B "," R2",'2B2', ' D ', '2L ', " D'", ' R2', ' D ', "2L'", " D'", ' R2', '2B2'," R2","2B'")







##            self.myperms2['EdgePA00-'] = ("2L'", ' U ', ' R ', " U'", '2L ', ' U ', " R'", " U'")
##            self.myperms2['EdgePA01-'] = self.invert_moves(self.myperms2['EdgePA00-'])
##            self.myperms2['EdgePA02-'] = ("2L'", " U'", " L'", ' U ', '2L ', " U'", ' L ', ' U ')
##            self.myperms2['EdgePA03-'] = self.invert_moves(self.myperms2['EdgePA02-'])
##            self.myperms2['EdgePA04-'] = ('2L ', " U'", ' R ', ' U ', "2L'", " U'", " R'", ' U ')            
##            self.myperms2['EdgePA05-'] = self.invert_moves(self.myperms2['EdgePA04-'])
##            self.myperms2['EdgePA06-'] = ('2L ', ' U ', " L'", " U'", "2L'", ' U ', ' L ', " U'")
##            self.myperms2['EdgePA07-'] = self.invert_moves(self.myperms2['EdgePA06-'])

            self.myperms2['Wing3-Parallel2Plus1-B00-'] = (' U2', " B'", "2U'", ' B ', ' U2', " B'", '2U ', ' B ')
            self.myperms2['Wing3-Parallel2Plus1-B01-'] = self.invert_moves(self.myperms2['Wing3-Parallel2Plus1-B00-'])            
            self.myperms2['Wing3-Parallel2Plus1-B02-'] = (' U2', " B ", "2D'", " B'", ' U2', " B ", "2D ", " B'")
            self.myperms2['Wing3-Parallel2Plus1-B03-'] = self.invert_moves(self.myperms2['Wing3-Parallel2Plus1-B02-'])  
            self.myperms2['Wing3-Parallel2Plus1-B04-'] = (' U2', ' B ', '2D2', " B'", ' U2', ' B ', '2D2', " B'")
            self.myperms2['Wing3-Parallel2Plus1-B05-'] = self.invert_moves(self.myperms2['Wing3-Parallel2Plus1-B04-'])
            self.myperms2['Wing3-Parallel2Plus1-B06-'] = (' U2', " B'", '2U2', " B ", ' U2', " B'", '2U2', " B ")
            self.myperms2['Wing3-Parallel2Plus1-B07-'] = self.invert_moves(self.myperms2['Wing3-Parallel2Plus1-B06-'])



            self.myperms2['Wing3-U00-'] = (" B'", ' R ', ' B ', "2L'", " B'", " R'", ' B ', '2L ')
            self.myperms2['Wing3-U01-'] = self.invert_moves(self.myperms2['Wing3-U00-'])
            self.myperms2['Wing3-U02-'] = (' B ', " L'", " B'", "2L'", ' B ', ' L ', " B'", '2L ')
            self.myperms2['Wing3-U03-'] = self.invert_moves(self.myperms2['Wing3-U02-'])


            self.myperms2['Wing3-V00-'] = (' F ', ' R ', " F'", '2L ', ' F ', " R'", " F'", "2L'")
            self.myperms2['Wing3-V01-'] = self.invert_moves(self.myperms2['Wing3-V00-'])
            self.myperms2['Wing3-V02-'] = (" F'", " L'", ' F ', '2L ', " F'", ' L ', ' F ', "2L'")
            self.myperms2['Wing3-V03-'] = self.invert_moves(self.myperms2['Wing3-V02-'])
            

            self.myperms2['Wing3-U07A-'] = ('2R2', ' B2', ' D ', '2B ', " D'", ' B2', ' D ', "2B'", " D'", '2R2')
            self.myperms2['Wing3-U06A-'] = ('2R2', ' D ', '2B ', " D'", ' B2', ' D ', "2B'", " D'", ' B2', '2R2')
            self.myperms2['Wing3-U06B-'] = ('2R2', ' B2', " D'", '2F ', ' D ', ' B2', " D'", "2F'", ' D ', '2R2')
            self.myperms2['Wing3-U07B-'] = ('2R2', " D'", '2F ', ' D ', ' B2', " D'", "2F'", ' D ', ' B2', '2R2')
            self.myperms2['Wing3-U04A-'] = ('2R2', ' B2', " D'", '2F2', ' D ', ' B2', " D'", '2F2', ' D ', '2R2')
            self.myperms2['Wing3-U05A-'] = ('2R2', " D'", '2F2', ' D ', ' B2', " D'", '2F2', ' D ', ' B2', '2R2')
            self.myperms2['Wing3-U05B-'] = ('2R2', ' B2', ' D ', '2B2', " D'", ' B2', ' D ', '2B2', " D'", '2R2')
            self.myperms2['Wing3-U04B-'] = ('2R2', ' D ', '2B2', " D'", ' B2', ' D ', '2B2', " D'", ' B2', '2R2')

            self.myperms2['Wing3-V07A-'] = ('2L2', ' F2', ' U ', '2F ', " U'", ' F2', ' U ', "2F'", " U'", '2L2')
            self.myperms2['Wing3-V06A-'] = ('2L2', ' U ', '2F ', " U'", ' F2', ' U ', "2F'", " U'", ' F2', '2L2')
            self.myperms2['Wing3-V06B-'] = ('2L2', ' F2', " U'", '2B ', ' U ', ' F2', " U'", "2B'", ' U ', '2L2')
            self.myperms2['Wing3-V07B-'] = ('2L2', " U'", '2B ', ' U ', ' F2', " U'", "2B'", ' U ', ' F2', '2L2')
            self.myperms2['Wing3-V04A-'] = ('2L2', ' F2', " U'", '2B2', ' U ', ' F2', " U'", '2B2', ' U ', '2L2')
            self.myperms2['Wing3-V05A-'] = ('2L2', " U'", '2B2', ' U ', ' F2', " U'", '2B2', ' U ', ' F2', '2L2')
            self.myperms2['Wing3-V05B-'] = ('2L2', ' F2', ' U ', '2F2', " U'", ' F2', ' U ', '2F2', " U'", '2L2')
            self.myperms2['Wing3-V04B-'] = ('2L2', ' U ', '2F2', " U'", ' F2', ' U ', '2F2', " U'", ' F2', '2L2')


            self.myperms2['Wing3-Parallel2Plus1-I00-'] = (' B ', ' L2', " B'", '2L2', ' B ', ' L2', " B'", '2L2')
            self.myperms2['Wing3-Parallel2Plus1-I01-'] = ('2L2', ' B ', ' L2', " B'", '2L2', ' B ', ' L2', " B'")
            self.myperms2['Wing3-Parallel2Plus1-I02-'] = (" B'", ' R2', ' B ', '2L2', " B'", ' R2', ' B ', '2L2')
            self.myperms2['Wing3-Parallel2Plus1-I03-'] = ('2L2', " B'", ' R2', ' B ', '2L2', " B'", ' R2', ' B ')
            self.myperms2['Wing3-Parallel2Plus1-I04-'] = (" U'", " L'", ' U ', '2L2', " U'", ' L ', ' U ', '2L2')
            self.myperms2['Wing3-Parallel2Plus1-I05-'] = ('2L2', " U'", " L'", ' U ', '2L2', " U'", ' L ', ' U ')            
            self.myperms2['Wing3-Parallel2Plus1-I06-'] = (' U ', ' R ', " U'", '2L2', ' U ', " R'", " U'", '2L2')
            self.myperms2['Wing3-Parallel2Plus1-I07-'] = ('2L2', ' U ', ' R ', " U'", '2L2', ' U ', " R'", " U'")                

            self.myperms2['Wing3-Parallel2Plus1-I04B-'] = ('2L2', " D'", ' L ', ' D ', '2L2', " D'", " L'", ' D ')
            self.myperms2['Wing3-Parallel2Plus1-I05B-'] = (" D'", ' L ', ' D ', '2L2', " D'", " L'", ' D ', '2L2')            
            self.myperms2['Wing3-Parallel2Plus1-I06B-'] = ('2L2', ' D ', " R'", " D'", '2L2', ' D ', ' R ', " D'")
            self.myperms2['Wing3-Parallel2Plus1-I07B-'] = (' D ', " R'", " D'", '2L2', ' D ', ' R ', " D'", '2L2')

            self.myperms2['Wing3-Parallel2Plus1-I00C-'] = (" B'", '2U2', " B'", ' D2', ' B ', '2U2', " B'", ' D2', ' B2')
            self.myperms2['Wing3-Parallel2Plus1-I01C-'] = (' B2', ' D2', ' B ', "2U2", " B'", ' D2', ' B ', '2U2', ' B ')
            self.myperms2['Wing3-Parallel2Plus1-I02C-'] = (' B ', '2D2', ' B ', ' D2', " B'", '2D2', ' B ', ' D2', ' B2')
            self.myperms2['Wing3-Parallel2Plus1-I03C-'] = (' B2', ' D2', " B'", "2D2", ' B ', ' D2', " B'", '2D2', " B'")
            self.myperms2['Wing3-Parallel2Plus1-I04C-'] = (' B ', "2D'", ' B ', ' D2', " B'", '2D ', ' B ', ' D2', ' B2')
            self.myperms2['Wing3-Parallel2Plus1-I05C-'] = (' B2', ' D2', " B'", "2D'", ' B ', ' D2', " B'", '2D ', " B'")
            self.myperms2['Wing3-Parallel2Plus1-I06C-'] = (" B'", "2U'", " B'", ' D2', ' B ', '2U ', " B'", ' D2', ' B2')
            self.myperms2['Wing3-Parallel2Plus1-I07C-'] = (' B2', ' D2', ' B ', "2U'", " B'", ' D2', ' B ', '2U ', ' B ')



            self.myperms2['Wing3-O00-'] = (" F'", '2L2', " F'", ' R ', ' F ', '2L2', " F'", " R'", ' F2')
            self.myperms2['Wing3-O01-'] = (" F'", '2R2', " F'", ' R ', ' F ', '2R2', " F'", " R'", ' F2')
            self.myperms2['Wing3-O02-'] = (' D ', "2L'", " B'", ' L2', ' B ', '2L ', " B'", ' L2', ' B ', " D'")
            self.myperms2['Wing3-O03-'] = (' D ', '2R ', " B'", ' L2', ' B ', "2R'", " B'", ' L2', ' B ', " D'")

            self.myperms2['Wing3-Y00-'] = (" R'", " D'", '2L ', ' D ', " R'", " D'", "2L'", ' D ', ' R2')
            self.myperms2['Wing3-Y01-'] = (" R'", " D'", "2R'", ' D ', " R'", " D'", '2R ', ' D ', ' R2')
            self.myperms2['Wing3-Y00B-'] = (" F'", ' L ', '2B2', " L'", " F'", ' L ', '2B2', " L'", ' F2')
            self.myperms2['Wing3-Y01B-'] = (" F'", ' L ', '2F2', " L'", " F'", ' L ', '2F2', " L'", ' F2')
            self.myperms2['Wing3-Y02-'] = (' R ', ' U ', " F'", '2U2', ' F ', " U'", " F'", '2U2', ' F ', " R'")       
            self.myperms2['Wing3-Y03-'] = (' R ', ' U ', " F'", '2D2', ' F ', " U'", " F'", '2D2', ' F ', " R'")


            self.myperms2['Wing3-N00-'] = (' U ', ' L ', '2U ', " L'", " U'", ' L ', "2U'", " L'")
            self.myperms2['Wing3-N01-'] = (" L ", "2U ", " L'", " U ", " L ", "2U'", " L'", " U'")
            self.myperms2['Wing3-N00B-'] = (' R ', "2B'", " R'", ' F ', ' R ', '2B ', " R'", " F'")
            self.myperms2['Wing3-N01B-'] = (' F ', ' R ', "2B'", " R'", " F'", ' R ', '2B ', " R'")
            self.myperms2['Wing3-N02-'] = (" L'", '2D2', ' L ', ' U ', " L'", '2D2', ' L ', " U'")
            self.myperms2['Wing3-N03-'] = (' U ', " L'", '2D2', ' L ', " U'", " L'", '2D2', ' L ')
            self.myperms2['Wing3-N04-'] = (" L'", '2U2', ' L ', ' U ', " L'", '2U2', ' L ', " U'")
            self.myperms2['Wing3-N05-'] = (' U ', " L'", '2U2', ' L ', " U'", " L'", '2U2', ' L ')
            self.myperms2['Wing3-N06-'] = (" L'", " B'", ' U2', " B'", "2U'", ' B ', ' U2', " B'", '2U ', ' B2', ' L ')
            self.myperms2['Wing3-N07-'] = (" L'", ' B2', "2U'", ' B ', ' U2', " B'", '2U ', ' B ', ' U2', ' B ', ' L ')
            self.myperms2['Wing3-N06B-'] = (" R'", ' D2', '2B ', ' D ', ' F2', " D'", "2B'", ' D ', ' F2', ' D ', ' R ')
            self.myperms2['Wing3-N07B-'] = (" R'", " D'", ' F2', " D'", '2B ', ' D ', ' F2', " D'", "2B'", ' D2', ' R ')




            self.myperms2['Wing3-Q00-'] = (" R'", "2F'", ' R ', ' F ', " R'", '2F ', ' R ', " F'")
            self.myperms2['Wing3-Q01-'] = (' F ', " R'", "2F'", ' R ', " F'", " R'", '2F ', ' R ')
            self.myperms2['Wing3-Q02-'] = (' L ', "2B'", " L'", " F'", ' L ', '2B ', " L'", ' F ')
            self.myperms2['Wing3-Q03-'] = (" F'", ' L ', "2B'", " L'", ' F ', ' L ', '2B ', " L'")
            self.myperms2['Wing3-Q00B-'] = (" F'", " U'", '2F2', ' U ', ' F ', " U'", '2F2', ' U ')
            self.myperms2['Wing3-Q01B-'] = (" U'", '2F2', ' U ', " F'", " U'", '2F2', ' U ', ' F ')
            self.myperms2['Wing3-Q02B-'] = (' F ', ' U ', '2B2', " U'", " F'", ' U ', '2B2', " U'")
            self.myperms2['Wing3-Q03B-'] = (' U ', '2B2', " U'", ' F ', ' U ', '2B2', " U'", " F'")
            self.myperms2['Wing3-Q04-'] = (' L ', '2D2', ' L ', ' U ', " L'", '2D2', ' L ', " U'", ' L2')
            self.myperms2['Wing3-Q05-'] = (" R'", '2U2', " R'", " U'", ' R ', '2U2', " R'", ' U ', ' R2')
            self.myperms2['Wing3-Q06-'] = (" R'", "2F'", " D'", ' F2', ' D ', '2F ', " D'", ' F2', ' D ', ' R ')
            self.myperms2['Wing3-Q07-'] = (' L ', "2B'", ' D ', ' F2', " D'", '2B ', ' D ', ' F2', " D'", " L'")

            self.myperms2['Wing3-Parallel2Plus1-A00-'] = ("2U'", " B'", '2U ', ' F ', "2U'", ' B ', '2U ', " F'")
            self.myperms2['Wing3-Parallel2Plus1-A01-'] = ("2D'", ' B ', '2D ', " F'", "2D'", " B'", '2D ', ' F ')
            self.myperms2['Wing3-Parallel2Plus1-A02-'] = ("2U ", " B'", '2U ', ' F ', "2U'", ' B ', '2U ', " F'", "2U2")
            self.myperms2['Wing3-Parallel2Plus1-A03-'] = ("2D ", ' B ', '2D ', " F'", "2D'", " B'", '2D ', ' F ', "2D2")
            self.myperms2['Wing3-Parallel2Plus1-A04-'] = self.invert_moves(self.myperms2['Wing3-Parallel2Plus1-A00-'])
            self.myperms2['Wing3-Parallel2Plus1-A05-'] = self.invert_moves(self.myperms2['Wing3-Parallel2Plus1-A01-'])
            self.myperms2['Wing3-Parallel2Plus1-A06-'] = self.invert_moves(self.myperms2['Wing3-Parallel2Plus1-A02-'])
            self.myperms2['Wing3-Parallel2Plus1-A07-'] = self.invert_moves(self.myperms2['Wing3-Parallel2Plus1-A03-'])
            self.myperms2['Wing3-Parallel2Plus1-J00-'] = ('2U ', " B'", "2U'", " F'", '2U ', ' B ', "2U'", ' F ')
            self.myperms2['Wing3-Parallel2Plus1-J01-'] = ('2D ', ' B ', "2D'", ' F ', '2D ', " B'", "2D'", " F'")
            self.myperms2['Wing3-Parallel2Plus1-J02-'] = ("2U'", " B'", "2U'", " F'", '2U ', ' B ', "2U'", ' F ', "2U2")
            self.myperms2['Wing3-Parallel2Plus1-J03-'] = ("2D'", ' B ', "2D'", ' F ', '2D ', " B'", "2D'", " F'", "2D2")
            self.myperms2['Wing3-Parallel2Plus1-J04-'] = self.invert_moves(self.myperms2['Wing3-Parallel2Plus1-J00-'])
            self.myperms2['Wing3-Parallel2Plus1-J05-'] = self.invert_moves(self.myperms2['Wing3-Parallel2Plus1-J01-'])
            self.myperms2['Wing3-Parallel2Plus1-J06-'] = self.invert_moves(self.myperms2['Wing3-Parallel2Plus1-J02-'])
            self.myperms2['Wing3-Parallel2Plus1-J07-'] = self.invert_moves(self.myperms2['Wing3-Parallel2Plus1-J03-'])


            self.myperms2['Wing3-SameEdgePairPlus1-K00-'] = ('2R2', "2U'", ' B ', '2U ', ' F ', "2U'", " B'", '2U ', " F'", '2R2')
            self.myperms2['Wing3-SameEdgePairPlus1-K01-'] = ('2R2', "2D'", " B'", '2D ', " F'", "2D'", ' B ', '2D ', ' F ', '2R2')
            self.myperms2['Wing3-SameEdgePairPlus1-K02-'] = ('2R2', ' F ', "2U'", ' B ', '2U ', " F'", "2U'", " B'", '2U ', '2R2')
            self.myperms2['Wing3-SameEdgePairPlus1-K03-'] = ('2R2', " F'", "2D'", " B'", '2D ', ' F ', "2D'", ' B ', '2D ', '2R2')
            self.myperms2['Wing3-SameEdgePairPlus1-K04-'] = ('2R2', "2D'", ' B ', '2D ', ' F ', "2D'", " B'", '2D ', " F'", '2R2')
            self.myperms2['Wing3-SameEdgePairPlus1-K05-'] = ('2R2', "2U'", " B'", '2U ', " F'", "2U'", ' B ', '2U ', ' F ', '2R2')
            self.myperms2['Wing3-SameEdgePairPlus1-K06-'] = ('2R2', ' F ', "2D'", ' B ', '2D ', " F'", "2D'", " B'", '2D ', '2R2')
            self.myperms2['Wing3-SameEdgePairPlus1-K07-'] = ('2R2', " F'", "2U'", " B'", '2U ', ' F ', "2U'", ' B ', '2U ', '2R2')

            
            self.myperms2['L2NA-'] = ('2F2', ' R2', "2F'", ' U2', "2F'", ' U2', ' R2', "2F'", ' R2', '2F ', ' R2', "2F'", ' R2', '2F2', ' R2')
            self.myperms2['L2NA1-'] = ('2B2', ' D2', '2F ', ' U2', '2B ', ' L2', "2F'", ' L2', ' U2', "2B'", ' R2', '2F ', ' R2', ' D2', '2B2')
            self.myperms2['L2NA2-'] = ('2B2', ' D2', ' R2', "2F'", ' R2', '2B ', ' U2', ' L2', '2F ', ' L2', "2B'", ' U2', "2F'", ' D2', '2B2')
            self.myperms2['L2OA-'] = ('2B2', ' U2', "2B'", ' U2', ' D2', '2F ', ' D2', ' U2', "2B'", ' U2', '2B2')
            self.myperms2['L2ZA-'] = ("2F'", ' U2', "2F'", ' U2', ' R2', "2F'", ' R2', "2F'", ' L2', '2B2', ' L2', '2F ', ' U2', '2F2', ' U2')

            self.myperms2['L2E-NB0-'] = ('2F ', " D'", '2L ', ' D ', ' R2', " D'", "2L'", ' D ', ' R2', '2F ', ' D ', '2R2', " D'", ' R2', ' D ', '2R2', ' D ', '2F ', ' D2', '2F2', ' R2', '2B ', ' U2', '2F2', ' U2', ' R2', "2B'", ' R2')
            self.myperms2['L2E-OB0-'] = (" R "," B ","2R'"," U2","2R'"," U2"," B2","2R'"," B2","2R'"," F2","2L2"," F2","2R "," U2","2R2"," U2"," B'"," R'")
            self.myperms2['L2E-ZB0-'] = (" R "," B ","2R2"," U2","2R "," U2"," D2","2L'"," U2"," D2","2R "," U2","2R2"," B'"," R'")
            self.myperms2['L2E-ZB1-'] = self.invert_moves(self.myperms2['L2E-ZB0-'])
            self.myperms2['L2E-OB1-'] = self.invert_moves(self.myperms2['L2E-OB0-'])


            self.myperms2['L2E-NC0-'] = ('2B ', " U'", '2R ', ' U ', ' L2', " U'", "2R'", ' U ', ' L2', '2B ', ' U ', "2L'", " U'", ' R2', ' U ', '2L ', ' U ', "2B'", ' U2', '2B2', ' R2', '2B ', ' U2', '2B2', ' U2', ' R2', '2B ', ' R2')
            self.myperms2['L2E-ZC0-'] = (" U'", '2L ', ' F2', '2L ', ' F2', ' U2', '2L ', ' U2', '2L ', ' D2', '2R2', ' D2', "2L'", ' F2', '2L2', ' F2', ' U ')
            self.myperms2['L2E-OC0-'] = (" U'", '2L2', ' F2', "2L'", ' F2', ' B2', '2R ', ' F2', ' B2', "2L'", ' F2', '2L2', ' U ')
            self.myperms2['L2E-OC1-'] = self.invert_moves(self.myperms2['L2E-OC0-'])            
            self.myperms2['L2E-ZC1-'] = self.invert_moves(self.myperms2['L2E-ZC0-'])


            self.myperms2['L2ND-'] = ('2F2', ' D2', '2F ', ' D2', "2F'", ' D2', '2F ', ' D2', ' R2', '2F ', ' R2', '2F ', ' D2', '2F2', ' D2')
            self.myperms2['L2OD-'] = ('2B2', ' U2', "2B'", ' U2', '2B ', ' U2', "2B'", ' U2', "2B'", ' U2', '2B ', ' L2', "2B'", ' L2', '2B ', ' U2')
            self.myperms2['L2ZD-'] = (' R2', '2B ', ' D2', "2B'", ' D2', ' R2', '2B ', ' L2', '2B ', ' L2', '2B ', ' L2', '2B2', ' L2')


            
            self.myperms2['L2XA-'] = ('2B2', ' L2', ' U2', '2B2', ' U2', ' L2', '2B2')
            self.myperms2['L2XA1-'] = ('2B2', ' R2', ' D2', '2F2', ' D2', ' R2', '2B2')
            self.myperms2['L2FA-'] = ('2B ', ' L2', '2F2', ' D2', '2F ', ' D2', '2F ', ' L2', '2B2', ' U2', '2B ', ' U2')
            self.myperms2['L2FA1-'] = ('2B ', ' L2', '2F2', ' D2', '2F ', ' D2', "2B'", ' L2', '2F2', ' U2', "2F'", ' U2')
            self.myperms2['L2HA-'] = (" R2",'2F ', ' R2', '2B ', ' R2', ' L2', '2F ', "2B'", ' L2', ' R2', '2B ', ' R2', '2B '," R2")

            self.myperms2['L2HD-'] = (' L2', '2B2', ' L2', ' U2', '2B2', ' U2', ' L2', '2B2', ' L2')
            self.myperms2['L2FD-'] = (" L2","2B "," L2","2F2"," D2","2F "," D2","2F "," L2","2B2"," U2","2B "," U2"," L2")
            self.myperms2['L2FD1-'] = (' U2', '2F ', ' U2', '2B2', ' R2', '2B ', ' R2', "2F'", ' U2', '2B2', ' L2', "2B'", ' L2', ' U2')
            self.myperms2['L2XD-'] = ('2F ', ' U2', '2B ', ' U2', ' D2', '2F ', "2B'", ' D2', ' U2', '2B ', ' U2', '2B ')


            self.myperms2['L2E-HB0-'] = ("2R'", ' F2', " D'", '2F2', ' D ', ' F2', " D'", '2F2', ' D ', ' F2', ' D ', "2B'", " D'", ' F2', ' D ', '2B ', " D'", '2R ')


            self.myperms2['L2E-XB0-'] = ("2R'", ' F2', ' D ', "2B'", " D'", ' F2', ' D ', '2B ', " D'", ' F2', " D'", '2F2', ' D ', ' F2', " D'", '2F2', ' D ', '2R ')
          
            self.myperms2['L2E-FB0-'] = (" R "," B ","2L "," F2","2R2"," D2","2R "," D2","2R "," F2","2L2"," U2","2L "," U2"," B'"," R'")

            self.myperms2['L2E-XC0-'] = ('2R ', ' F2', ' D ', '2F2', " D'", ' F2', ' D ', '2F2', " D'", ' F2', " D'", '2B ', ' D ', ' F2', " D'", "2B'", ' D ', "2R'")

            self.myperms2['L2E-HC0-'] = ('2R ', ' F2', " D'", '2B ', ' D ', ' F2', " D'", "2B'", ' D ', ' F2', ' D ', '2F2', " D'", ' F2', ' D ', '2F2', " D'", "2R'")
   
            self.myperms2['L2E-FC0-'] = (" U'", "2R'", ' D2', '2L2', ' B2', "2L'", ' B2', "2L'", ' D2', '2R2', ' F2', "2R'", ' F2', ' U ')
            self.myperms2['L2E-FC1-'] = self.invert_moves(self.myperms2['L2E-FC0-'])

            self.myperms2['Edge6A'] = ("2L ", "2R'", " D2", "2L'", "2R ", " D2")
            self.myperms2['Edge6B'] = (" U'", "2L'", "2R ", ' U ', ' F2', " U'", "2L ", "2R'", ' U ', ' F2')
            self.myperms2['Edge6C'] = (" F'", "2U ", "2D'", " F'", ' D2', ' F ', "2U'", "2D ", " F'", ' D2', ' F2')
            self.myperms2['Edge6D'] = (' D2', " B'", "2L ", "2R'", ' B ', ' D2', " B'", "2L'", "2R ", ' B ')            
            self.myperms2['Edge6E'] = ('2L2', ' B2', "2R'", ' F2', "2L'", ' U2', '2R ', ' U2', ' F2', '2L ', ' D2', "2R'", '2L2', ' D2', ' B2', '2L2')
            self.myperms2['Edge6F'] = ('2L2', ' F2', '2L ', ' D2', '2L ', ' D2', ' F2', '2L ', ' F2', "2L'", ' F2', '2L ', ' D2', '2L2', ' D2', ' F2', '2L2', ' F2')
            self.myperms2['Edge6G'] = ('2R ', ' F2', "2R'", '2L ', ' F2', ' U2', ' B2', '2R ', ' B2', ' U2', '2R2', ' D2', '2R ', ' F2', "2L'", ' U2', '2R ', ' U2', ' F2', '2L ', ' D2', '2R ')
            self.myperms2['Edge6H'] = ('2L ', "2R'", ' D2', '2R ', "2L'", ' D2', '2L2', ' B2', "2R'", ' F2', '2L ', ' F2', ' U2', '2L ', ' U2', "2L'", ' U2', '2R ', ' U2', ' B2', '2L2')
            
            self.myperms2['Edge6PAX'] = (" U'", "2L ", "2R'", ' U ', ' F2', " U'", "2L'", "2R ", ' U ', ' F2') + ("2R2"," U2"," F2","2R2"," F2"," U2","2R2")
            self.myperms2['Edge6PBX'] = (" U'", "2L2", "2R2", ' U ', ' F2', " U'", "2L2", "2R2", ' U ', ' F2') + ("2R2"," U2"," F2","2R2"," F2"," U2","2R2")
            self.myperms2['Edge6PCX'] = (' D2', " B'", "2L'", "2R ", ' B ', ' D2', " B'", "2L ", "2R'", ' B ') + ("2R2"," F2"," D2","2R2"," D2"," F2","2R2")
            self.myperms2['Edge6PDX'] = (' D2', " B'", "2L2", "2R2", ' B ', ' D2', " B'", "2L2", "2R2", ' B ') + ("2R2"," F2"," D2","2R2"," D2"," F2","2R2")
        
            self.myperms2['Edge6PAN'] = (" U'", "2L ", "2R'", ' U ', ' F2', " U'", "2L'", "2R ", ' U ', ' F2') + ('2R2', ' U2', "2R'", ' F2', "2R'", ' F2', ' U2', "2R'", ' U2', '2R ', ' U2', "2R'", ' U2', '2R2', ' U2')
            self.myperms2['Edge6PBN'] = (" U'", "2L2", "2R2", ' U ', ' F2', " U'", "2L2", "2R2", ' U ', ' F2') + ('2R2', ' U2', "2R'", ' F2', "2R'", ' F2', ' U2', "2R'", ' U2', '2R ', ' U2', "2R'", ' U2', '2R2', ' U2')
            self.myperms2['Edge6PCN'] = (' D2', " B'", "2L'", "2R ", ' B ', ' D2', " B'", "2L ", "2R'", ' B ') + ('2R2', ' F2', "2R'", ' D2', "2R'", ' D2', ' F2', "2R'", ' F2', '2R ', ' F2', "2R'", ' F2', '2R2', ' F2')
            self.myperms2['Edge6PDN'] = (' D2', " B'", "2L2", "2R2", ' B ', ' D2', " B'", "2L2", "2R2", ' B ') + ('2R2', ' F2', "2R'", ' D2', "2R'", ' D2', ' F2', "2R'", ' F2', '2R ', ' F2', "2R'", ' F2', '2R2', ' F2')


            self.myperms2['EdgePK-A00-'] = ("2F'", ' L ', '2D ', " L'", ' U2', ' L ', "2D'", " L'", ' U2', '2F ')
            self.myperms2['EdgePK-A01-'] = ("2F'", ' U2', ' L ', '2D ', " L'", ' U2', ' L ', "2D'", " L'", '2F ')
            self.myperms2['EdgePK-A02-'] = ("2F'", " L'", '2U ', ' L ', ' U2', " L'", "2U'", ' L ', ' U2', '2F ')
            self.myperms2['EdgePK-A03-'] = ("2F'", ' U2', " L'", '2U ', ' L ', ' U2', " L'", "2U'", ' L ', '2F ')
            self.myperms2['EdgePK-A04-'] = ('2F2', ' R2', " D'", "2L'", ' D ', ' R2', " D'", '2L ', ' D ', '2F2')
            self.myperms2['EdgePK-A05-'] = ('2F2', " D'", "2L'", ' D ', ' R2', " D'", '2L ', ' D ', ' R2', '2F2')
            self.myperms2['EdgePK-A06-'] = ('2F2', ' R2', ' D ', "2R'", " D'", ' R2', ' D ', '2R ', " D'", '2F2')
            self.myperms2['EdgePK-A07-'] = ('2F2', ' D ', "2R'", " D'", ' R2', ' D ', '2R ', " D'", ' R2', '2F2')
            self.myperms2['EdgePK-A08-'] = ('2B2', ' R2', ' D ', '2L ', " D'", ' R2', ' D ', "2L'", " D'", '2B2')
            self.myperms2['EdgePK-A09-'] = ('2B2', ' D ', '2L ', " D'", ' R2', ' D ', "2L'", " D'", ' R2', '2B2')
                        
            self.myperms2['EdgePK-D00-'] = (" L2","2F'", ' L ', '2D ', " L'", ' U2', ' L ', "2D'", " L'", ' U2', '2F '," L2")
            self.myperms2['EdgePK-D01-'] = (" L2","2F'", ' U2', ' L ', '2D ', " L'", ' U2', ' L ', "2D'", " L'", '2F '," L2")
            self.myperms2['EdgePK-D02-'] = (" L2","2F'", " L'", '2U ', ' L ', ' U2', " L'", "2U'", ' L ', ' U2', '2F '," L2")
            self.myperms2['EdgePK-D03-'] = (" L2","2F'", ' U2', " L'", '2U ', ' L ', ' U2', " L'", "2U'", ' L ', '2F '," L2")
            self.myperms2['EdgePK-D04-'] = (" R2",'2F2', ' R2', " D'", "2L'", ' D ', ' R2', " D'", '2L ', ' D ', '2F2'," R2")
            self.myperms2['EdgePK-D05-'] = (" R2",'2F2', " D'", "2L'", ' D ', ' R2', " D'", '2L ', ' D ', ' R2', '2F2'," R2")
            self.myperms2['EdgePK-D06-'] = (" R2",'2F2', ' R2', ' D ', "2R'", " D'", ' R2', ' D ', '2R ', " D'", '2F2'," R2")
            self.myperms2['EdgePK-D07-'] = (" R2",'2F2', ' D ', "2R'", " D'", ' R2', ' D ', '2R ', " D'", ' R2', '2F2'," R2")
            self.myperms2['EdgePK-D08-'] = (" R2",'2B2', ' R2', ' D ', '2L ', " D'", ' R2', ' D ', "2L'", " D'", '2B2'," R2")
            self.myperms2['EdgePK-D09-'] = (" R2",'2B2', ' D ', '2L ', " D'", ' R2', ' D ', "2L'", " D'", ' R2', '2B2'," R2")




            self.myperms2['SideLA-'] = ('2L ', ' U2', "2R'", ' F2', '2R ', ' F2', ' U2', ' B2', "2R'", ' D2', '2R2', ' D2', "2R'", ' B2')
            self.myperms2['SideLB-'] = self.invert_moves(self.myperms2['SideLA-'])
            self.myperms2['SideLC-'] = ('2L ', ' F2', '2L ', ' F2', '2L ', ' F2', '2L2', ' B2', "2L'", ' F2', '2L ', ' B2')
            self.myperms2['SideLD-'] = self.invert_moves(self.myperms2['SideLC-'])
            self.myperms2['SideLE-'] = ("2R'", ' B2', ' U2', '2R ', ' U2', "2R'", ' U2', '2R2', '2L ', ' U2', "2L'", ' B2', '2R2')
            self.myperms2['SideLF-'] = self.invert_moves(self.myperms2['SideLE-'])

            self.myperms2['SideLG-'] = (' F2', ' U2', ' F ', "2U'", " F'", ' U2', ' F ', '2U2', ' F ', ' U2', " F'", "2U'", ' F ', ' U2')
            self.myperms2['SideLH-'] = ('2R2', ' B2', "2R'", ' B2', "2R'", ' U2', '2L2', ' F2', "2L'", ' F2', "2L'", ' U2')
            self.myperms2['SideLI-'] = ('2R ', ' B2', "2L'", ' B2', '2L2', ' F2', "2L'", ' U2', '2L ', ' U2', '2L ', ' F2', '2L2', ' U2', "2R'", ' U2')

            self.myperms2['SideRA-'] = (" F2",'2L2', ' F2', '2L ', ' B2', "2L'", ' B2', ' F2', ' U2', "2L'", ' U2', '2R ', ' B2', "2R'", ' B2', '2L2'," F2")
            self.myperms2['SideRB-'] = self.invert_moves(self.myperms2['SideRA-'])
            self.myperms2['SideRC-'] = ('2L ', ' B2', '2L ', ' B2', ' D2', '2L ', '2R ', ' D2', "2R'", ' D2', "2L'", ' D2', "2L'")
            self.myperms2['SideRD-'] = self.invert_moves(self.myperms2['SideRC-'])
            self.myperms2['SideRE-'] = ('2L2', ' U2', "2L'", ' U2', "2L'", "2R'", ' D2', ' B2', '2R ', ' B2', ' D2', '2R ')
            self.myperms2['SideRF-'] = self.invert_moves(self.myperms2['SideRE-'])

            self.myperms2['SideRG-'] = ('2L2', ' D2', '2L ', ' B2', "2L'", ' B2', "2L'", ' D2', '2L2', ' B2', '2R ', ' B2', "2R'", ' U2', '2L ', ' U2')
            self.myperms2['SideRH-'] = ("2R'", ' B2', '2R2', ' F2', "2R'", ' D2', '2R ', ' D2', '2R ', ' F2', '2R2', ' D2', "2L'", ' D2', '2L ', ' B2')
            self.myperms2['SideRI-'] = ("2L'", ' U2', '2L ', ' U2', '2L ', ' F2', '2L2', ' U2', "2R'", ' U2', '2R ', ' B2', "2L'", ' B2', '2L2', ' F2')


            self.myperms2['SideSA-'] = (" U2",'2L ', ' U2', "2R'", ' F2', '2R ', ' F2', ' U2', ' B2', "2R'", ' D2', '2R2', ' D2', "2R'", ' B2'," U2")
            self.myperms2['SideSB-'] = (" U2",'2L ', ' F2', '2L ', ' F2', '2L ', ' F2', '2L2', ' B2', "2L'", ' F2', '2L ', ' B2'," U2")
            self.myperms2['SideSC-'] = ("2R'", ' U2', "2R'", ' U2', "2R'", ' F2', ' D2', ' B2', '2L ', ' B2', ' D2', ' F2', "2R'")
            self.myperms2['SideSD-'] = self.invert_moves(self.myperms2['SideSC-'])

            self.myperms2['SideSE-'] = ("2L'", ' B2', "2R'", ' B2', ' D2', "2R'", ' D2', '2R ', ' D2', "2L'", ' D2', ' F2', "2R'", ' F2', '2R ', ' U2', "2L'", ' U2', ' F2', "2L'", ' F2', "2L'")
            self.myperms2['SideSF-'] = ('2L ', ' F2', '2L ', ' F2', '2L2', ' U2', '2R ', ' B2', '2R ', ' B2', '2R2', ' U2')
            self.myperms2['SideSG-'] = ('2L ', ' F2', '2R2', ' U2', "2R'", ' F2', "2R'", ' F2', '2R ', ' U2', '2R2', ' D2', '2R ', ' D2', "2L'", ' F2')

            self.myperms2['SideTA-'] = ('2L2', ' F2', '2L ', ' B2', "2L'", ' B2', ' F2', ' U2', "2L'", ' U2', '2R ', ' B2', "2R'", ' B2', '2L2')
            self.myperms2['SideTB-'] = ('2R2', ' D2', "2R'", ' B2', '2R2', ' B2', ' D2', ' B2', '2R ', ' B2', ' D2', '2R ', ' D2')
            self.myperms2['SideTC-'] = self.invert_moves(self.myperms2['SideTB-'])

            self.myperms2['SideTD-'] = ('2R ', ' B2', "2R'", ' B2', "2R'", ' U2', '2L2', ' F2', "2L'", ' F2', "2L'", ' U2',"2R ")
            self.myperms2['SideTE-'] = ('2R2', ' D2', '2L ', ' D2', "2L'", ' F2', '2L2', ' F2', '2L ', ' D2', "2L'", ' D2', '2R2')
            
            self.myperms2['SideKKA-'] = ("2R "," U2","2R "," U2","2R "," U2","2R "," U2","2R ")
            self.myperms2['SideKKB-'] = ("2L'", ' D2', "2L'", ' D2', '2L ', ' B2', '2L2', ' D2', "2L'", ' D2', "2L'", ' B2')
            self.myperms2['SideKKC-'] = ('2R ', ' U2', '2R ', ' U2', '2R2', ' B2', "2R'", ' U2', '2R ', ' U2', '2R ', ' B2')

            self.myperms2['SideKKD-'] = (' U2', '2R ', ' U2', ' F2', ' B2', ' D2', '2L ', ' D2', ' B2', ' F2')
            self.myperms2['SideKKE-'] = (" D'", "2F'", ' D ', ' B2', " D'", '2F ', ' D ', " U'", "2F'", ' U ', ' B2', " U'", '2F ', ' U ')
            self.myperms2['SideKKF-'] = (' F2', "2L'", ' B2', '2L ', ' F2', "2L'", ' B2', '2L ', '2R ', ' F2', "2R'", ' B2', '2R ', ' F2', "2R'", ' B2')
            
            self.myperms2['SideJJA-'] = ('2R2', ' U2', '2L ', ' U2', "2L'", ' B2', '2R ', ' B2', ' U2', '2R2', ' D2', "2R'", ' U2', '2R ', ' D2')
            self.myperms2['SideJJB-'] = ("2R'", ' U2', ' D2', "2R'", ' U2', "2R ", ' D2', '2R2', ' U2', "2R'", ' U2', "2R'")
            self.myperms2['SideJJC-'] = self.invert_moves(self.myperms2['SideJJB-'])

            self.myperms2['SideJJD-'] = ('2L ', ' D2', '2L ', ' D2', '2L ', ' B2', '2R2', ' U2', '2R ', ' U2', '2R ', ' B2', '2L ')
            self.myperms2['SideJJE-'] = ("2R'", ' U2', ' D2', "2R'", ' U2', '2R ', ' D2', '2R2', ' U2', "2R'", ' U2', '2R2', ' U2', ' D2', "2R'", ' U2', '2R ', ' D2', '2R2', ' U2', "2R'", ' U2', "2R'")
            
            self.myperms2['SideIIA-'] = (" U2","2R "," U2","2R "," U2","2R "," U2","2R "," U2","2R "," U2")
            self.myperms2['SideIIB-'] = (' U2', '2R ', ' U2', '2R ', ' U2', '2R ', ' U2', '2R ', ' U2', '2R ', "2L'", ' U2', '2L ', ' F2', ' U2', '2R ', ' U2', "2R'", ' F2')

            self.myperms2['SideIIC-'] = ("2R'", ' B2', ' U2', ' D2', ' F2', "2L'", ' F2', ' D2', ' U2', ' B2')
            self.myperms2['SideIID-'] = ('2L2', ' B2', "2R'", ' B2', '2R ', ' D2', "2L'", ' D2', ' B2', "2L'", ' B2', ' F2', '2L ', ' F2', ' U2', '2L ', ' U2', "2R'", ' F2', '2R ', ' F2', '2L2')
            
            self.myperms2['SideSSA-'] = ('2R ', ' U2', '2R2', ' B2', "2R'", ' B2', '2R2', ' F2', ' D2', '2L ', ' D2', ' F2', ' U2')
            self.myperms2['SideSSB-'] = (' F2', '2R ', ' F2', '2L ', ' D2', "2L'", ' D2', "2R'", ' F2', '2L ', ' F2', "2L'", ' U2', '2R ', ' U2')

            self.myperms2['SideSSC-'] = self.myperms2['SideSSA-'] * 2
            self.myperms2['SideSSD-'] = ('2R2', ' U2', ' B2', '2R ', "2L'", ' B2', "2R'", '2L ', ' B2', '2R2', ' B2', ' U2')
            

            self.myperms2['CenterPXA-'] = ("2R2","2F2","2R2","2F2")
            self.myperms2['CenterPXB-'] = (" U ","2R2","2F2","2R2","2F2"," U'")
            self.myperms2['CenterPXC-'] = (" U2","2R2","2F2","2R2","2F2"," U2")
            self.myperms2['CenterPWA-'] = ('2F2', " D'", '2R2', '2F2', '2R2', '2F2', ' D ', '2F2')
            self.myperms2['CenterPWB-'] = ('2B2', " D'", '2L2', '2B2', '2L2', '2B2', ' D ', '2B2')
            self.myperms2['CenterPWC-'] = ('2F2', ' U ', '2L2', '2F2', '2L2', '2F2', " U'", '2F2')
            self.myperms2['CenterPWD-'] = ('2B2', ' U ', '2R2', '2B2', '2R2', '2B2', " U'", '2B2') 
            self.myperms2['CenterPVA-'] = ("2F'", '2U ', '2F ', "2U'", '2F ', "2R'", "2F'", '2R ')
            self.myperms2['CenterPVB-'] = ("2F'", '2U ', "2F'", "2U'", '2F ', "2R'", '2F ', '2R ')
            self.myperms2['CenterPVC-'] = ("2R'", '2F ', '2R ', "2F'", '2U ', "2F'", "2U'", '2F ')
            self.myperms2['CenterPUA-'] = ('2F2', ' U ', '2R2', " U'", '2R2', '2F2', '2R2', ' U ', '2R2', " U'")
            self.myperms2['CenterPUB-'] = ('2R2', '2F2', '2R2', '2F2', ' U2', '2R2', '2F2', '2R2', '2F2', ' U2')


            

            self.myperms2['CenterP8-'] = ("2U2","2R2","2U'","2R2","2U'","2R2","2U'","2R2","2U ")      
            
            self.myperms2['CenterP6A-'] = ("2R ","2U ","2R'","2U'")
            self.myperms2['CenterP6B-'] = ("2R ","2U'","2R'","2U ")
            self.myperms2['CenterP6C-'] = ("2R ","2U2","2R'","2U2")
            self.myperms2['CenterP6D-'] = ("2R2","2U'","2R2","2U ")
            self.myperms2['CenterP6E-'] = ("2U'","2R ","2U ","2R2","2F ","2R ","2F'")
            self.myperms2['CenterP6F-'] = ('2B ', '2D2', '2B ', '2D2', "2L'", "2B'", '2L ', '2U ', "2B'", "2U'")
            self.myperms2['CenterP6G-'] = ("2R ","2U ","2R ","2U'","2R2")
            self.myperms2['CenterP6H-'] = ("2R ","2U'","2R ","2U ","2R2")
            self.myperms2['CenterP6I-'] = ("2R2","2U ","2R'","2U'","2R'")
            self.myperms2['CenterP6J-'] = ("2R2","2U'","2R'","2U ","2R'")
            self.myperms2['CenterP6K-'] = ("2R2","2U ","2R2","2U ","2R2","2U2","2R2")
            self.myperms2['CenterP6L-'] = ("2R2","2U2","2R2","2U ","2R2","2U ","2R2")
            self.myperms2['CenterP6M-'] = ("2U ","2R2","2U2","2R2","2U ")
            self.myperms2['CenterP6N-'] = ("2F ","2R ","2F2","2R'","2F ")
            self.myperms2['CenterP6O-'] = ("2F'","2R ","2F2","2R'","2F'")

            

            self.myperms2['CenterP4A-'] = ("2R2","2U2","2R'","2U2","2R'")
            self.myperms2['CenterP4B-'] = ("2R ","2U2","2R ","2U2","2R2")
            self.myperms2['CenterP4C-'] = ("2U ","2F ","2R ","2F'","2R'","2U'")
            self.myperms2['CenterP4D-'] = ('2F ', "2D'", '2F2', '2D ', "2F'", '2R2', '2F2', '2R2')
            self.myperms2['CenterP4D(1)-'] = ("2D'", "2F'", '2D2', '2F2', '2L ', "2F'", "2L'", "2D'")
            self.myperms2['CenterP4D(2)-'] = ("2F'", '2D2', "2B'", '2D2', '2F ', '2D ', '2B ', "2D'")
            self.myperms2['CenterP4D(3)-'] = ("2D'", "2F'", '2D ', "2F'", '2R2', '2F ', '2R2', '2F ')
            self.myperms2['CenterP4D(4)-'] = ('2F ', "2L'", "2F'", '2L ', "2F'", "2D'", '2F ', '2D ')
            self.myperms2['CenterP4XA-'] = ("2L'"," U ","2R'","2D2","2R "," U'","2D2","2L ")
            self.myperms2['CenterP4XB-'] = ("2L'"," D'","2R'","2D2","2R "," D ","2D2","2L ")
            self.myperms2['CenterP4YA-'] = ("2B "," U'","2R ","2U ","2R'"," U ","2U'","2B'")
            self.myperms2['CenterP4YB-'] = ("2B "," D ","2R ","2U ","2R'"," D'","2U'","2B'")
            self.myperms2['CenterP4YC-'] = (' D2', '2L ', '2U2', '2L ', '2U2', '2L2', ' D2')
            self.myperms2['CenterP4YD-'] = (' U2', '2L ', '2U2', '2L ', '2U2', '2L2', ' U2')
            self.myperms2['CenterP4ZA-'] = (" U2","2R ","2U2","2R'"," U2","2R2","2U2","2R2")
            self.myperms2['CenterP4ZB-'] = (" D2","2R ","2U2","2R'"," D2","2R2","2U2","2R2")
            self.myperms2['CenterP4ZC-'] = (' U2', '2R ', '2U2', "2R'", ' U2', '2L2', '2U2', '2L2')
            self.myperms2['CenterP4ZD-'] = (' D2', '2R ', '2U2', "2R'", ' D2', '2L2', '2U2', '2L2')
            self.myperms2['CenterP4WA-'] = ('2L ', '2U2', ' D ', '2R ', '2U2', "2R'", " D'", "2L'")
            self.myperms2['CenterP4WB-'] = ('2L ', '2U2', " U'", '2R ', '2U2', "2R'", " U ", "2L'")

            



            
            self.myperms2['BigCenter-AOpp-'] = ('2L2', '2R2', '2F2', '2R2', '2L2', '2F2')
            self.myperms2['BigCenter-ANbr-'] = ("2R "," U ","2L'"," U'","2R'"," U ","2L "," U2","2R "," U ","2L'"," U'","2R'"," U ","2L2",
                                               " F ","2R'"," F'","2L'"," F ","2R "," F2","2L "," F ","2R'"," F'","2L'"," F ","2R ")




            self.myperms2['BigCenter-ACyc3-'] = self.myperms2['BigCenter-ANbr-'] + self.transform(self.myperms2['BigCenter-ANbr-'],1)
            self.myperms2['BigCenter-ACyc4-'] = self.myperms2['BigCenter-ANbr-'] + self.transform(self.myperms2['BigCenter-ANbr-'],3) + self.transform(self.myperms2['BigCenter-ANbr-'],14)
            self.myperms2['BigCenter-ASwap2-'] = self.myperms2['BigCenter-ANbr-'] + self.transform(self.myperms2['BigCenter-ANbr-'],29)



            if self.size >= 6:
                self.myperms2['BigCenter-AOppW-'] = ('2F2', '2B2', '2L2', '2B2', '2F2', '2L2', '3R2', '3B2', '3F2', '3R2', '3F2', '3B2')
                self.myperms2['BigCenter-ANbrW-'] = self.myperms2['BigCenter-ANbr-'] + self.transform(self.myperms2['BigCenter-ANbr-'],48)


                self.myperms2['BigCenter-ACyc3W-'] = self.myperms2['BigCenter-ANbrW-'] + self.transform(self.myperms2['BigCenter-ANbrW-'],1)
                self.myperms2['BigCenter-ACyc4W-'] = self.myperms2['BigCenter-ANbrW-'] + self.transform(self.myperms2['BigCenter-ANbrW-'],3) + self.transform(self.myperms2['BigCenter-ANbrW-'],14)
                self.myperms2['BigCenter-ASwap2W-'] = self.myperms2['BigCenter-ANbrW-'] + self.transform(self.myperms2['BigCenter-ANbrW-'],29)


            self.myperms2['CenterA-OppX'] = (" U ", '2R2', " U'", '2F2', ' U ', '2R2', " U'", '2F2')
            self.myperms2['CenterA-OppX(1)'] = (" D'", '2L2', ' D ', '2R2', " D'", '2L2', ' D ', '2R2')
            self.myperms2['CenterA-OppX(2)'] = ('2R2', '2F ', ' L ', "2F'", '2R2', '2F ', " L'", "2F'")
            self.myperms2['CenterA-OppX(3)'] = ('2R2', "2B'", ' R ', '2B ', '2R2', "2B'", " R'", '2B ')
            self.myperms2['CenterA-OppY'] = ('2R2', " U'", '2F2', ' U ', '2R2', " U'", '2F2', ' U ')
            self.myperms2['CenterA-OppY(1)'] = ('2R2', " D'", '2L2', ' D ', '2R2', " D'", '2L2', ' D ')
            self.myperms2['CenterA-OppY(2)'] = ('2F ', ' L ', "2F'", '2R2', '2F ', " L'", "2F'", '2R2')
            self.myperms2['CenterA-OppY(3)'] = ("2B'", ' R ', '2B ', '2R2', "2B'", " R'", '2B ', '2R2')
            self.myperms2['CenterA-OppZ'] = (" U'", '2R2', " U'", '2F2', ' U ', '2R2', " U'", '2F2', ' U2')
            self.myperms2['CenterA-OppZ(1)'] = (" U'", '2R2', " U'", '2L2', ' U ', '2R2', " U'", '2L2', ' U2')
            self.myperms2['CenterA-OppZ(2)'] = ('2R2', " D'", '2F ', '2B ', '2R2', "2F'", "2B'", '2R2', ' D ', '2R2')
            self.myperms2['CenterA-OppZ(3)'] = ('2R2', " D'", '2R2', '2B ', '2F ', '2R2', "2B'", "2F'", ' D ', '2R2')
            self.myperms2['CenterA-OppZ(4)'] = ('2F2', ' D ', '2R ', '2L ', '2F2', "2R'", "2L'", '2F2', " D'", '2F2')
            self.myperms2['CenterA-OppZ(5)'] = ('2F2', ' D ', '2F2', '2L ', '2R ', '2F2', "2L'", "2R'", " D'", '2F2')
            self.myperms2['CenterA-OppZ(6)'] = ('2B2', " D'", '2F2', ' D ', '2B2', " D'", '2L2', '2F2', '2L2', ' D ')
            


            self.myperms2['CenterA-IO_D(0)'] = ("2F'", '2U ', '2F ', " U2", "2F'", "2U'", '2F ', " U2")
            self.myperms2['CenterA-IO_V(0)'] = ('2R ', '2U2', "2R'", " U2", '2R ', '2U2', "2R'", " U2")
            self.myperms2['CenterA-IO_D(1)'] = ("2F'", '2U ', '2F ', " D2", "2F'", "2U'", '2F ', " D2")
            self.myperms2['CenterA-IO_V(1)'] = ('2R ', '2U2', "2R'", " D2", '2R ', '2U2', "2R'", " D2")
            self.myperms2['CenterA-IO_V(2)'] = ("2R "," U ","2L'"," U'","2R'"," U ","2L "," U'")
            self.myperms2['CenterA-IO_V(3)'] = ("2L'"," U ","2R "," U'","2L "," U ","2R'"," U'")
            self.myperms2['CenterA-IO_D(2)'] = (' U ', "2L'", " U'", '2R ', ' U ', '2L ', " U'", "2R'")
            self.myperms2['CenterA-IO_D(3)'] = (' U ', "2R ", " U'", "2L'", ' U ', "2R'", " U'", "2L ")


            
            self.myperms2['CenterA-II_D(0)'] = (' U2', '2R ', '2U2', "2R'", " U2", '2R ', '2U2', "2R'")
            self.myperms2['CenterA-OO_D(0)'] = (" D2", '2R ', '2U2', "2R'", " D2", '2R ', '2U2', "2R'")
            self.myperms2['CenterA-II_V(0)'] = (" U2", "2F'", '2U ', '2F ', " U2", "2F'", "2U'", '2F ')
            self.myperms2['CenterA-OO_V(0)'] = (" D2", "2F'", '2U ', '2F ', " D2", "2F'", "2U'", '2F ')

            self.myperms2['CenterA-IO_D(4)'] = (' U2', "2B'", "2U'", '2B ', ' U2', "2B'", '2U ', '2B ')
            self.myperms2['CenterA-IO_D(5)'] = (' D2', "2B'", "2U'", '2B ', ' D2', "2B'", '2U ', '2B ')

            self.myperms2['CenterA-3AAA(0)'] = (" F ","2D "," R2","2D'","2R'","2D "," R2","2D'","2R "," F'")
            self.myperms2['CenterA-3CCC(0)'] = (" F ","2U'"," R2","2U ","2L ","2U'"," R2","2U ","2L'"," F'")
            self.myperms2['CenterA-3BBB(0)'] = (" F'","2D'","2L'"," U2","2L ","2D ","2L'"," U2","2L "," F ")
            self.myperms2['CenterA-3DDD(0)'] = (" F'","2U ","2R "," U2","2R'","2U'","2R "," U2","2R'"," F ")

            self.myperms2['CenterA-3AAC(0)'] = (" F'","2D "," R2","2D'","2R'","2D "," R2","2D'","2R "," F ")
            self.myperms2['CenterA-3CCA(0)'] = (" F'","2U'"," R2","2U ","2L ","2U'"," R2","2U ","2L'"," F ")
            self.myperms2['CenterA-3BBD(0)'] = (" F ","2D'","2L'"," U2","2L ","2D ","2L'"," U2","2L "," F'")
            self.myperms2['CenterA-3DDB(0)'] = (" F ","2U ","2R "," U2","2R'","2U'","2R "," U2","2R'"," F'")
            
            self.myperms2['CenterA-3AAD(0)'] = ("2D "," R2","2D'","2R'","2D "," R2","2D'","2R ")
            self.myperms2['CenterA-3CCB(0)'] = ("2U'"," R2","2U ","2L ","2U'"," R2","2U ","2L'")
            self.myperms2['CenterA-3BBC(0)'] = ("2D'","2L'"," U2","2L ","2D ","2L'"," U2","2L ")
            self.myperms2['CenterA-3DDA(0)'] = ("2U ","2R "," U2","2R'","2U'","2R "," U2","2R'")

            self.myperms2['CenterA-3AAB(0)'] = ('2U ', "2L'", ' U2', '2L ', "2U'", "2L'", ' U2', '2L ')
            self.myperms2['CenterA-3CCD(0)'] = ("2D'", '2R ', ' U2', "2R'", '2D ', '2R ', ' U2', "2R'")
            self.myperms2['CenterA-3DDC(0)'] = ('2D ', ' R2', "2D'", '2L ', '2D ', ' R2', "2D'", "2L'")
            self.myperms2['CenterA-3BBA(0)'] = ("2U'", ' R2', '2U ', "2R'", "2U'", ' R2', '2U ', '2R ')

            self.myperms2['CenterA-3ADC(0)'] = ("2L'"," D'","2F'",' D ','2L '," D'",'2F ',' D ')
            self.myperms2['CenterA-3CBA(0)'] = ("2R "," D'","2B ",' D ',"2R'"," D'","2B'",' D ')
            self.myperms2['CenterA-3BAD(0)'] = ("2R "," D ","2F'"," D'","2R'"," D ","2F "," D'")
            self.myperms2['CenterA-3DCB(0)'] = ("2L'"," D ","2B "," D'","2L "," D ","2B'"," D'")

            self.myperms2['CenterA-3ABC(0)'] = (" U2","2L'"," D'","2F'",' D ','2L '," D'",'2F ',' D '," U2")
            self.myperms2['CenterA-3CDA(0)'] = (" U2","2R "," D'","2B ",' D ',"2R'"," D'","2B'",' D '," U2")
            self.myperms2['CenterA-3BCD(0)'] = (" U2","2R "," D ","2F'"," D'","2R'"," D ","2F "," D'"," U2")
            self.myperms2['CenterA-3DAB(0)'] = (" U2","2L'"," D ","2B "," D'","2L "," D ","2B'"," D'"," U2")

            self.myperms2['CenterA-3V-AAD(0)'] = ("2R "," U ","2L "," U'","2R'"," U ","2L'"," U'")
            self.myperms2['CenterA-3V-CCB(0)'] = ("2L'"," U ","2R'"," U'","2L "," U ","2R "," U'")
            self.myperms2['CenterA-3V-ADA(0)'] = ("2R ", ' F ', '2U2', " F'", "2R'", ' F ', '2U2', " F'")
            self.myperms2['CenterA-3V-CBC(0)'] = ("2L'", ' F ', '2D2', " F'", '2L ', ' F ', '2D2', " F'")

            self.myperms2['CenterA-3V-ADD(0)'] = ("2L2"," F'","2R'"," F ","2L2"," F'","2R "," F ")
            self.myperms2['CenterA-3V-CBB(0)'] = ("2R2"," F'","2L "," F ","2R2"," F'","2L'"," F ")
            self.myperms2['CenterA-3V-AAA(0)'] = ('2U2', '2L ', '2F2', "2L'", ' F2', '2L ', '2F2', "2L'", ' F2', '2U2')
            self.myperms2['CenterA-3V-CCC(0)'] = ('2D2', "2R'", '2B2', '2R ', ' F2', "2R'", '2B2', '2R ', ' F2', '2D2')
            self.myperms2['CenterA-3V-CAA(0)'] = ('2D2', '2R ', '2B2', "2R'", ' B2', '2R ', '2B2', "2R'", ' B2', '2D2')
            self.myperms2['CenterA-3V-ACC(0)'] = ('2U2', "2L'", '2F2', '2L ', ' B2', "2L'", '2F2', '2L ', ' B2', '2U2')

            self.myperms2['CenterA-3V-ADB(0)'] = ('2D2', "2L'", ' U ', '2L ', '2D2', "2L'", " U'", '2L ')
            self.myperms2['CenterA-3V-CBD(0)'] = ('2U2', '2R ', ' U ', "2R'", '2U2', '2R ', " U'", "2R'")
            self.myperms2['CenterA-3V-ABD(0)'] = ('2L ', ' U ', "2L'", '2U2', '2L ', " U'", "2L'", '2U2')
            self.myperms2['CenterA-3V-CDB(0)'] = ("2R'", ' U ', '2R ', '2D2', "2R'", " U'", '2R ', '2D2')
            
            self.myperms2['CenterA-3V-AAC(0)'] = ('2L ', ' U2', "2L'", '2D2', '2L ', ' U2', "2L'", '2D2')
            self.myperms2['CenterA-3V-CCA(0)'] = ("2R'", ' U2', '2R ', '2U2', "2R'", ' U2', '2R ', '2U2')
            self.myperms2['CenterA-3V-ACA(0)'] = ('2U2', '2L ', ' U2', "2L'", '2U2', '2L ', ' U2', "2L'")
            self.myperms2['CenterA-3V-CAC(0)'] = ('2D2', "2R'", ' U2', '2R ', '2D2', "2R'", ' U2', '2R ')

            self.myperms2['CenterA-3V-ACB(0)'] = ('2F2', '2L ', ' D ', '2R ', " D'", "2L'", ' D ', "2R'", " D'", '2F2')
            self.myperms2['CenterA-3V-CAD(0)'] = ('2B2', "2R'", ' D ', "2L'", " D'", '2R ', ' D ', '2L ', " D'", '2B2')
            self.myperms2['CenterA-3V-ABC(0)'] = ('2F2', '2L ', ' F ', '2D2', " F'", "2L'", ' F ', '2D2', '2F2', " F'")
            self.myperms2['CenterA-3V-CDA(0)'] = ('2B2', "2R'", ' F ', '2U2', " F'", '2R ', ' F ', '2U2', '2B2', " F'")
            self.myperms2['CenterA-3V-ABB(0)'] = ('2F2', '2R2', " F'", "2L'", ' F ', '2R2', " F'", '2L ', '2F2', ' F ')
            self.myperms2['CenterA-3V-CDD(0)'] = ('2B2', '2L2', " F'", '2R ', ' F ', '2L2', " F'", "2R'", '2B2', ' F ')
            self.myperms2['CenterA-3V-AAB(0)'] = ('2F2', " F'", '2R2', " F'", "2L'", ' F ', '2R2', " F'", '2L ', '2F2', ' F2')
            self.myperms2['CenterA-3V-CCD(0)'] = ('2B2', " F'", '2L2', " F'", '2R ', ' F ', '2L2', " F'", "2R'", '2B2', ' F2') 
            self.myperms2['CenterA-3V-ABA(0)'] = (' B2', '2F2', '2L ', ' B ', '2R2', " B'", "2L'", ' B ', '2R2', ' B ', '2F2')
            self.myperms2['CenterA-3V-CDC(0)'] = (' B2', '2B2', "2R'", ' B ', '2L2', " B'", '2R ', ' B ', '2L2', ' B ', '2B2')



            #self.myperms2['OLLParity'] = ("2R'"," U2","2L "," F2","2L'"," F2","2R2"," U2","2R "," U2","2R'"," U2"," F2","2R2"," F2")

            perm_A = ("2R "," U2","2R "," U2"," F2","2R "," F2","2L'"," U2","2L "," U2","2R2")
            perm_a = self.invert_moves(perm_A)

            #perm_a = ("2L2"," U2","2R "," U2","2R'"," F2","2L "," F2"," U2","2L "," U2","2L ")
            #perm_B = ("2L2"," U2","2R "," U2","2R'"," F2","2L "," F2","2L "," U2","2R "," U2","2R'"," F2","2L "," F2")

            ("2L2"," U2","2R "," U2","2R'"," F2","2L "," F2","2L "," F2","2L'"," U2","2L "," U2","2L "," F2")




            perm_k0 = ("2R2"," B2"," D2","2R "," D2","2R'"," D2","2R2"," B2","2L "," B2","2L'"," D2","2R "," B2")
            perm_k1 = ("2L2"," U2"," B2","2L'"," B2","2L "," B2","2L2"," U2","2R'"," U2","2R "," B2","2L'"," U2")
            perm_k2 = ('2R2', ' D2', '2L ', ' U2', "2R'", ' U2', ' B2', "2R'", ' B2', '2R ', ' B2', "2L'", ' B2', ' D2', '2R2')
            perm_k3 = ('2L2', ' B2', ' U2', "2R'", ' U2', '2L ', ' U2', "2L'", ' U2', ' F2', "2L'", ' F2', '2R ', ' B2', '2L2')

            perm_kB = ('2R2', ' D2', "2L'", ' U2', '2R ', ' U2', ' F2', '2R ', ' F2', "2R'", ' F2', '2L ', ' F2', ' D2', '2R2')
            perm_kC = ('2R2', ' D2', ' B2', '2L ', ' B2', "2R'", ' B2', '2R ', ' B2', ' U2', '2R ', ' U2', "2L'", ' D2', '2R2')
            
            

            perm_j0 = ('2L2', ' B2', ' U2', "2L'", ' U2', '2R ', ' B2', "2R'", ' B2', '2L2', ' U2', '2L ', ' U2', "2L'", ' B2')
            perm_j1 = ('2R2', ' D2', ' B2', '2R ', ' B2', "2L'", ' D2', '2L ', ' D2', '2R2', ' B2', "2R'", ' B2', '2R ', ' D2')
            
            perm_j2 = ('2L2', ' B2', ' U2', "2L'", ' U2', '2L2', "2R'", ' F2', "2R'", ' F2', '2R2', ' U2', '2L ', ' U2', "2L'", ' B2')
            perm_j3 = ('2R2', ' D2', ' B2', '2R ', ' B2', '2R2', '2L ', ' U2', '2L ', ' U2', '2L2', ' B2', "2R'", ' B2', '2R ', ' D2')

            perm_b0 = ("2R2"," F2"," U2","2R "," U2","2R2"," F2","2R "," U2","2R2"," U2"," F2","2R "," F2")


            self.myperms2['WingSwapParallel-A0-'] = ("2R2"," U2","2L'"," U2","2L "," F2","2R'"," F2"," U2","2R'"," U2","2R'")
            self.myperms2['WingSwapParallel-A1-'] = ("2R2"," U2","2R "," B2","2L'"," D2","2R "," D2"," B2","2L "," U2","2R ")
            self.myperms2['WingSwapParallel-A2-'] = ("2L2"," D2","2L "," D2","2R'"," D2","2R "," D2"," B2","2R "," B2","2L ")
            self.myperms2['WingSwapParallel-A3-'] = ("2L2"," D2","2R "," F2","2R'"," F2","2L "," D2"," B2","2R "," B2","2L ")



            
            #SwapD ('2L2', ' B2', ' U2', '2L ', ' U2', '2L2', ' B2', '2L ', ' U2', '2L2', ' B ', "2D'", " B'", ' U2', ' B ', '2D ', ' B ', '2L ', ' B2')
            #SwapE ('2L2', ' B ', '2D2', " B'", ' U2', ' B ', '2D2', ' B ', '2R ', ' B2', '2R2', ' U2', '2L ', ' F2', '2L2', ' F2', ' U2', '2R ', ' U2')

            self.myperms2['WingSwapParallel-K0-'] = ("2L2"," B2","2R'"," F2","2L "," F2"," U2","2L "," U2","2L'"," U2","2R "," U2"," B2","2L2")
            self.myperms2['WingSwapParallel-K1-'] = self.invert_moves(self.myperms2['WingSwapParallel-K0-'])
            

    

            swapc = ('2D2', ' B ', '2R ', " B'", ' R2', ' B ', "2R'", ' B ', '2D ', ' B2', '2D2', ' R2', '2U ', ' F2', '2D2', ' F2', ' R2', "2U'", ' R2')
            swapd = ('2U2', ' B ', "2L'", " B'", ' R2', ' B ', '2L ', ' B ', "2U'", ' B2', '2U2', ' R2', "2D'", ' F2', '2U2', ' F2', ' R2', '2D ', ' R2')
            swapex = ('2U2', " B'", '2R2', ' B ', ' R2', " B'", '2R2', " B'", "2U'", ' B2', '2U2', ' R2', "2D'", ' F2', '2U2', ' F2', ' R2', '2D ', ' R2')
            swapey = ('2D2', " B'", '2L2', ' B ', ' R2', " B'", '2L2', " B'", "2D ", ' B2', '2D2', ' R2', "2U ", ' F2', '2D2', ' F2', ' R2', "2U'", ' R2')
            swapfx = ('2U2', " F'", "2R'", ' F ', ' R2', " F'", '2R ', " F'", "2U'", ' F2', '2U2', ' R2', '2U ', ' F2', '2U2', ' F2', ' R2', '2U ', ' R2')
            swapfy = ('2D2', " F'", '2L ', ' F ', ' R2', " F'", "2L'", " F'", '2D ', ' F2', '2D2', ' R2', "2D'", ' F2', '2D2', ' F2', ' R2', "2D'", ' R2')
            swapg = ('2U2', ' F ', '2L2', " F'", ' R2', ' F ', '2L2', ' F ', "2U'", ' F2', '2U2', ' R2', '2U ', ' F2', '2U2', ' F2', ' R2', '2U ', ' R2')
            swaph = ('2D2', ' F ', '2R2', " F'", ' R2', ' F ', '2R2', ' F ', '2D ', ' F2', '2D2', ' R2', "2D'", ' F2', '2D2', ' F2', ' R2', "2D'", ' R2')

            self.myperms2['WingSwapParallel-IX0-'] = ('2L ', ' F2', "2L'", "2R'", ' F2', '2R ', ' F2', '2R2', ' F2', ' U2', "2R'", ' U2', ' F2', '2R2', ' F2')
            self.myperms2['WingSwapParallel-IX1-'] = ("2R'", ' F2', '2R ', '2L ', ' F2', "2L'", ' F2', '2R2', ' F2', ' U2', "2R'", ' U2', ' F2', '2R2', ' F2')
            self.myperms2['WingSwapParallel-IX2-'] = ('2L ', ' F2', "2L'", "2R'", ' F2', '2R ', ' U2', '2R2', ' U2', ' F2', '2R ', ' F2', ' U2', '2R2', ' U2')
            self.myperms2['WingSwapParallel-IX3-'] = ("2R'", ' F2', '2R ', '2L ', ' F2', "2L'", ' U2', '2R2', ' U2', ' F2', '2R ', ' F2', ' U2', '2R2', ' U2')
            self.myperms2['WingSwapParallel-IX4-'] = ('2L ', ' B2', "2L'", "2R'", ' B2', '2R ', ' B2', '2L2', ' B2', ' D2', "2L'", ' D2', ' B2', '2L2', ' B2')
            self.myperms2['WingSwapParallel-IX5-'] = ("2R'", ' B2', "2R ", "2L ", ' B2', "2L'", ' B2', '2L2', ' B2', ' D2', "2L'", ' D2', ' B2', '2L2', ' B2')
            self.myperms2['WingSwapParallel-IX6-'] = ('2L ', ' B2', "2L'", "2R'", ' B2', '2R ', ' D2', '2L2', ' D2', ' B2', "2L ", ' B2', ' D2', '2L2', ' D2')
            self.myperms2['WingSwapParallel-IX7-'] = ("2R'", ' B2', "2R ", "2L ", ' B2', "2L'", ' D2', '2L2', ' D2', ' B2', "2L ", ' B2', ' D2', '2L2', ' D2')

            self.myperms2['WingSwapParallel-IY0-'] = self.invert_moves((" F2", '2L2', ' B2', ' D2', '2R ', ' D2', ' B2', '2L2', ' F2', '2R ', ' U2', "2R'", "2L'", ' U2', '2L '))
            self.myperms2['WingSwapParallel-IY1-'] = self.invert_moves((" F2", '2L2', ' B2', ' D2', '2R ', ' D2', ' B2', '2L2', ' F2', "2L'", ' U2', '2L ', '2R ', ' U2', "2R'"))
            self.myperms2['WingSwapParallel-IY2-'] = self.invert_moves((" F2", '2L2', ' B2', ' D2', '2R ', ' D2', ' B2', '2L2', ' F2', "2R'", ' F2', "2R ", "2L ", ' F2', "2L'"))
            self.myperms2['WingSwapParallel-IY3-'] = self.invert_moves((" F2", '2L2', ' B2', ' D2', '2R ', ' D2', ' B2', '2L2', ' F2', '2L ', ' F2', "2L'", "2R'", ' F2', '2R '))
            self.myperms2['WingSwapParallel-IY4-'] = self.invert_moves((" F2", '2R2', ' B2', ' D2', '2L ', ' D2', ' B2', '2R2', ' F2', '2R ', ' U2', "2R'", "2L'", ' U2', '2L '))
            self.myperms2['WingSwapParallel-IY5-'] = self.invert_moves((" F2", '2R2', ' B2', ' D2', '2L ', ' D2', ' B2', '2R2', ' F2', "2L'", ' U2', "2L ", "2R ", ' U2', "2R'"))
            self.myperms2['WingSwapParallel-IY6-'] = self.invert_moves((" F2", '2R2', ' B2', ' D2', '2L ', ' D2', ' B2', '2R2', ' F2', "2R'", ' F2', '2R ', '2L ', ' F2', "2L'"))
            self.myperms2['WingSwapParallel-IY7-'] = self.invert_moves((" F2", '2R2', ' B2', ' D2', '2L ', ' D2', ' B2', '2R2', ' F2', "2L ", ' F2', "2L'", "2R'", ' F2', "2R "))




            self.myperms2['WingSwapParallel-I0-'] = ('2L ', ' B2', '2R2', ' U2', '2R ', ' U2', "2R'", "2L'", ' B2', ' D2', "2R'", ' D2', ' B2', '2R2', ' B2')
            self.myperms2['WingSwapParallel-I1-'] = ('2R ', ' D2', '2L2', ' F2', '2L ', ' F2', '2L ', '2R ', ' D2', ' B2', '2R ', ' B2', ' D2', '2R2', ' D2')

            

            self.myperms2['WingSwapParallel-J0-'] = ('2L2', ' D2', ' B2', "2L'", ' B2', '2R ', ' D2', "2R'", ' D2', '2L2', ' B2', '2L ', ' B2', "2L'", ' D2')
            self.myperms2['WingSwapParallel-J1-'] = ('2R2', ' B2', ' D2', "2R'", ' D2', '2R2', "2L'", ' F2', "2L'", ' F2', '2L2', ' D2', '2R ', ' D2', "2R'", ' B2')


      
            self.myperms2['WingSwapParallel-B0-'] = ("2R2", " F2", " U2", "2R ", " U2", "2R2", " F2", "2R ", " U2", "2R2", " U2", " F2", "2R ", " F2")
            self.myperms2['WingSwapParallel-B1-'] = ("2L2", " F2", " U2", "2L ", " U2", "2L2", " F2", "2L'", " U2", "2L2", " U2", " F2", "2L'", " F2")
            self.myperms2['WingSwapParallel-B2-'] = ('2L2', ' F2', ' D2', '2L ', ' D2', '2L2', ' F2', '2R ', ' U2', '2L2', ' U2', ' F2', "2R'", ' F2')
            self.myperms2['WingSwapParallel-B3-'] = ("2R2", " F2", " U2", "2L'", " U2", "2L2", " F2", "2L'", " U2", "2R2", " U2", " F2", "2R ", " F2")
            self.myperms2['WingSwapParallel-B4-'] = ('2R2', ' B2', ' D2', "2L'", ' D2', '2L2', ' B2', "2R'", ' U2', '2R2', ' U2', ' B2', "2L'", ' B2')
            self.myperms2['WingSwapParallel-B5-'] = ('2L2', ' B2', ' D2', "2R'", ' D2', '2R2', ' B2', "2L ", ' U2', '2L2', ' U2', ' B2', "2R ", ' B2')
            self.myperms2['WingSwapParallel-B6-'] = ('2R2', ' F2', ' U2', "2R'", ' U2', '2R2', ' F2', "2L'", '2R2', ' U2', '2L2', ' U2', ' B2', '2R ', ' B2')
            self.myperms2['WingSwapParallel-B7-'] = ('2L2', ' B2', ' D2', '2R2', "2L'", ' D2', '2L2', ' B2', "2R'", ' U2', '2L2', ' U2', ' B2', '2R ', ' B2')
            self.myperms2['WingSwapParallel-B8-'] = ('2L2', ' F2', ' U2', '2L2', '2R ', ' U2', '2R2', ' F2', '2R ', ' U2', '2L2', ' U2', ' F2', "2L'", ' F2')


            self.myperms2['WingSwapParallel-BX00-'] = ('2R2', ' F2', ' U2', '2R ', ' U2', ' F2', '2R2', ' F2', "2R'", ' F2', '2R ', '2L ', ' F2', "2L'", " F2")
            self.myperms2['WingSwapParallel-BX01-'] = ('2R2', ' F2', ' U2', '2R ', ' U2', ' F2', '2R2', ' F2', "2L ", ' F2', "2L'", "2R'", ' F2', "2R ", " F2")
            self.myperms2['WingSwapParallel-BX02-'] = ('2R2', ' B2', ' U2', '2R ', ' U2', ' B2', '2R2', ' B2', '2L ', ' U2', "2L'", "2R'", ' U2', '2R ', ' B2')
            self.myperms2['WingSwapParallel-BX03-'] = ('2R2', ' B2', ' U2', '2R ', ' U2', ' B2', '2R2', ' B2', "2R'", ' U2', "2R ", "2L ", ' U2', "2L'", ' B2')
            self.myperms2['WingSwapParallel-BX04-'] = ('2L2', ' F2', ' U2', '2L ', ' U2', ' F2', '2L2', ' F2', "2R'", ' F2', '2R ', '2L ', ' F2', "2L'", ' F2')
            self.myperms2['WingSwapParallel-BX05-'] = ('2L2', ' F2', ' U2', '2L ', ' U2', ' F2', '2L2', ' F2', "2L ", ' F2', "2L'", "2R'", ' F2', "2R ", ' F2')
            self.myperms2['WingSwapParallel-BX06-'] = ('2L2', ' B2', ' U2', '2L ', ' U2', ' B2', '2L2', ' B2', '2L ', ' U2', "2L'", "2R'", ' U2', '2R ', ' B2')
            self.myperms2['WingSwapParallel-BX07-'] = ('2L2', ' B2', ' U2', '2L ', ' U2', ' B2', '2L2', ' B2', "2R'", ' U2', "2R ", "2L ", ' U2', "2L'", ' B2')

            self.myperms2['WingSwapParallel-BY00-'] = ('2L2', ' B2', ' D2', '2R ', ' D2', ' B2', '2L2', ' F2', '2R ', ' U2', "2R'", "2L'", ' U2', '2L ', ' F2')
            self.myperms2['WingSwapParallel-BY01-'] = ('2L2', ' B2', ' D2', '2R ', ' D2', ' B2', '2L2', ' F2', "2L'", ' U2', '2L ', '2R ', ' U2', "2R'", ' F2')
            self.myperms2['WingSwapParallel-BY02-'] = ('2L2', ' B2', ' D2', '2R ', ' D2', ' B2', '2L2', ' F2', "2R'", ' F2', "2R ", "2L ", ' F2', "2L'", ' F2')
            self.myperms2['WingSwapParallel-BY03-'] = ('2L2', ' B2', ' D2', '2R ', ' D2', ' B2', '2L2', ' F2', '2L ', ' F2', "2L'", "2R'", ' F2', '2R ', ' F2')
            self.myperms2['WingSwapParallel-BY04-'] = ('2R2', ' B2', ' D2', '2L ', ' D2', ' B2', '2R2', ' F2', '2R ', ' U2', "2R'", "2L'", ' U2', '2L ', ' F2')
            self.myperms2['WingSwapParallel-BY05-'] = ('2R2', ' B2', ' D2', '2L ', ' D2', ' B2', '2R2', ' F2', "2L'", ' U2', "2L ", "2R ", ' U2', "2R'", ' F2')
            self.myperms2['WingSwapParallel-BY06-'] = ('2R2', ' B2', ' D2', '2L ', ' D2', ' B2', '2R2', ' F2', "2R'", ' F2', '2R ', '2L ', ' F2', "2L'", ' F2')
            self.myperms2['WingSwapParallel-BY07-'] = ('2R2', ' B2', ' D2', '2L ', ' D2', ' B2', '2R2', ' F2', "2L ", ' F2', "2L'", "2R'", ' F2', "2R ", ' F2')

            #('2L2', ' F2', ' D2', "2R'", ' D2', ' B2', '2L2', ' B2', '2R ', ' D2', "2L'", "2R'", ' D2', '2R ', ' F2')




            self.myperms2['WingSwapSkew-C'] = swapc
            self.myperms2['WingSwapSkew-D'] = swapd
            self.myperms2['WingSwapSkew-Ex'] = swapex
            self.myperms2['WingSwapSkew-Ey'] = swapey
            self.myperms2['WingSwapSkew-Fx'] = swapfx
            self.myperms2['WingSwapSkew-Fy'] = swapfy
            self.myperms2['WingSwapSkew-G'] = swapg
            self.myperms2['WingSwapSkew-H'] = swaph

            self.myperms2['WingSwapSkewViaEdge-XK00-'] = self.simplify(self.myperms2['Wing3-SameEdgePairPlus1-K00-'] + perm_kB)
            self.myperms2['WingSwapSkewViaEdge-XK01-'] = self.simplify(self.myperms2['Wing3-SameEdgePairPlus1-K01-'] + perm_kB)
            self.myperms2['WingSwapSkewViaEdge-XK02-'] = self.simplify(self.myperms2['Wing3-SameEdgePairPlus1-K02-'] + perm_kB)
            self.myperms2['WingSwapSkewViaEdge-XK03-'] = self.simplify(self.myperms2['Wing3-SameEdgePairPlus1-K03-'] + perm_kB)
            self.myperms2['WingSwapSkewViaEdge-XK04-'] = self.simplify(self.myperms2['Wing3-SameEdgePairPlus1-K04-'] + perm_kB)
            self.myperms2['WingSwapSkewViaEdge-XK05-'] = self.simplify(self.myperms2['Wing3-SameEdgePairPlus1-K05-'] + perm_kB)
            self.myperms2['WingSwapSkewViaEdge-XK06-'] = self.simplify(self.myperms2['Wing3-SameEdgePairPlus1-K06-'] + perm_kB)
            self.myperms2['WingSwapSkewViaEdge-XK07-'] = self.simplify(self.myperms2['Wing3-SameEdgePairPlus1-K07-'] + perm_kB)

            self.myperms2['WingSwapSkewViaEdge-XK08-'] = self.simplify(self.myperms2['Wing3-SameEdgePairPlus1-K00-'] + perm_kC)
            self.myperms2['WingSwapSkewViaEdge-XK09-'] = self.simplify(self.myperms2['Wing3-SameEdgePairPlus1-K01-'] + perm_kC)
            self.myperms2['WingSwapSkewViaEdge-XK10-'] = self.simplify(self.myperms2['Wing3-SameEdgePairPlus1-K02-'] + perm_kC)
            self.myperms2['WingSwapSkewViaEdge-XK11-'] = self.simplify(self.myperms2['Wing3-SameEdgePairPlus1-K03-'] + perm_kC)
            self.myperms2['WingSwapSkewViaEdge-XK12-'] = self.simplify(self.myperms2['Wing3-SameEdgePairPlus1-K04-'] + perm_kC)
            self.myperms2['WingSwapSkewViaEdge-XK13-'] = self.simplify(self.myperms2['Wing3-SameEdgePairPlus1-K05-'] + perm_kC)
            self.myperms2['WingSwapSkewViaEdge-XK14-'] = self.simplify(self.myperms2['Wing3-SameEdgePairPlus1-K06-'] + perm_kC)
            self.myperms2['WingSwapSkewViaEdge-XK15-'] = self.simplify(self.myperms2['Wing3-SameEdgePairPlus1-K07-'] + perm_kC)
            
            self.myperms2['WingSwapSkewViaEdge-XI00-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-I00C-'] + self.myperms2['WingSwapParallel-IX0-'])
            self.myperms2['WingSwapSkewViaEdge-XI01-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-I01C-'] + self.myperms2['WingSwapParallel-IX1-'])
            self.myperms2['WingSwapSkewViaEdge-XI02-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-I02C-'] + self.myperms2['WingSwapParallel-IX2-'])
            self.myperms2['WingSwapSkewViaEdge-XI03-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-I03C-'] + self.myperms2['WingSwapParallel-IX3-'])
            self.myperms2['WingSwapSkewViaEdge-XI04-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-I04C-'] + self.myperms2['WingSwapParallel-IX4-'])
            self.myperms2['WingSwapSkewViaEdge-XI05-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-I05C-'] + self.myperms2['WingSwapParallel-IX5-'])
            self.myperms2['WingSwapSkewViaEdge-XI06-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-I06C-'] + self.myperms2['WingSwapParallel-IX6-'])
            self.myperms2['WingSwapSkewViaEdge-XI07-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-I07C-'] + self.myperms2['WingSwapParallel-IX7-'])

            self.myperms2['WingSwapSkewViaEdge-XI08-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-I00C-'] + self.myperms2['WingSwapParallel-IY0-'])
            self.myperms2['WingSwapSkewViaEdge-XI09-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-I01C-'] + self.myperms2['WingSwapParallel-IY1-'])
            self.myperms2['WingSwapSkewViaEdge-XI10-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-I02C-'] + self.myperms2['WingSwapParallel-IY2-'])
            self.myperms2['WingSwapSkewViaEdge-XI11-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-I03C-'] + self.myperms2['WingSwapParallel-IY3-'])
            self.myperms2['WingSwapSkewViaEdge-XI12-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-I04C-'] + self.myperms2['WingSwapParallel-IY4-'])
            self.myperms2['WingSwapSkewViaEdge-XI13-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-I05C-'] + self.myperms2['WingSwapParallel-IY5-'])
            self.myperms2['WingSwapSkewViaEdge-XI14-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-I06C-'] + self.myperms2['WingSwapParallel-IY6-'])
            self.myperms2['WingSwapSkewViaEdge-XI15-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-I07C-'] + self.myperms2['WingSwapParallel-IY7-'])

            self.myperms2['WingSwapSkewViaEdge-XJ00-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-J00-'] + perm_j0)
            self.myperms2['WingSwapSkewViaEdge-XJ01-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-J01-'] + perm_j0)
            self.myperms2['WingSwapSkewViaEdge-XJ02-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-J02-'] + perm_j0)
            self.myperms2['WingSwapSkewViaEdge-XJ03-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-J03-'] + perm_j0)
            self.myperms2['WingSwapSkewViaEdge-XJ04-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-J04-'] + perm_j0)
            self.myperms2['WingSwapSkewViaEdge-XJ05-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-J05-'] + perm_j0)
            self.myperms2['WingSwapSkewViaEdge-XJ06-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-J06-'] + perm_j0)
            self.myperms2['WingSwapSkewViaEdge-XJ07-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-J07-'] + perm_j0)

            self.myperms2['WingSwapSkewViaEdge-XJ08-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-J00-'] + perm_j2)
            self.myperms2['WingSwapSkewViaEdge-XJ09-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-J01-'] + perm_j2)
            self.myperms2['WingSwapSkewViaEdge-XJ10-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-J02-'] + perm_j2)
            self.myperms2['WingSwapSkewViaEdge-XJ11-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-J03-'] + perm_j2)
            self.myperms2['WingSwapSkewViaEdge-XJ12-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-J04-'] + perm_j2)
            self.myperms2['WingSwapSkewViaEdge-XJ13-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-J05-'] + perm_j2)
            self.myperms2['WingSwapSkewViaEdge-XJ14-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-J06-'] + perm_j2)
            self.myperms2['WingSwapSkewViaEdge-XJ15-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-J07-'] + perm_j2)


            self.myperms2['WingSwapSkewViaEdge-XA00-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-A00-'] + self.myperms2['WingSwapParallel-A0-'])
            self.myperms2['WingSwapSkewViaEdge-XA01-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-A01-'] + self.myperms2['WingSwapParallel-A0-'])
            self.myperms2['WingSwapSkewViaEdge-XA02-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-A02-'] + self.myperms2['WingSwapParallel-A1-'])
            self.myperms2['WingSwapSkewViaEdge-XA03-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-A03-'] + self.myperms2['WingSwapParallel-A1-'])
            self.myperms2['WingSwapSkewViaEdge-XA04-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-A04-'] + self.myperms2['WingSwapParallel-A0-'])
            self.myperms2['WingSwapSkewViaEdge-XA05-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-A05-'] + self.myperms2['WingSwapParallel-A0-'])
            self.myperms2['WingSwapSkewViaEdge-XA06-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-A06-'] + self.myperms2['WingSwapParallel-A1-'])
            self.myperms2['WingSwapSkewViaEdge-XA07-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-A07-'] + self.myperms2['WingSwapParallel-A1-'])

            self.myperms2['WingSwapSkewViaEdge-XA08-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-A00-'] + self.myperms2['WingSwapParallel-A2-'])
            self.myperms2['WingSwapSkewViaEdge-XA09-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-A01-'] + self.myperms2['WingSwapParallel-A2-'])
            self.myperms2['WingSwapSkewViaEdge-XA10-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-A02-'] + self.myperms2['WingSwapParallel-A3-'])
            self.myperms2['WingSwapSkewViaEdge-XA11-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-A03-'] + self.myperms2['WingSwapParallel-A3-'])
            self.myperms2['WingSwapSkewViaEdge-XA12-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-A04-'] + self.myperms2['WingSwapParallel-A2-'])
            self.myperms2['WingSwapSkewViaEdge-XA13-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-A05-'] + self.myperms2['WingSwapParallel-A2-'])
            self.myperms2['WingSwapSkewViaEdge-XA14-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-A06-'] + self.myperms2['WingSwapParallel-A3-'])
            self.myperms2['WingSwapSkewViaEdge-XA15-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-A07-'] + self.myperms2['WingSwapParallel-A3-'])


            self.myperms2['WingSwapSkewViaEdge-XB00-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-B00-'] + self.myperms2['WingSwapParallel-BX00-'])
            self.myperms2['WingSwapSkewViaEdge-XB01-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-B01-'] + self.myperms2['WingSwapParallel-BX01-'])
            self.myperms2['WingSwapSkewViaEdge-XB02-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-B02-'] + self.myperms2['WingSwapParallel-BX02-'])
            self.myperms2['WingSwapSkewViaEdge-XB03-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-B03-'] + self.myperms2['WingSwapParallel-BX03-'])
            self.myperms2['WingSwapSkewViaEdge-XB04-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-B04-'] + self.myperms2['WingSwapParallel-BX04-'])
            self.myperms2['WingSwapSkewViaEdge-XB05-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-B05-'] + self.myperms2['WingSwapParallel-BX05-'])
            self.myperms2['WingSwapSkewViaEdge-XB06-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-B06-'] + self.myperms2['WingSwapParallel-BX06-'])
            self.myperms2['WingSwapSkewViaEdge-XB07-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-B07-'] + self.myperms2['WingSwapParallel-BX07-'])

            self.myperms2['WingSwapSkewViaEdge-XB08-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-B00-'] + self.myperms2['WingSwapParallel-BY00-'])
            self.myperms2['WingSwapSkewViaEdge-XB09-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-B01-'] + self.myperms2['WingSwapParallel-BY01-'])
            self.myperms2['WingSwapSkewViaEdge-XB10-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-B02-'] + self.myperms2['WingSwapParallel-BY02-'])
            self.myperms2['WingSwapSkewViaEdge-XB11-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-B03-'] + self.myperms2['WingSwapParallel-BY03-'])
            self.myperms2['WingSwapSkewViaEdge-XB12-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-B04-'] + self.myperms2['WingSwapParallel-BY04-'])
            self.myperms2['WingSwapSkewViaEdge-XB13-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-B05-'] + self.myperms2['WingSwapParallel-BY05-'])
            self.myperms2['WingSwapSkewViaEdge-XB14-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-B06-'] + self.myperms2['WingSwapParallel-BY06-'])
            self.myperms2['WingSwapSkewViaEdge-XB15-'] = self.simplify(self.myperms2['Wing3-Parallel2Plus1-B07-'] + self.myperms2['WingSwapParallel-BY07-'])


            
            




            if self.size % 2 == 1:
                self.myperms2['CenterQXA-'] = (" S2","2R2"," S2","2R2")
                self.myperms2['CenterQXB-'] = (" U "," S2","2R2"," S2","2R2"," U'")
                self.myperms2['CenterQY-'] = (" E ","2R2"," E'","2R2")
                self.myperms2['CenterQZ-'] = ('2B ', " E'", '2B2', ' E ', '2B ')
                self.myperms2['CenterQWA-'] = ("2L2"," E2","2L'"," U ","2R'"," E2","2R "," U'","2L'")
                self.myperms2['CenterQWB-'] = ("2R2"," E2","2R "," U ","2L "," E2","2L'"," U'","2R ")
                self.myperms2['CenterQU-'] = ('2R ', ' S2', '2R2', ' S2', '2R ')
                self.myperms2['CenterQV-'] = (" E'", "2B'", ' E ', '2B2', " E'", "2B'", ' E ')
                self.myperms2['CenterQTA-'] = (' M ', '2U2', " M'", '2U ', ' S ', '2U2', " S'", "2U'")
                self.myperms2['CenterQTB-'] = (" U ","2L'", " E'", '2B ', ' E ', "2B'", '2L ', '2B2', ' E2', '2B ', ' E2', '2B '," U'")
                self.myperms2['CenterQTC-'] = (' S2', ' M2', ' D ', '2F2', " D'", ' S2', ' M2', ' D ', '2F2', " D'")

                
                self.myperms2['CenterQ6A-'] = ("2R "," E ","2R'"," E'")
                self.myperms2['CenterQ6B-'] = (" E ","2R "," E'","2R'")                
                self.myperms2['CenterQ6C-'] = ("2R "," E2","2R'"," E2")
                self.myperms2['CenterQ6D-'] = (" E2","2R'"," E2","2R ")
                self.myperms2['CenterQ6E-'] = ('2U ', " M'", '2B ', ' M ', "2B'", "2U'", " E'", "2F'", " E'", '2F ', ' E2')
                self.myperms2['CenterQ6F-'] = ('2U ', ' S ', '2R ', " S'", " E'", '2F ', ' E ', "2F'", "2R'", "2U'")
                self.myperms2['CenterQ6G-'] = ("2R "," E ","2R "," E'","2R2")
                self.myperms2['CenterQ6H-'] = ("2R2"," E'","2R'"," E ","2R'")
                self.myperms2['CenterQ6I-'] = (" M ","2U "," M ","2U'"," M2")
                self.myperms2['CenterQ6J-'] = (" M2","2U'"," M'","2U "," M'")                



                self.myperms2['CenterQ4A-'] = ("2R2"," E2","2R "," E2","2R ")
                self.myperms2['CenterQ4B-'] = ("2R "," E2","2R "," E2","2R2")
                self.myperms2['CenterQ4C-'] = ("2U "," S ","2R "," S'","2R'","2U'")
                self.myperms2['CenterQ4D-'] = (" M'", "2B'", ' M2', "2U'", " M'", '2U ', '2B ')
                self.myperms2['CenterQ4E-'] = ('2U ', " M'", '2U ', " M'", "2U'", ' M2', "2U'")
                self.myperms2['CenterQ4XA-'] = ("2L'"," U ","2R'"," E2","2R "," U'"," E2","2L ")
                self.myperms2['CenterQ4XB-'] = ("2L'"," D'","2R'"," E2","2R "," D "," E2","2L ")
                self.myperms2['CenterQ4YA-'] = ("2B "," U'","2R "," E'","2R'"," U "," E ","2B'")
                self.myperms2['CenterQ4YB-'] = ("2B "," D ","2R "," E'","2R'"," D'"," E ","2B'")                
                self.myperms2['CenterQ4YC-'] = ('2L ', " U'", '2R ', ' E2', "2R'", " U ", ' E2', "2L'")
                self.myperms2['CenterQ4YD-'] = ('2L ', ' D ', '2R ', ' E2', "2R'", " D'", ' E2', "2L'")
                self.myperms2['CenterQ4ZA-'] = (' U2', '2R ', ' E2', '2R ', ' E2', '2R2', ' U2')
                self.myperms2['CenterQ4ZB-'] = (' D2', '2R ', ' E2', '2R ', ' E2', '2R2', ' D2')
                self.myperms2['CenterQ4ZC-'] = (' U2', '2R ', ' E2', "2R'", ' U2', '2L2', ' E2', '2L2')
                self.myperms2['CenterQ4ZD-'] = (' D2', '2R ', ' E2', "2R'", ' D2', '2L2', ' E2', '2L2')
                self.myperms2['CenterQ4WA-'] = ('2L ', ' E2', ' D ', '2R ', ' E2', "2R'", " D'", "2L'")
                self.myperms2['CenterQ4WB-'] = ('2L ', ' E2', " U'", '2R ', ' E2', "2R'", " U ", "2L'")


                self.myperms2['BigCenter-BOpp-'] = (" M2","2F2"," M2","2F2"," S2","2R2"," S2","2R2")
                self.myperms2['BigCenter-BNbr-'] = ("2R "," U "," M'"," U'","2R'"," U "," M "," U2","2R "," U "," M'"," U'","2R'"," U "," M2",
                                                   " F'","2L "," F "," M'"," F'","2L'"," F2"," M "," F'","2L "," F "," M'"," F'","2L'")


                self.myperms2['BigCenter-BCyc3-'] = self.myperms2['BigCenter-BNbr-'] + self.transform(self.myperms2['BigCenter-BNbr-'],1)
                self.myperms2['BigCenter-BCyc4-'] = self.myperms2['BigCenter-BNbr-'] + self.transform(self.myperms2['BigCenter-BNbr-'],3) + self.transform(self.myperms2['BigCenter-BNbr-'],14)
                self.myperms2['BigCenter-BSwap2-'] = self.myperms2['BigCenter-BNbr-'] + self.transform(self.myperms2['BigCenter-BNbr-'],29)


                self.myperms2['MidBar(VV)'] = (" M'"," U "," L "," R'"," M "," F'"," M "," F "," L'"," R "," M'"," U'")
                self.myperms2['MidBar(HV)'] = (' U ', ' M ', " R'", ' L ', " F'", " M'", ' F ', " M'", ' R ', " L'", " U'", ' M ')
                self.myperms2['MidBar(HH)'] = (' M ', " R'", ' L ', " F'", " M'", ' F ', " M'", ' R ', " L'", " U'", ' M ',' U ')

                self.myperms2['MidBar-Opp(VV)'] = (" M2"," U "," L2"," R2"," M2"," D'"," M2"," D "," L2"," R2"," M2"," U'")
                self.myperms2['MidBar-Opp(HV)'] = (' U ', ' M2', " R2", ' L2', " D'", " M2", ' D ', " M2", ' R2', " L2", " U'", ' M2')

                self.myperms2['MidBar-3A'] = (" F "," U "," L "," R'"," M "," F'"," M "," F "," L'"," R "," M'"," U'"," M'"," F'")
                self.myperms2['MidBar-3B'] = (" U "," L "," R'"," M "," F'"," M "," F "," L'"," R "," M'"," U'"," M'")
                self.myperms2['MidBar-3C'] = (' F ',' L '," R'",' M '," F'",' M ',' F '," L'",' R '," M'"," U'"," M'",' U '," F'")
                self.myperms2['MidBar-3D'] = (" L "," R'"," M "," F'"," M "," F "," L'"," R "," M'"," U'"," M'"," U ")                
                self.myperms2['MidBar-3E'] = (" B'"," F "," U "," L "," R'"," M "," F'"," M "," F "," L'"," R "," M'"," U'"," M'"," F'"," B ")
                self.myperms2['MidBar-3F'] = (" B'"," U "," L "," R'"," M "," F'"," M "," F "," L'"," R "," M'"," U'"," M'"," B ")
                self.myperms2['MidBar-3G'] = (' B '," F'"," R'",' L ',' M ',' F ',' M '," F'",' R '," L'"," M'",' U '," M'"," U'",' F '," B'")
                self.myperms2['MidBar-3H'] = (" B'"," L "," R'"," M "," F'"," M "," F "," L'"," R "," M'"," U'"," M'"," U "," B ")

                self.myperms2['MidBar-3OA'] = (" E'"," U'"," M'"," U "," L "," R'"," M "," F'"," M "," F "," L'"," R "," M'"," E ")
                self.myperms2['MidBar-3OB'] = self.invert_moves(self.myperms2['MidBar-3OA'])
                self.myperms2['MidBar-3OC'] = (" E'"," M'"," U "," L "," R'"," M "," F'"," M "," F "," L'"," R "," M'"," U'"," E ")
                self.myperms2['MidBar-3OD'] = self.invert_moves(self.myperms2['MidBar-3OC'])


                if self.size >= 6:
                    self.myperms2['BigCenter-BOppW-'] = self.myperms2['BigCenter-BOpp-'] + self.transform(self.myperms2['BigCenter-BOpp-'],48)
                    self.myperms2['BigCenter-BNbrW-'] = self.myperms2['BigCenter-BNbr-'] + self.transform(self.myperms2['BigCenter-BNbr-'],48)


                    self.myperms2['BigCenter-BCyc3W-'] = self.myperms2['BigCenter-BNbrW-'] + self.transform(self.myperms2['BigCenter-BNbrW-'],1)
                    self.myperms2['BigCenter-BCyc4W-'] = self.myperms2['BigCenter-BNbrW-'] + self.transform(self.myperms2['BigCenter-BNbrW-'],3) + self.transform(self.myperms2['BigCenter-BNbrW-'],14)
                    self.myperms2['BigCenter-BSwap2W-'] = self.myperms2['BigCenter-BNbrW-'] + self.transform(self.myperms2['BigCenter-BNbrW-'],29)




                self.myperms2['CenterB-OppX'] = (" U ", '2R2', " U'", ' S2', ' U ', '2R2', " U'", ' S2')
                self.myperms2['CenterB-OppX(1)'] = (' U ', '2R2', " U'", ' M2', ' U ', '2R2', " U'", ' M2')
                self.myperms2['CenterB-OppX(2)'] = ('2F2', ' D ', ' M2', '2F2', ' M2', '2F2', " D'", '2F2')
                self.myperms2['CenterB-OppY'] = ('2R2', " U'", ' S2', ' U ', '2R2', " U'", ' S2', ' U ')
                self.myperms2['CenterB-OppY(1)'] = ('2R2', " U'", ' M2', ' U ', '2R2', " U'", ' M2', ' U ')
                self.myperms2['CenterB-OppZ'] = (" M2"," U ","2F2"," U'"," M2"," U ","2F2"," U'")
                self.myperms2['CenterB-OppZ(1)'] = (' M2', ' U ', '2R2', " U'", ' M2', ' U ', '2R2', " U'")
                

                self.myperms2['CenterB-MI(0)'] = (" S'", '2U ', ' S ', " U2", " S'", "2U'", ' S ', " U2")
                self.myperms2['CenterB-MO(0)'] = (" S'", '2U ', ' S ', " D2", " S'", "2U'", ' S ', " D2")
                self.myperms2['CenterB-MV(0)'] = ('2R ', ' E2', "2R'", " U2", '2R ', ' E2', "2R'", " U2")
                self.myperms2['CenterB-MV(1)'] = ('2R ', ' E2', "2R'", " D2", '2R ', ' E2', "2R'", " D2")
                self.myperms2['CenterB-MV(2)'] = ("2R "," U "," M'"," U'","2R'"," U "," M "," U'")
                self.myperms2['CenterB-MV(3)'] = ("2L'"," U "," M'"," U'","2L "," U "," M "," U'")
                self.myperms2['CenterB-MV(4)'] = (" E'"," L2"," E ","2R'"," E'"," L2"," E ","2R ")
                self.myperms2['CenterB-MV(5)'] = (" S'", ' L2', ' S ', "2L'", " S'", ' L2', ' S ', '2L ')

                
                self.myperms2['CenterB-MD(0)'] = (' U2', '2R ', ' E2', "2R'", " U2", '2R ', ' E2', "2R'")
                self.myperms2['CenterB-MD(1)'] = (" D2", '2R ', ' E2', "2R'", " D2", '2R ', ' E2', "2R'")
                self.myperms2['CenterB-MD(2)'] = ("2R'"," E'"," L2"," E ","2R "," E'"," L2"," E ")
                self.myperms2['CenterB-MD(3)'] = ("2L'", " S'", ' L2', ' S ', '2L ', " S'", ' L2', ' S ')

                self.myperms2['CenterB-MI(1)'] = (" U2", " S'", '2U ', ' S ', " U2", " S'", "2U'", ' S ')
                self.myperms2['CenterB-MO(1)'] = (" D2", " S'", '2U ', ' S ', " D2", " S'", "2U'", ' S ')

                self.myperms2['CenterB-MI(2)'] = (' U2', '2F ', ' E ', "2F'", ' U2', '2F ', " E'", "2F'")
                self.myperms2['CenterB-MO(2)'] = (' D2', '2F ', ' E ', "2F'", ' D2', '2F ', " E'", "2F'")

                self.myperms2['CenterB-MI(3)'] = (" U ", " M'", " U'", "2L'", " U ", ' M ', " U'", '2L ')
                self.myperms2['CenterB-MO(3)'] = (" U ", " M'", " U'", "2R ", " U ", ' M ', " U'", "2R'")

                self.myperms2['CenterB-MI(4)'] = (" F'", '2L ', ' F ', ' M ', " F'", "2L'", ' F ', " M'")
                self.myperms2['CenterB-MO(4)'] = (" F'", "2R'", ' F ', ' M ', " F'", "2R ", ' F ', " M'")




                self.myperms2['CenterB-IO(0)'] = (" U2","2D'"," M'","2D "," M "," U2"," M'","2D'"," M ","2D ")
                self.myperms2['CenterB-IO(1)'] = (" U2","2U "," M'","2U'"," M "," U2"," M'","2U "," M ","2U'")
                self.myperms2['CenterB-IO(2)'] = (" M'"," U ","2R "," U'"," M "," U ","2R'"," U'")
                self.myperms2['CenterB-IO(3)'] = (" M'"," U ","2L'"," U'"," M "," U ","2L "," U'")                
                self.myperms2['CenterB-OO(0)'] = ("2D'"," M'","2D "," M "," U2"," M'","2D'"," M ","2D "," U2")
                self.myperms2['CenterB-II(0)'] = ("2U "," M'","2U'"," M "," U2"," M'","2U "," M ","2U'"," U2")

                self.myperms2['CenterB-3AAA(0)'] = (" F ","2D "," R2","2D'"," M ","2D "," R2","2D'"," M'"," F'")
                self.myperms2['CenterB-3CCC(0)'] = (" F ","2U'"," R2","2U "," M ","2U'"," R2","2U "," M'"," F'")
                self.myperms2['CenterB-3BBB(0)'] = (" F'"," E'","2L'"," U2","2L "," E ","2L'"," U2","2L "," F ")
                self.myperms2['CenterB-3DDD(0)'] = (" F'"," E'","2R "," U2","2R'"," E ","2R "," U2","2R'"," F ")

                self.myperms2['CenterB-3AAC(0)'] = (" F'","2D "," R2","2D'"," M ","2D "," R2","2D'"," M'"," F ")
                self.myperms2['CenterB-3CCA(0)'] = (" F'","2U'"," R2","2U "," M ","2U'"," R2","2U "," M'"," F ")
                self.myperms2['CenterB-3BBD(0)'] = (" F "," E'","2L'"," U2","2L "," E ","2L'"," U2","2L "," F'")
                self.myperms2['CenterB-3DDB(0)'] = (" F "," E'","2R "," U2","2R'"," E ","2R "," U2","2R'"," F'")
            
                self.myperms2['CenterB-3AAD(0)'] = ("2D "," R2","2D'"," M ","2D "," R2","2D'"," M'")
                self.myperms2['CenterB-3CCB(0)'] = ("2U'"," R2","2U "," M ","2U'"," R2","2U "," M'")
                self.myperms2['CenterB-3BBC(0)'] = (" E'","2L'"," U2","2L "," E ","2L'"," U2","2L ")
                self.myperms2['CenterB-3DDA(0)'] = (" E'","2R "," U2","2R'"," E ","2R "," U2","2R'")

                self.myperms2['CenterB-3DDC(0)'] = ('2L2', " F'", ' E ', ' F ', '2L ', " F'", " E'", ' F ', '2L ')
                self.myperms2['CenterB-3BBA(0)'] = ('2R2', " F'", ' E ', ' F ', "2R'", " F'", " E'", ' F ', "2R'")
                self.myperms2['CenterB-3CCD(0)'] = ('2D ', ' F ', " M'", " F'", '2D ', ' F ', ' M ', " F'", '2D2')
                self.myperms2['CenterB-3AAB(0)'] = ("2U'", ' F ', " M'", " F'", "2U'", ' F ', ' M ', " F'", '2U2')
                

                self.myperms2['CenterB-3ADC(0)'] = ("2L'"," D'"," S'",' D ','2L '," D'",' S ',' D ')
                self.myperms2['CenterB-3CBA(0)'] = ("2R "," D'"," S'",' D ',"2R'"," D'"," S ",' D ')
                self.myperms2['CenterB-3BAD(0)'] = (" M'", ' D ', "2F'", " D'", ' M ', ' D ', "2F ", " D'")
                self.myperms2['CenterB-3DCB(0)'] = (" M'", ' D ', '2B ', " D'", ' M ', ' D ', "2B'", " D'")

                self.myperms2['CenterB-3ABC(0)'] = (" U2","2L'"," D'"," S'",' D ','2L '," D'",' S ',' D '," U2")
                self.myperms2['CenterB-3CDA(0)'] = (" U2","2R "," D'"," S'",' D ',"2R'"," D'"," S ",' D '," U2")
                self.myperms2['CenterB-3BCD(0)'] = (" U2"," M'", "2F'", ' M ', ' U ', " M'", " U'", '2F ', ' U ', ' M ', " U ")
                self.myperms2['CenterB-3DAB(0)'] = (" U2"," M'", "2B ", ' M ', ' U ', " M'", " U'", "2B'", ' U ', ' M ', " U ")

                self.myperms2['CenterB-3V-BBA(0)'] = ("2R "," U "," M "," U'","2R'"," U "," M'"," U'")
                self.myperms2['CenterB-3V-BBC(0)'] = ('2R '," U'",' M ',' U ',"2R'"," U'"," M'",' U ')
                self.myperms2['CenterB-3V-BDC(0)'] = (" U2","2L'"," U "," M "," U'","2L "," U "," M'"," U ")
                self.myperms2['CenterB-3V-BDA(0)'] = (" U2","2L'"," U'",' M ',' U ',"2L "," U'"," M'"," U'")
                self.myperms2['CenterB-3V-BAB(0)'] = ("2R ", ' F ', ' E2', " F'", "2R'", ' F ', ' E2', " F'")
                self.myperms2['CenterB-3V-BCB(0)'] = ("2R ", " F'", ' E2', " F ", "2R'", " F'", ' E2', " F ")

                self.myperms2['CenterB-3V-ABB(0)'] = ("2R2"," F "," M "," F'","2R2"," F "," M'"," F'")
                self.myperms2['CenterB-3V-CBB(0)'] = ("2R2"," F'"," M "," F ","2R2"," F'"," M'"," F ")
                self.myperms2['CenterB-3V-CAB(0)'] = (" F'","2R2"," F'"," M "," F ","2R2"," F'"," M'"," F2")
                self.myperms2['CenterB-3V-ACB(0)'] = (" F ","2R2"," F "," M "," F'","2R2"," F "," M'"," F2")

                self.myperms2['CenterB-3V-AAB(0)'] = (" M'"," U'","2R'"," U "," M "," U'","2R "," U ")
                self.myperms2['CenterB-3V-CCB(0)'] = (" M'"," U ","2R'"," U'"," M "," U ","2R "," U'")
                self.myperms2['CenterB-3V-ABA(0)'] = (" M'", " F'", '2U2', ' F ', ' M ', " F'", '2U2', ' F ')
                self.myperms2['CenterB-3V-CBC(0)'] = (" M'", ' F ', '2D2', " F'", ' M ', ' F ', '2D2', " F'")

                self.myperms2['CenterB-3V-BAA(0)'] = (" M2"," F'","2R'"," F "," M2"," F'","2R "," F ")
                self.myperms2['CenterB-3V-BCC(0)'] = (" M2"," F ","2R'"," F'"," M2"," F ","2R "," F'")

                self.myperms2['CenterB-3V-BDD(0)'] = ("2L ", " S ", ' R2', " S'", '2L2', " S ", ' R2', " S'", "2L ")
                self.myperms2['CenterB-3V-BBB(0)'] = ('2L ', ' E2', "2L'", ' U2', '2L ', ' E2', '2L2', ' E2', '2L ', ' U2', "2L'", ' E2', '2L ')
                self.myperms2['CenterB-3V-BDB(0)'] = (' E2', "2L'", ' U2', '2L ', ' E2', "2L'", ' U2', '2L ')
                self.myperms2['CenterB-3V-BBD(0)'] = ('2L ', ' U2', "2L'", ' E2', '2L ', ' U2', "2L'", ' E2')
                self.myperms2['CenterB-3V-BCA(0)'] = (" S ", "2U ", " S'", ' U2', " S ", '2U2', " S'", ' U2', " S ", "2U ", " S'")
                self.myperms2['CenterB-3V-BAC(0)'] = (" S'", '2D ', ' S ', ' U2', " S'", '2D2', ' S ', ' U2', " S'", '2D ', ' S ')

                self.myperms2['CenterB-3V-CCA(0)'] = ("2U2"," B "," M "," B'","2U2"," B "," M'"," B'")
                self.myperms2['CenterB-3V-AAC(0)'] = ("2D2"," B "," M "," B'","2D2"," B "," M'"," B'")
                self.myperms2['CenterB-3V-ACA(0)'] = (' F ', " M'", " F'", '2U2', ' F ', ' M ', " F'", '2U2')
                self.myperms2['CenterB-3V-CAC(0)'] = (' F ', " M'", " F'", '2D2', ' F ', ' M ', " F'", '2D2')
                self.myperms2['CenterB-3V-CCC(0)'] = (" B2","2U2"," B "," M "," B'","2U2"," B "," M'"," B ")
                self.myperms2['CenterB-3V-AAA(0)'] = (" B2","2D2"," B "," M "," B'","2D2"," B "," M'"," B ")

                self.myperms2['CenterB-3V-ABD(0)'] = (' E2', '2R ', " U'", "2R'", ' E2', '2R ', ' U ', "2R'")
                self.myperms2['CenterB-3V-CBD(0)'] = (' E2', '2R ', ' U ', "2R'", ' E2', '2R ', " U'", "2R'")
                
            if self.size >= 6:
                self.myperms2['CenterRXA-'] = ("2R2","3F2","2R2","3F2")
                self.myperms2['CenterRXB-'] = (" U ","2R2","3F2","2R2","3F2"," U'")
                self.myperms2['CenterRXC-'] = (" U2","2R2","3F2","2R2","3F2"," U2")
                self.myperms2['CenterRWA-'] = ("2L2","3D2","2L'"," U ","2R'","3D2","2R "," U'","2L'")
                self.myperms2['CenterRWB-'] = ("2R2","3U2","2R "," U ","2L ","3U2","2L'"," U'","2R ")
                self.myperms2['CenterRWC-'] = ("2L2","3U2","2L'"," U ","2R'","3U2","2R "," U'","2L'")
                self.myperms2['CenterRWD-'] = ("2R2","3D2","2R "," U ","2L ","3D2","2L'"," U'","2R ")
                self.myperms2['CenterRVA-'] = ('2L2', ' U ', '2L2', '3B2', '2L2', " U'", '2L2', ' U ', '3B2', " U'")
                self.myperms2['CenterRVB-'] = (" U'", '2L2', ' U ', '2L2', '3B2', '2L2', " U'", '2L2', ' U ', '3B2')
                self.myperms2['CenterRVC-'] = ('2B2', '3L2', '2B2', '3L2', ' U ', '3B2', '2R2', '3B2', '2R2', " U'")
                self.myperms2['CenterRUA-'] = ("3L'", "2D'", '3B ', '2D ', "3B'", '3L ', '3B2', '2U2', '3B ', '2U2', '3B ')
                self.myperms2['CenterRUB-'] = ("3L'", "2U ", '3B ', "2U'", "3B'", '3L ', '3B2', '2D2', '3B ', '2D2', '3B ')
                self.myperms2['CenterRUC-'] = (" U ","3L'", "2D'", '3B ', '2D ', "3B'", '3L ', '3B2', '2U2', '3B ', '2U2', '3B '," U'")
                self.myperms2['CenterRUD-'] = (" U ","3L'", "2U ", '3B ', "2U'", "3B'", '3L ', '3B2', '2D2', '3B ', '2D2', '3B '," U'")
                self.myperms2['CenterRUE-'] = (" U2","3L'", "2D'", '3B ', '2D ', "3B'", '3L ', '3B2', '2U2', '3B ', '2U2', '3B '," U2")
                self.myperms2['CenterRUF-'] = (" U2","3L'", "2U ", '3B ', "2U'", "3B'", '3L ', '3B2', '2D2', '3B ', '2D2', '3B '," U2")
                self.myperms2['CenterRZA-'] = ('3L2', '2B2', '3L2', '2B2', ' U2', '3R2', '2B2', '3R2', '2B2', ' U2')
                self.myperms2['CenterRZB-'] = (" U ", '3L2', '2B2', '3L2', '2B2', ' U2', '3R2', '2B2', '3R2', '2B2', ' U ')

                self.myperms2['CenterR8-'] = ("3U2","2R2","3U'","2R2","3U'","2R2","3U'","2R2","3U ")      
                
                self.myperms2['CenterR6A-'] = ("2R ","3U ","2R'","3U'")
                self.myperms2['CenterR6B-'] = ("2R ","3U'","2R'","3U ")
                self.myperms2['CenterR6C-'] = ("2R ","3U2","2R'","3U2")
                self.myperms2['CenterR6D-'] = ("2R2","3U ","2R2","3U'")
                self.myperms2['CenterR6E-'] = ("2R'", "3F'", "2U'", '3F ', '2U ', '2R ', '3L ', '2F2', '3L ', '2F2', '3L2')
                self.myperms2['CenterR6F-'] = ('3L ', "2F'", '3D ', '2F ', "3D'", '2L ', "3L'", '3B2', '2L ', '3B2', '2L2')
                self.myperms2['CenterR6G-'] = ("2R ","3U ","2R ","3U'","2R2")
                self.myperms2['CenterR6H-'] = ("2R ","3U'","2R ","3U ","2R2")
                self.myperms2['CenterR6I-'] = ("2R2","3U ","2R'","3U'","2R'")
                self.myperms2['CenterR6J-'] = ("2R2","3U'","2R'","3U ","2R'")
                self.myperms2['CenterR6K-'] = ("2R2","3U ","2R2","3U ","2R2","3U2","2R2")
                self.myperms2['CenterR6L-'] = ("2R2","3U2","2R2","3U ","2R2","3U ","2R2")
                self.myperms2['CenterR6M-'] = ("2U ","3R2","2U2","3R2","2U ")
                self.myperms2['CenterR6N-'] = ("2F ","3R ","2F2","3R'","2F ")
                self.myperms2['CenterR6O-'] = ("2F'","3R ","2F2","3R'","2F'")                

                self.myperms2['CenterR4A-'] = ("2R2","3U2","2R ","3U2","2R ")
                self.myperms2['CenterR4B-'] = ("2R ","3U2","2R ","3U2","2R2")
                self.myperms2['CenterR4C-'] = ("2U ","3F ","2R ","3F'","2R'","2U'")
                self.myperms2['CenterR4D-'] = ("2F'", '3D ', "2R'", "3D'", '2R ', '2F ')
                self.myperms2['CenterR4XA-'] = ("2L'"," U ","2R'","3D2","2R "," U'","3D2","2L ")
                self.myperms2['CenterR4XB-'] = ("2L'"," D'","2R'","3D2","2R "," D ","3D2","2L ")
                self.myperms2['CenterR4YA-'] = ("2B "," U'","2R ","3U ","2R'"," U ","3U'","2B'")
                self.myperms2['CenterR4YB-'] = ("2B "," D ","2R ","3U ","2R'"," D'","3U'","2B'")
                self.myperms2['CenterR4YC-'] = ('2L ', " U'", '2R ', '3U2', "2R'", " U ", '3U2', "2L'")
                self.myperms2['CenterR4YD-'] = ('2L ', ' D ', '2R ', '3U2', "2R'", " D'", '3U2', "2L'")
                self.myperms2['CenterR4ZA-'] = (' U2', '2R ', '3U2', '2R ', '3U2', '2R2', ' U2')
                self.myperms2['CenterR4ZB-'] = (' D2', '2R ', '3U2', '2R ', '3U2', '2R2', ' D2')
                self.myperms2['CenterR4ZC-'] = (' U2', '2R ', '3U2', "2R'", ' U2', '2L2', '3U2', '2L2')
                self.myperms2['CenterR4ZD-'] = (' D2', '2R ', '3U2', "2R'", ' D2', '2L2', '3U2', '2L2')
                self.myperms2['CenterR4WA-'] = ('2L ', '3U2', ' D ', '2R ', '3U2', "2R'", " D'", "2L'")
                self.myperms2['CenterR4WB-'] = ('2L ', '3U2', " U'", '2R ', '3U2', "2R'", " U ", "2L'")
                

                self.myperms2['BigCenter-COpp-'] = ("2R2"," U ","3R2"," U'","2R2"," U ","3R2"," U2","2R2"," U ","3R2"," U'","2R2"," U ","3R2",
                                                    "2L2"," D ","3L2"," D'","2L2"," D ","3L2"," D2","2L2"," D ","3L2"," D'","2L2"," D ","3L2")
                self.myperms2['BigCenter-CNbr-'] = ("2R "," U ","3R "," U'","2R'"," U ","3R'"," U2","2R "," U ","3R "," U'","2R'"," U ","3R'",
                                                    "2L "," F ","3L "," F'","2L'"," F ","3L'"," F2","2L "," F ","3L "," F'","2L'"," F ","3L'")
                                               

                self.myperms2['BigCenter-CCyc3-'] = self.myperms2['BigCenter-CNbr-'] + self.transform(self.myperms2['BigCenter-CNbr-'],1)
                self.myperms2['BigCenter-CCyc4-'] = self.myperms2['BigCenter-CNbr-'] + self.transform(self.myperms2['BigCenter-CNbr-'],3) + self.transform(self.myperms2['BigCenter-CNbr-'],14)
                self.myperms2['BigCenter-CSwap2-'] = self.myperms2['BigCenter-CNbr-'] + self.transform(self.myperms2['BigCenter-CNbr-'],29)




                self.myperms2['BigCenter-COppW-'] = ('2R2', '3F2', '3B2', '2R2', '3B2', '3F2', '2B2', '3L2', '2B2', '3R2', '3L2', '2F2', '3R2', '2F2')
                self.myperms2['BigCenter-CNbrW-'] = self.myperms2['BigCenter-CNbr-'] + self.transform(self.myperms2['BigCenter-CNbr-'],48)

                self.myperms2['BigCenter-CCyc3W-'] = self.myperms2['BigCenter-CNbrW-'] + self.transform(self.myperms2['BigCenter-CNbrW-'],1)
                self.myperms2['BigCenter-CCyc4W-'] = self.myperms2['BigCenter-CNbrW-'] + self.transform(self.myperms2['BigCenter-CNbrW-'],3) + self.transform(self.myperms2['BigCenter-CNbrW-'],14)
                self.myperms2['BigCenter-CSwap2W-'] = self.myperms2['BigCenter-CNbrW-'] + self.transform(self.myperms2['BigCenter-CNbrW-'],29)


                self.myperms2['CenterC-OppX'] = (" U ", '2R2', " U'", '3F2', ' U ', '2R2', " U'", '3F2')
                self.myperms2['CenterC-OppX(1)'] = ('3B2', ' U ', '3B2', '2R2', '3B2', '2R2', " U'", '3B2')
                self.myperms2['CenterC-OppX(2)'] = (" D'", '3L2', ' D ', '2R2', " D'", '3L2', ' D ', '2R2')
                self.myperms2['CenterC-OppY'] = ('2R2', " U'", '3F2', ' U ', '2R2', " U'", '3F2', ' U ')
                self.myperms2['CenterC-OppY(1)'] = ('2R2', ' U ', '3F2', " U'", '2R2', ' U ', '3F2', " U'")
                self.myperms2['CenterC-OppY(2)'] = ('3F2', ' D ', '2R2', '3F2', '2R2', '3F2', " D'", '3F2')
                self.myperms2['CenterC-OppY(3)'] = ('3B2', " U'", '2R2', '3B2', '2R2', '3B2', ' U ', '3B2')
                self.myperms2['CenterC-OppY(4)'] = ('2R2', " U'", '3L2', ' U ', '2R2', " U'", '3L2', ' U ')
                self.myperms2['CenterC-OppY(5)'] = ('2R2', ' U ', '3R2', " U'", '2R2', ' U ', '3R2', " U'")
                self.myperms2['CenterC-OppZ'] = (' U ', '3F2', " U'", '2R2', ' U ', '3F2', " U'", '2R2')
                self.myperms2['CenterC-OppZ(1)'] = ('3B2', " U'", '3B2', '2R2', '3B2', '2R2', ' U ', '3B2')
                self.myperms2['CenterC-OppZ(2)'] = (' U ', '3F2', " U'", '2F2', ' U ', '3F2', " U'", '2F2')


                self.myperms2['CenterC-IO_D(0)'] = ("3F'", '2U ', '3F ', " U2", "3F'", "2U'", '3F ', " U2")
                self.myperms2['CenterC-IO_D(1)'] = ("3F'", '2U ', '3F ', " D2", "3F'", "2U'", '3F ', " D2")
                self.myperms2['CenterC-IO_V(0)'] = ('2R ', '3U2', "2R'", " U2", '2R ', '3U2', "2R'", " U2")
                self.myperms2['CenterC-IO_V(1)'] = ('2R ', '3U2', "2R'", " D2", '2R ', '3U2', "2R'", " D2")
                self.myperms2['CenterC-IO_V(2)'] = ("2R "," U ","3L'"," U'","2R'"," U ","3L "," U'")
                self.myperms2['CenterC-IO_V(3)'] = ("2L'"," U ","3R "," U'","2L "," U ","3R'"," U'")
                self.myperms2['CenterC-IO_V(4)'] = ("2R "," U ","3R "," U'","2R'"," U ","3R'"," U'")
                self.myperms2['CenterC-IO_V(5)'] = ("2L'"," U ","3L'"," U'","2L "," U ","3L "," U'")                
                self.myperms2['CenterC-IO_D(2)'] = (' U ', "3L'", " U'", '2R ', ' U ', '3L ', " U'", "2R'")
                self.myperms2['CenterC-IO_D(3)'] = (' U ', "3R ", " U'", "2L'", ' U ', "3R'", " U'", "2L ")
                
                self.myperms2['CenterC-II_D(0)'] = (' U2', '2R ', '3U2', "2R'", " U2", '2R ', '3U2', "2R'")
                self.myperms2['CenterC-OO_D(0)'] = (" D2", '2R ', '3U2', "2R'", " D2", '2R ', '3U2', "2R'")
                self.myperms2['CenterC-II_V(0)'] = (" U2", "3F'", '2U ', '3F ', " U2", "3F'", "2U'", '3F ')
                self.myperms2['CenterC-OO_V(0)'] = (" D2", "3F'", '2U ', '3F ', " D2", "3F'", "2U'", '3F ')

                self.myperms2['CenterC-IO_D(4)'] = (' U2', "3B'", "2U'", '3B ', ' U2', "3B'", '2U ', '3B ')
                self.myperms2['CenterC-IO_D(5)'] = (' D2', "3B'", "2U'", '3B ', ' D2', "3B'", '2U ', '3B ')

                

                self.myperms2['CenterC-3AAA(0)'] = (" F ","2D "," R2","2D'","3R'","2D "," R2","2D'","3R "," F'")
                self.myperms2['CenterC-3CCC(0)'] = (" F ","2U'"," R2","2U ","3L ","2U'"," R2","2U ","3L'"," F'")
                self.myperms2['CenterC-3BBB(0)'] = (" F'","3D'","2L'"," U2","2L ","3D ","2L'"," U2","2L "," F ")
                self.myperms2['CenterC-3DDD(0)'] = (" F'","3U ","2R "," U2","2R'","3U'","2R "," U2","2R'"," F ")

                self.myperms2['CenterC-3AAC(0)'] = (" F'","2D "," R2","2D'","3R'","2D "," R2","2D'","3R "," F ")
                self.myperms2['CenterC-3CCA(0)'] = (" F'","2U'"," R2","2U ","3L ","2U'"," R2","2U ","3L'"," F ")
                self.myperms2['CenterC-3BBD(0)'] = (" F ","3D'","2L'"," U2","2L ","3D ","2L'"," U2","2L "," F'")
                self.myperms2['CenterC-3DDB(0)'] = (" F ","3U ","2R "," U2","2R'","3U'","2R "," U2","2R'"," F'")
                
                self.myperms2['CenterC-3AAD(0)'] = ("2D "," R2","2D'","3R'","2D "," R2","2D'","3R ")
                self.myperms2['CenterC-3CCB(0)'] = ("2U'"," R2","2U ","3L ","2U'"," R2","2U ","3L'")
                self.myperms2['CenterC-3BBC(0)'] = ("3D'","2L'"," U2","2L ","3D ","2L'"," U2","2L ")
                self.myperms2['CenterC-3DDA(0)'] = ("3U ","2R "," U2","2R'","3U'","2R "," U2","2R'")

                self.myperms2['CenterC-3AAB(0)'] = ('3U ', "2L'", ' U2', '2L ', "3U'", "2L'", ' U2', '2L ')
                self.myperms2['CenterC-3CCD(0)'] = ("3D'", '2R ', ' U2', "2R'", '3D ', '2R ', ' U2', "2R'")
                self.myperms2['CenterC-3DDC(0)'] = ('2D ', ' R2', "2D'", '3L ', '2D ', ' R2', "2D'", "3L'")
                self.myperms2['CenterC-3BBA(0)'] = ("2U'", ' R2', '2U ', "3R'", "2U'", ' R2', '2U ', '3R ')

                self.myperms2['CenterC-3ADC(0)'] = ("2L'"," D'","3F'",' D ','2L '," D'",'3F ',' D ')
                self.myperms2['CenterC-3CBA(0)'] = ("2R "," D'","3B ",' D ',"2R'"," D'","3B'",' D ')
                self.myperms2['CenterC-3BAD(0)'] = ("2R "," D ","3F'"," D'","2R'"," D ","3F "," D'")
                self.myperms2['CenterC-3DCB(0)'] = ("2L'"," D ","3B "," D'","2L "," D ","3B'"," D'")

                self.myperms2['CenterC-3ABC(0)'] = (" U2","2L'"," D'","3F'",' D ','2L '," D'",'3F ',' D '," U2")
                self.myperms2['CenterC-3CDA(0)'] = (" U2","2R "," D'","3B ",' D ',"2R'"," D'","3B'",' D '," U2")
                self.myperms2['CenterC-3BCD(0)'] = (" U2","2R "," D ","3F'"," D'","2R'"," D ","3F "," D'"," U2")
                self.myperms2['CenterC-3DAB(0)'] = (" U2","2L'"," D ","3B "," D'","2L "," D ","3B'"," D'"," U2")

                self.myperms2['CenterC-3V-AAD(0)'] = ("2R "," U ","3L "," U'","2R'"," U ","3L'"," U'")
                self.myperms2['CenterC-3V-CCB(0)'] = ("2L'"," U ","3R'"," U'","2L "," U ","3R "," U'")
                self.myperms2['CenterC-3V-ADA(0)'] = ("2R ", ' F ', '3U2', " F'", "2R'", ' F ', '3U2', " F'")
                self.myperms2['CenterC-3V-CBC(0)'] = ("2L'", ' F ', '3D2', " F'", '2L ', ' F ', '3D2', " F'")

                self.myperms2['CenterC-3V-ADD(0)'] = ("2L2"," F'","3R'"," F ","2L2"," F'","3R "," F ")
                self.myperms2['CenterC-3V-CBB(0)'] = ("2R2"," F'","3L "," F ","2R2"," F'","3L'"," F ")
                self.myperms2['CenterC-3V-AAA(0)'] = ('3U2', '2L ', '3F2', "2L'", ' F2', '2L ', '3F2', "2L'", ' F2', '3U2')
                self.myperms2['CenterC-3V-CCC(0)'] = ('3D2', "2R'", '3B2', '2R ', ' F2', "2R'", '3B2', '2R ', ' F2', '3D2')
                self.myperms2['CenterC-3V-CAA(0)'] = ('3D2', '2R ', '3B2', "2R'", ' B2', '2R ', '3B2', "2R'", ' B2', '3D2')
                self.myperms2['CenterC-3V-ACC(0)'] = ('3U2', "2L'", '3F2', '2L ', ' B2', "2L'", '3F2', '2L ', ' B2', '3U2')

                self.myperms2['CenterC-3V-ADB(0)'] = ('3D2', "2L'", ' U ', '2L ', '3D2', "2L'", " U'", '2L ')
                self.myperms2['CenterC-3V-CBD(0)'] = ('3U2', '2R ', ' U ', "2R'", '3U2', '2R ', " U'", "2R'")
                self.myperms2['CenterC-3V-ABD(0)'] = ('2L ', ' U ', "2L'", '3U2', '2L ', " U'", "2L'", '3U2')
                self.myperms2['CenterC-3V-CDB(0)'] = ("2R'", ' U ', '2R ', '3D2', "2R'", " U'", '2R ', '3D2')

                self.myperms2['CenterC-3V-AAC(0)'] = ('2L ', ' U2', "2L'", '3D2', '2L ', ' U2', "2L'", '3D2')
                self.myperms2['CenterC-3V-CCA(0)'] = ("2R'", ' U2', '2R ', '3U2', "2R'", ' U2', '2R ', '3U2')
                self.myperms2['CenterC-3V-ACA(0)'] = ('3U2', '2L ', ' U2', "2L'", '3U2', '2L ', ' U2', "2L'")
                self.myperms2['CenterC-3V-CAC(0)'] = ('3D2', "2R'", ' U2', '2R ', '3D2', "2R'", ' U2', '2R ')

                self.myperms2['CenterC-3V-ACB(0)'] = ('3F2', '2L ', ' D ', '3R ', " D'", "2L'", ' D ', "3R'", " D'", '3F2')
                self.myperms2['CenterC-3V-CAD(0)'] = ('3B2', "2R'", ' D ', "3L'", " D'", '2R ', ' D ', '3L ', " D'", '3B2')
                self.myperms2['CenterC-3V-ABC(0)'] = ('3F2', '2L ', ' F ', '3D2', " F'", "2L'", ' F ', '3D2', '3F2', " F'")
                self.myperms2['CenterC-3V-CDA(0)'] = ('3B2', "2R'", ' F ', '3U2', " F'", '2R ', ' F ', '3U2', '3B2', " F'")
                self.myperms2['CenterC-3V-ABB(0)'] = ('2F2', '2R2', " F'", "3L'", ' F ', '2R2', " F'", '3L ', '2F2', ' F ')
                self.myperms2['CenterC-3V-CDD(0)'] = ('2B2', '2L2', " F'", '3R ', ' F ', '2L2', " F'", "3R'", '2B2', ' F ')

                self.myperms2['CenterC-3V-AAB(0)'] = ('2F2', " F'", '2R2', " F'", "3L'", ' F ', '2R2', " F'", '3L ', '2F2', ' F2')
                self.myperms2['CenterC-3V-CCD(0)'] = ('2B2', " F'", '2L2', " F'", '3R ', ' F ', '2L2', " F'", "3R'", '2B2', ' F2')
                self.myperms2['CenterC-3V-ABA(0)'] = (' B2', '2F2', '3L ', ' B ', '2R2', " B'", "3L'", ' B ', '2R2', ' B ', '2F2')
                self.myperms2['CenterC-3V-CDC(0)'] = (' B2', '2B2', "3R'", ' B ', '2L2', " B'", '3R ', ' B ', '2L2', ' B ', '2B2')



            self.myperms2['Bar-A'] = (' F2', '2R ', ' F2', ' D2', ' B2', '2L ', ' B2', ' D2')
            self.myperms2['Bar-B'] = (' D2', ' B2', "2L'", ' B2', ' D2', ' F2', "2R'", ' F2')
            
            self.myperms2['Bar-C'] = (" F'", '2R ', ' F2', ' D2', ' B2', '2L ', ' B2', ' D2', " F'")
            self.myperms2['Bar-D'] = (' F ', '2R ', ' F2', ' D2', ' B2', '2L ', ' B2', ' D2', ' F ')

            self.myperms2['Bar-E'] = (' U ', " F'", '2R ', ' F2', ' D2', ' B2', '2L ', ' B2', ' D2', " F'", " U'")
            self.myperms2['Bar-F'] = (' U ', ' F ', '2R ', ' F2', ' D2', ' B2', '2L ', ' B2', ' D2', ' F ', " U'")
            self.myperms2['Bar-G'] = (" U'", " F'", '2R ', ' F2', ' D2', ' B2', '2L ', ' B2', ' D2', " F'", ' U ')
            self.myperms2['Bar-H'] = (" U'", ' F ', '2R ', ' F2', ' D2', ' B2', '2L ', ' B2', ' D2', ' F ', ' U ')


            
            self.myperms2['Bar-W'] = ('2R ', ' F2', ' D2', ' B2', '2L ', '2R ', ' B2', ' D2', ' F2', '2L ')
            self.myperms2['Bar-WW'] = (' F ', '2R ', ' F2', ' D2', ' B2', '2L ', '2R ', ' B2', ' D2', ' F2', '2L ', " F'")

            self.myperms2['Bar-KA'] = ("2L'", ' B2', ' D2', ' F2', '2R2', ' F2', ' D2', ' B2', "2L'")
            self.myperms2['Bar-KB'] = ("2L ", ' B2', ' D2', ' F2', '2R2', ' F2', ' D2', ' B2', "2L ")

            self.myperms2['Bar-JA'] = ("2R "," U2"," F2"," D2","2L'"," D2"," F2"," U2","2R2")
            self.myperms2['Bar-JB'] = ("2R2"," U2"," F2"," D2","2L "," D2"," F2"," U2","2R'")

            self.myperms2['Bar-IA'] = (" B2","2R "," U2"," F2"," D2","2L'"," D2"," F2"," U2","2R2"," B2")
            self.myperms2['Bar-IB'] = (" B2","2R2"," U2"," F2"," D2","2L "," D2"," F2"," U2","2R'"," B2")

            self.myperms2['SuperBar-3III-A'] = (" R'","2D "," F "," B'","2R "," U2"," F2"," D2","2L'"," D2"," F2"," U2","2R2"," B "," F'","2D'"," R ")
            self.myperms2['SuperBar-3OOO-A'] = (" R'","2U'"," F "," B'","2L'"," U2"," F2"," D2","2R "," D2"," F2"," U2","2L2"," B "," F'","2U "," R ")
            self.myperms2['SuperBar-3IIO-A'] = (" R ","2D "," F "," B'","2R "," U2"," F2"," D2","2L'"," D2"," F2"," U2","2R2"," B "," F'","2D'"," R'")
            self.myperms2['SuperBar-3OOI-A'] = (" R ","2U'"," F "," B'","2L'"," U2"," F2"," D2","2R "," D2"," F2"," U2","2L2"," B "," F'","2U "," R'")

            self.myperms2['SuperBar-3III-B'] = self.invert_moves(self.myperms2['SuperBar-3III-A'])
            self.myperms2['SuperBar-3OOO-B'] = self.invert_moves(self.myperms2['SuperBar-3OOO-A'])
            self.myperms2['SuperBar-3IIO-B'] = self.invert_moves(self.myperms2['SuperBar-3IIO-A'])
            self.myperms2['SuperBar-3OOI-B'] = self.invert_moves(self.myperms2['SuperBar-3OOI-A'])

            
            self.myperms2['Bar-X'] = ("2L2"," F2"," U2"," F2","2L2"," F2"," U2"," F2")
            self.myperms2['Bar-Y'] = (" F2"," U2"," F2","2L2"," F2"," U2"," F2","2L2")
            self.myperms2['Bar-Z'] = (" U ","2L2"," F2"," U2"," F2","2L2"," F2"," U2"," F2"," U'")
            self.myperms2['Bar-XX'] = ("2R2"," F2"," B2","2L2"," F2"," B2")
            self.myperms2['Bar-ZZ'] = (" U ","2R2"," F2"," B2","2L2"," F2"," B2"," U'")

            

        self.myperms2['E-Perm'] = (" R "," B'"," R'"," F "," R "," B "," R'"," F'"," R "," B "," R'"," F "," R "," B'"," R'"," F'")
        self.myperms2['X-Perm-A'] = (" U'", ' L2', ' F2', ' B2', ' R2', " D'", ' R2', ' B2', ' F2', ' L2')
        self.myperms2['X-Perm-B'] = (" L "," F2"," R2"," D2"," R "," D2"," R "," F2"," L2"," U2"," L "," U2")
        self.myperms2['X-Perm-C'] = (' R ', ' B ', " L'", " B'", " R'", ' B ', ' L ', ' B2', ' R ', ' B ', " L'", " B'", " R'", ' B ', ' L ')

        self.myperms2['X-Perm-D'] = (' R2', ' B2', " D'", ' B2', ' R2', ' L2', ' F2', " U'", ' F2', ' L2')
        self.myperms2['X-Perm-E'] = (" F'",) + (" R "," U "," R'"," U'") * 3 + (" F ",)
        self.myperms2['X-Perm-F'] = (' U ', " F'", " U'", " B'", ' U ', ' F ', " U'", ' B2', " U'", ' F ', ' U ', " B'", " U'", " F'", ' U ')

        self.myperms2['X-Perm-G'] = (' R2', ' D ', ' U ', ' R2', ' F2', ' L2', ' B2', ' D ', ' U ', ' B2', ' L2', ' F2')
        

        

        self.myperms2['CO-A'] = (" R'"," U2"," R'"," B "," D2"," B'"," R "," U2"," R'"," B "," D2"," B'"," R2")
        self.myperms2['CO-B'] = (" U2"," R'"," B "," D2"," B'"," R "," U2"," R'"," B "," D2"," B'"," R ")
        self.myperms2['CO-C'] = (" R "," U2"," R'"," B "," D2"," B'"," R "," U2"," R'"," B "," D2"," B'")
        self.myperms2['CO-D'] = (' B ', " L'", " B'", ' R ', ' B ', ' L ', " B'", ' U2', ' R ', ' D ', " R'", ' U2', ' R ', " D'", ' R2')
        self.myperms2['CO-E'] = (" R'", ' F ', ' R ', ' B ', " R'", " F'", ' R ', ' B2', " D'", ' B ', ' U2', " B'", ' D ', ' B ', ' U2')
        self.myperms2['CO-F'] = (' R2', ' B ', " L'", ' B2', ' U ', " F'", " U'", ' B ', ' U ', ' F ', " U'", ' R2', ' B ', ' L ', " B'")
        self.myperms2['CO-F(1)'] = self.invert_moves(self.myperms2['CO-F'])
        


        self.myperms2['CP-A00-'] = (" R "," B'"," R "," F2"," R'"," B "," R "," F2"," R2")
        self.myperms2['CP-A01-'] = (" R ",' U2', ' R ', ' D ', " R'", ' U2', ' R ', " D'", " R2")
        self.myperms2['CP-A02-'] = (' F ', ' R ', ' B ', " R'", " F'", ' R ', " B'", " R'")
        self.myperms2['CP-A03-'] = (" L'", ' B ', ' U2', " B'", ' L ', ' B ', " L'", ' U2', ' L ', " B'")
        self.myperms2['CP-A04-'] = (" B'", ' R2', " B'", ' L2', ' B ', ' R2', " B'", ' L2', ' B2')
        self.myperms2['CP-A05-'] = (' F2', " D'", ' F ', ' U2', " F'", ' D ', ' F ', ' U2', ' F ')
        self.myperms2['CP-A06-'] = (' F ', " U'", " B'", ' U ', " F'", " U'", ' B ', ' U ')
        self.myperms2['CP-A07-'] = (' R ', ' B ', " L'", " B'", " R'", ' B ', ' L ', " B'")
        self.myperms2['CP-A08-'] = (' L2', ' B2', " L'", ' F2', ' L ', ' B2', " L'", ' F2', " L'")

        self.myperms2['CP-A09-'] = (" L'", ' B ', ' L ', " F'", " L'", " B'", ' L ', ' F ')
        self.myperms2['CP-A10-'] = (' U ', ' L ', " U'", " R'", ' U ', " L'", " U'", ' R ')
        self.myperms2['CP-A11-'] = (" F'", " L'", ' F ', " R'", " F'", ' L ', ' F ', ' R ')

        self.myperms2['CP-B00-'] = (" B'"," R "," F2"," R'"," B "," R "," F2"," R'")
        self.myperms2['CP-B01-'] = (' U2', ' R ', ' D ', " R'", ' U2', ' R ', " D'", " R'")
        self.myperms2['CP-B02-'] = (" R'", ' F ', ' R ', ' B ', " R'", " F'", ' R ', " B'")
        self.myperms2['CP-B03-'] = (' U ', ' R2', " U'", ' B2', ' U ', ' B2', ' U ', ' R2', " U'", ' B2', " U'", ' B2')
        self.myperms2['CP-B04-'] = (" D'", ' R2', " D'", ' L ', ' D ', ' R2', " D'", " L'", ' D2')

        self.myperms2['CP-B05-'] = self.invert_moves(self.myperms2['CP-B00-'])
        self.myperms2['CP-B06-'] = self.invert_moves(self.myperms2['CP-B01-'])
        self.myperms2['CP-B07-'] = self.invert_moves(self.myperms2['CP-B02-'])
        self.myperms2['CP-B08-'] = self.invert_moves(self.myperms2['CP-B03-'])
        self.myperms2['CP-B09-'] = self.invert_moves(self.myperms2['CP-B04-'])

        self.myperms2['CP-B10-'] = (" F'", ' D2', ' F ', ' U2', " F'", ' D2', ' F ', ' U2')
        self.myperms2['CP-B11-'] = (" B'", " D'", ' F2', ' D ', ' B ', " D'", ' F2', ' D ')
        self.myperms2['CP-B12-'] = self.invert_moves(self.myperms2['CP-B10-'])
        self.myperms2['CP-B13-'] = self.invert_moves(self.myperms2['CP-B11-'])

        

        self.myperms2['CP-C00-'] = (" R "," U2"," R'"," U2"," R'"," F2"," R "," U2"," R "," U2"," R'"," F2")
        self.myperms2['CP-C01-'] = (" D'", ' F2', ' D ', " B'", " D'", ' F ', ' D ', ' B ', " D'", ' F ', ' D ')
        self.myperms2['CP-C02-'] = (" U'", " F'", ' U ', ' B ', " U'", " F'", ' U ', " B'", " U'", ' F2', ' U ')
        self.myperms2['CP-C03-'] = (" B'", ' D ', ' B ', ' U2', " B'", " D'", ' B ', ' U2')
        self.myperms2['CP-C04-'] = (' U2', " B'", ' D ', ' B ', ' U2', " B'", " D'", ' B ')
        self.myperms2['CP-C05-'] = self.invert_moves(self.myperms2['CP-C00-'])
        self.myperms2['CP-C06-'] = self.invert_moves(self.myperms2['CP-C01-'])
        self.myperms2['CP-C07-'] = self.invert_moves(self.myperms2['CP-C02-'])
        self.myperms2['CP-C08-'] = (' U ', ' F2', ' U ', ' B ', " U'", ' F ', ' U ', " B'", " U'", ' F ', " U'")
        self.myperms2['CP-C09-'] = self.invert_moves(self.myperms2['CP-C08-'])
        self.myperms2['CP-C10-'] = (' F2', " U'", ' R2', ' U ', ' R2', ' D ', ' R2', " D'", ' R2', " D'", ' F2', ' D ')
        self.myperms2['CP-C11-'] = self.invert_moves(self.myperms2['CP-C10-'])

        self.myperms2['EF-A'] = (" R'", " U'", " F'", ' U ', ' F2', ' U2', " F'", " B'", " R'", ' F ', ' R ', ' B ', ' U2', " F'", ' R ') 
        self.myperms2['EF-B'] = (" L "," F "," R'"," F'"," L'"," U2"," R "," U "," R "," U'"," R2"," U2"," R ")
        self.myperms2['EF-C'] = (" R'", " F'", ' R ', ' F2', ' R2', " F'", " B'", " D'", ' F ', ' D ', ' B ', ' R2', " F'")
        self.myperms2['EF-D'] = (' D ', " R'", " F'", ' R ', ' F2', ' R2', " F'", " B'", " D'", ' F ', ' D ', ' B ', ' R2', " F'", " D'")
        self.myperms2['EF-E'] = (" F'"," U2"," F "," U'"," R "," U "," B "," L "," U2"," L'"," U "," B'"," U'"," R'")
        self.myperms2['EF-F'] = (" U "," B2"," F "," U2"," F "," U'"," R "," U "," B "," L "," U2"," L'"," U "," B'"," U'"," R'"," B2"," F2"," U'")
        self.myperms2['EF-G'] = (" B2"," F "," U2"," F "," U'"," R "," U "," B "," L "," U2"," L'"," U "," B'"," U'"," R'"," B2"," F2")
        
        #(" F'", ' U2', " F'", ' R ', ' D2', " R'", ' F ', ' U2', " F'", ' R ', ' D2', " R'", ' F2')
        #(' F2', ' R ', ' D2', " R'", ' F ', ' U2', " F'", ' R ', ' D2', " R'", ' F ', ' U2', ' F ')

        self.myperms2['EP-PA'] = (' D2', ' B2', ' R ', ' B2', ' D2', ' F2', ' L ', ' F2')
        self.myperms2['EP-PB'] = (' F ', " U'", " R'", ' L ', ' F2', " L'", ' R ', " U'", " F'")
        self.myperms2['EP-PC'] = (" U "," F'"," U'"," B "," F'"," L "," F "," L'"," B'"," F ")
        self.myperms2['EP-PD'] = (" F "," B'"," R'"," F'"," R "," F'"," B "," U'"," F "," U ")
        self.myperms2['EP-PE'] = self.invert_moves(self.myperms2['EP-PA'])
        self.myperms2['EP-PF'] = self.invert_moves(self.myperms2['EP-PB'])
        self.myperms2['EP-PG'] = self.invert_moves(self.myperms2['EP-PC'])
        self.myperms2['EP-PH'] = self.invert_moves(self.myperms2['EP-PD'])

        self.myperms2['EP-UA'] = self.conjugate((" F ",),self.myperms2['EP-PA'])
        self.myperms2['EP-UB'] = (' F2', " U'", ' L ', " R'", ' F2', " L'", ' R ', " U'", ' F2')
        self.myperms2['EP-UC'] = self.conjugate((" F ",),self.myperms2['EP-PC'])
        self.myperms2['EP-UD'] = (" B'", " R'", ' F ', ' R ', ' B ', " F'", " U'", " F'", ' U ', ' F ')
        self.myperms2['EP-UE'] = self.invert_moves(self.myperms2['EP-UA'])
        self.myperms2['EP-UF'] = self.invert_moves(self.myperms2['EP-UB'])
        self.myperms2['EP-UG'] = self.invert_moves(self.myperms2['EP-UC'])
        self.myperms2['EP-UH'] = self.invert_moves(self.myperms2['EP-UD'])

        
        self.myperms2['EP-VA'] = self.conjugate((" F'",),self.myperms2['EP-PA'])
        self.myperms2['EP-VB'] = (" U'", " R'", ' L ', ' F2', " L'", ' R ', " U'")
        self.myperms2['EP-VC'] = (' F ', ' U ', ' F ', " U'", " F'", ' B ', ' L ', " F'", " L'", " B'")
        self.myperms2['EP-VD'] = self.conjugate((" F'",),self.myperms2['EP-PD'])
        self.myperms2['EP-VE'] = self.invert_moves(self.myperms2['EP-VA'])
        self.myperms2['EP-VF'] = self.invert_moves(self.myperms2['EP-VB'])
        self.myperms2['EP-VG'] = self.invert_moves(self.myperms2['EP-VC'])
        self.myperms2['EP-VH'] = self.invert_moves(self.myperms2['EP-VD'])
        
        self.myperms2['EP-RA'] = (" L'", ' D2', ' B2', ' U2', ' R ', ' B2', ' D2', ' F2', ' L2')
        self.myperms2['EP-RB'] = self.conjugate((" L2",),self.myperms2['EP-PB'])
        self.myperms2['EP-RC'] = self.conjugate((" L2",),self.myperms2['EP-PC'])
        self.myperms2['EP-RD'] = (' D2', " F'", ' B ', " R'", ' F ', ' R ', " B'", ' F ', " D'", " F'", " D'")
        self.myperms2['EP-RE'] = self.invert_moves(self.myperms2['EP-RA'])
        self.myperms2['EP-RF'] = self.invert_moves(self.myperms2['EP-RB'])
        self.myperms2['EP-RG'] = self.invert_moves(self.myperms2['EP-RC'])
        self.myperms2['EP-RH'] = self.invert_moves(self.myperms2['EP-RD'])

        self.myperms2['EP-NA'] = (' D ', ' L2', ' R2', " U'", " R'", ' U ', ' L2', ' R2', " D'", ' R ')
        self.myperms2['EP-NB'] = self.conjugate((" U "," R ",),self.myperms2['EP-PB'])
        self.myperms2['EP-NC'] = (" F'", ' U ', ' B2', ' F2', " D'", ' F ', ' D ', ' B2', ' F2', " U'")
        self.myperms2['EP-ND'] = (" F'", " R'", " F'", " R'", " F'", ' R ', ' F ', ' R ', ' F ', ' R ')

        self.myperms2['EP-NE'] = self.invert_moves(self.myperms2['EP-NA'])
        self.myperms2['EP-NF'] = self.invert_moves(self.myperms2['EP-NB'])
        self.myperms2['EP-NG'] = self.invert_moves(self.myperms2['EP-NC'])
        self.myperms2['EP-NH'] = self.invert_moves(self.myperms2['EP-ND'])

        self.myperms2['EP-QA'] = (' R ', " U'", " R'", " U'", " R'", " U'", ' R ', ' U ', ' R ', ' U ')
        self.myperms2['EP-QB'] = self.conjugate((" U'"," R ",),self.myperms2['EP-PB'])
        self.myperms2['EP-QC'] = (' D ', ' B ', " D'", ' U ', ' R2', " U'", ' D ', ' B ', " D'")
        self.myperms2['EP-QD'] = (' B ', ' R ', ' B ', ' R ', " B'", " R'", " B'", " R'", " B'", ' R ')
        self.myperms2['EP-QE'] = self.invert_moves(self.myperms2['EP-QA'])
        self.myperms2['EP-QF'] = self.invert_moves(self.myperms2['EP-QB'])
        self.myperms2['EP-QG'] = self.invert_moves(self.myperms2['EP-QC'])
        self.myperms2['EP-QH'] = self.invert_moves(self.myperms2['EP-QD'])

        self.myperms2['EP-YA'] = (" U'", " R'", " U'", " R'", " U'", " R'", ' U ', ' R ', ' U ', ' R ', ' U2')
        self.myperms2['EP-YB'] = self.conjugate((" R'"," U "," R ",),self.myperms2['EP-PC'])
        self.myperms2['EP-YC'] = self.invert_moves(self.myperms2['EP-YA'])
        self.myperms2['EP-YD'] = self.invert_moves(self.myperms2['EP-YB'])

        self.myperms2['EP-OA'] = (" L'", ' B ', " L'", ' R ', ' D2', ' L ', " R'", ' B ', ' L ')
        self.myperms2['EP-OB'] = self.conjugate((" R'"," F'",),self.myperms2['EP-PC'])
        self.myperms2['EP-OC'] = self.invert_moves(self.myperms2['EP-OA'])
        self.myperms2['EP-OD'] = self.invert_moves(self.myperms2['EP-OB'])

        self.myperms2['EP-IA'] = (' L ', " B'", ' F ', " U'", ' R2', ' U ', " F'", ' B ', " L'", ' U2')
        self.myperms2['EP-IB'] = (' U2', ' F ', " B'", ' R2', ' B ', " F'")
        self.myperms2['EP-IC'] = (' R2', " D'", ' B ', " F'", ' R ', ' U2', " R'", ' F ', " B'", ' D ')
        self.myperms2['EP-ID'] = (" D'"," B'"," R'"," F'"," R "," F'"," B "," U'"," F "," U "," F "," D ")
        self.myperms2['EP-IE'] = self.invert_moves(self.myperms2['EP-IA'])
        self.myperms2['EP-IF'] = self.invert_moves(self.myperms2['EP-IB'])
        self.myperms2['EP-IG'] = self.invert_moves(self.myperms2['EP-IC'])
        self.myperms2['EP-IH'] = self.invert_moves(self.myperms2['EP-ID'])

        self.myperms2['EX-A'] = (' F ', " R'", ' F ', ' D2', " B'", ' L ', ' B ', ' D2', ' F2', ' R ')
        self.myperms2['EX-B'] = (" U'", " F'", ' U ', ' F ', ' R ', " U'", " R'", " F'", ' L ', " F'", " L'", " F2")
        self.myperms2['EX-C'] = self.conjugate((" F2"," R "),self.myperms2['EX-A'])
        self.myperms2['EX-D'] = self.conjugate((" F "," R "),self.myperms2['EX-A'])
        self.myperms2['EX-E'] = self.conjugate((" R ",),self.myperms2['EX-A'])
        self.myperms2['EX-F'] = self.conjugate((" F'"," R "),self.myperms2['EX-A'])
        self.myperms2['EX-G'] = self.conjugate((" R2",),self.myperms2['EX-A'])
        self.myperms2['EX-H'] = (' F2', " U'", " F'", ' U ', ' F ', ' R ', " U'", " R'", " F'", ' L ', " F'", " L'")

        
        self.myperms2['EY-A'] = (" R "," U "," R'"," U'"," R'"," F "," R2"," U'"," R'"," U'"," R "," U "," R'"," F'")
        self.myperms2['EY-B'] = self.conjugate((" U "," F'"," R "),self.myperms2['EY-A'])
        self.myperms2['EY-C'] = self.conjugate((" F2"," R "),self.myperms2['EY-A'])
        self.myperms2['EY-D'] = self.conjugate((" F "," R "),self.myperms2['EY-A'])
        self.myperms2['EY-E'] = self.conjugate((" R ",),self.myperms2['EY-A'])
        self.myperms2['EY-F'] = self.conjugate((" F'"," R "),self.myperms2['EY-A'])
        self.myperms2['EY-G'] = self.conjugate((" R2",),self.myperms2['EY-A'])
        self.myperms2['EY-H'] = self.conjugate((" R'"," U'"," F "," U "),self.myperms2['EY-A'])

        self.myperms2['EZ-A'] = (' D2', " R'", ' B ', ' R ', ' D2', ' U2', " B'", ' U2', ' B ', ' U2', ' L2', ' F ', ' L ', " F'", ' L ')
        self.myperms2['EZ-B'] = self.conjugate((" F'"," U "," L'"),self.myperms2['EZ-A'])
        self.myperms2['EZ-C'] = self.conjugate((" U2"," L "),self.myperms2['EZ-A'])
        self.myperms2['EZ-D'] = self.conjugate((" U "," L "),self.myperms2['EZ-A'])
        self.myperms2['EZ-E'] = self.conjugate((" L ",),self.myperms2['EZ-A'])
        self.myperms2['EZ-F'] = self.conjugate((" U'"," L "),self.myperms2['EZ-A'])
        self.myperms2['EZ-G'] = self.conjugate((" L2",),self.myperms2['EZ-A'])
        self.myperms2['EZ-H'] = self.conjugate((" F "," U "," L'"),self.myperms2['EZ-A'])   
        

        


        self.myperms2['K00-'] = (' D2', ' L ', ' B ', " L'", ' D2', ' R ', " F'", ' R ', ' F ', ' R2', ' F2', ' D2', ' F ', ' U2', " F'", ' D2', ' F ', ' U2', ' F ')
        self.myperms2['K01-'] = (' R2', " D'", ' R ', ' U2', " R'", ' D ', ' R ', ' U2', ' R ', " U'", " L'", ' U ', ' R2', " U'", ' L ', ' U ', ' R2', ' U ', ' R ', " U'", ' R ', ' U ', ' R ', " U'", ' R2')
        self.myperms2['K02-'] = (" B'", ' R2', " B'", ' D2', ' L2', ' F2', ' L2', ' D2', ' B ', ' R2', ' D2', " L'", " F'", ' L ', ' D2', " R'", ' B ', ' R ')
        self.myperms2['K03-'] = (' B2', ' D ', " B'", ' U2', ' B ', " D'", " B'", ' U2', ' L ', " B'", " U'", ' L ', ' F ', ' U ', ' L2', " U'", ' L ', ' F ', ' L ', " F'", ' L2', ' U ')
        self.myperms2['K04-'] = (' U2', ' F ', ' L2', " B'", ' U2', ' B ', ' U2', ' F2', ' L2', " F'", ' L2', ' F ', ' L2', ' U2', ' F2', ' U2', ' B ', ' L2', ' U2', ' R2', ' F ', ' D2', ' R2')
        self.myperms2['K05-'] = (' D ', ' R ', " D'", ' U ', ' F2', " U'", ' D ', " R'", ' D2', ' B2', ' D2', " B'", ' D2', ' B ', ' D2', " B'", ' D2', ' R2', " B'", ' R2', " B'", ' D2', ' B2', " D'")
        self.myperms2['K06-'] = (' U2', " B'", ' L2', ' F ', ' U2', " F'", ' U2', ' B2', ' L2', ' B ', ' L2', " B'", ' L2', ' U2', ' B2', ' D2', " B'", ' D2', ' R2', ' U2', " F'", ' U2', ' R2')
        self.myperms2['K07-'] = (' D ', " R'", ' D ', " U'", ' B2', " D'", ' U ', ' R ', ' D2', ' B2', ' D2', " B'", ' D2', ' B ', ' D2', " B'", ' D2', ' R2', " B'", ' R2', " B'", ' D2', ' B2', " D'")
        self.myperms2['K08-'] = (' F2', ' D2', ' B ', ' U2', " B'", ' F ', ' R2', ' L2', ' F ', ' L2', ' D2', ' F ', ' D2', " F'", ' D2', ' F ', ' D2', ' F2', ' D2', ' L2')
        self.myperms2['K09-'] = self.conjugate((" L "," R'"),self.myperms2['EZ-H'])


        
        self.myperms2['J00-'] = (' L2', ' U2', ' F ', ' U ', " F'", ' U ', ' L2', " D'", ' B ', ' D ')
        self.myperms2['J01-'] = (' D2', " R'", " U'", ' R ', ' D2', " R'", ' U ', ' F2', " L'", " U'", ' L ', ' F2', " R'", ' D ', " R'", " D'", " R'")
        self.myperms2['J02-'] = (' U ', " B'", ' U ', ' R2', " D'", ' F ', ' D ', ' R2', ' F ', ' U2', ' B ', ' U2', " F'", ' U2')
        self.myperms2['J03-'] = (' U2', ' L ', ' D ', " L'", ' U2', ' L ', " D'", ' L2', ' F2', ' R ', ' U ', " R'", ' F2', ' L ', " D'", ' L ', ' D ', " L'")
        self.myperms2['J04-'] = (' L2', ' U2', " F'", ' L2', ' D2', ' R2', ' B2', ' D2', ' L2', " U'", " F'", ' U ', ' L2', " D'", ' B ', ' D ')
        self.myperms2['J05-'] = (' R2', " D'", " F'", ' D ', ' F ', ' D ', " R'", ' D2', ' F ', ' D ', ' F ', " D'", " F'", ' D ', ' B2', ' L2', ' U ', ' L2', ' B2', ' R2', ' D ', ' R ')
        self.myperms2['J06-'] = (" D'", " B'", ' D ', ' L2', " U'", ' F ', ' U ', ' L2', ' D2', ' B ', ' D2', ' U2', ' L2', ' D2', ' F ', ' R2', ' D2', ' L2', ' B ')
        self.myperms2['J07-'] = (" L'", ' U2', ' L2', ' R2', " D'", ' L2', ' D ', ' L2', ' R2', " U'", ' L2', " U'", ' L ', ' R ', " D'", ' F ', ' D ', " F'", " D'", " F'", ' D2', ' R ', " D'", " F'", " D'", ' F ', ' D ', ' R2')
        self.myperms2['J08-'] = self.conjugate((" F "," B "),self.myperms2['EZ-G'])
        self.myperms2['J09-'] = self.conjugate((" L "," R "),self.myperms2['EZ-H'])        
        self.myperms2['J10-'] = self.conjugate((" F2",),self.myperms2['EZ-G'])
        self.myperms2['J11-'] = self.conjugate((" L2",),self.myperms2['EZ-H'])

        self.myperms2['JX'] = (' B2', " L'", ' B2', ' D2', " F'", " R'", ' F ', ' D2', " B'", ' L ', ' B ')
        self.myperms2['JY'] = (' F2', " R'", ' F ', ' D2', " B'", ' L ', ' B ', ' D2', ' F ', " L'", ' F ', ' R ', " F'", ' L ')
        self.myperms2['JZ'] = (' B2', ' U2', ' B2', ' U2', ' B2', " R'", ' U ', ' F2', " D'", ' L ', ' D ', ' F2', ' U ', " L'", ' U ', ' R ', " U'", ' L ')        
        

        self.myperms2['Super00-'] = (" U'", " F'", ' U ', ' B ', " U'", ' F ', ' U ', " B'", ' L ', ' D ', " L'", ' U ', ' L ', " D'", ' L2', ' U ', ' L ', " U'", ' F ', ' R ', ' U ', " R'", " F'", " L'", " U'", ' L ')
        self.myperms2['B00-'] = (" L2"," F2"," U2"," L'"," U2"," L2"," F2"," L'"," U2"," L2"," U2"," F2"," L'"," F2")
        self.myperms2['F00-'] = (' L ', " F'", ' D2', ' B ', " R'", " B'", ' D2', ' F2', " L'", " F'")
        self.myperms2['B01-'] = (' R2', ' B2', ' L2', ' D2', ' F2', ' L2', ' B2', ' R2', ' F2', ' U ', ' F2', ' U2', ' R2', ' U ', ' F2', ' U2', ' F2', ' R2', ' U ', ' R2')
        self.myperms2['F01-'] = (" F "," R2"," F "," R "," U "," R'"," U'"," R'"," F "," R2"," U'"," R'"," U'"," R "," U "," R'"," F2"," R2"," F'")
        
        self.myperms2['Super05-'] = (' D2', ' B2', ' D2', ' F2', ' U2', ' F2', ' B2', " R'", ' B2', ' D2', ' R2', ' D2', " R'", ' B2', ' R2', ' D2', ' R ', ' D2', ' B2', ' R2')
        self.myperms2['Super06-'] = (' D2', ' F2', ' B2', ' U2', ' F2', " R'", ' B ', ' U2', " F'", ' L ', ' F ', ' U2', ' B2', ' R ', " B'")
        
        

    def _register_myperms2_f2l_oll(self):
        """F2L/OLLやCenters条件に応じた手順群を登録する。"""
        if self.F2L or self.OLL:
            self.myperms2 = {}
            self.myperms2['Q1-'] = (" S "," E "," S'"," E'")
            self.myperms2['Q2-'] = (" S "," E2"," S'"," E2")
            self.myperms2['Q3-'] = (' S ', " U'", ' B ', " F'", ' L ', ' F ', " B'", ' U ', " F "," B'", ' R2', " F'"," B ")

            self.myperms2['CornerSwap00-'] = (" L'", ' D ', " R'", " D'", ' L ', ' D ', ' R ', " D'", " L'", " D'", ' L ', ' U2', " L'", ' D ', ' L ')
            self.myperms2['CornerSwap01-'] = (" L'", ' D2', " L'", ' U2', ' L ', ' D2', " L'", ' U2', ' L2', ' F ', " D'", " F'", ' U ', ' F ', ' D ', " F'")
            self.myperms2['CornerSwap02-'] = (' L ', " B'", " L'", " F'", ' L ', ' B ', " L'", ' F ', ' B2', ' L ', ' F ', " L'", ' B2', ' L ', " F'", " L'")
            self.myperms2['CornerSwap03-'] = (" B'", ' D ', ' B ', ' U2', " B'", " D'", ' B ')
            self.myperms2['CornerSwap04-'] = (' F2', " U'", ' F2', " U'", ' F2', ' U2', ' F2')
            self.myperms2['CornerSwap05-'] = (" U ",' F2', " U'", ' F2', " U'", ' F2', ' U2', ' F2')
            self.myperms2['CornerSwap06-'] = (" U2",' F2', " U'", ' F2', " U'", ' F2', ' U2', ' F2')
            self.myperms2['CornerSwap07-'] = (" U'",' F2', " U'", ' F2', " U'", ' F2', ' U2', ' F2')
            self.myperms2['CornerSwap08-'] = (" F'", ' D ', ' F ', ' U ', " F'", " D'", ' F ')
            self.myperms2['CornerSwap09-'] = (" U "," F'", ' D ', ' F ', ' U ', " F'", " D'", ' F ')
            self.myperms2['CornerSwap10-'] = (" F'", ' D ', ' F ', " U'", " F'", " D'", ' F ')
            self.myperms2['CornerSwap11-'] = (' B ', ' D ', " B'", ' U ', ' B ', " D'", " B'")
            self.myperms2['CornerSwap12-'] = (' F2', " L'", ' F2', ' U2', ' D2', ' B2', " R'", ' B2', ' D2')


            
            self.myperms2['F2L-A0'] = (" R "," U2"," R'"," U "," R "," U2"," R'"," U "," F'"," U'"," F ")
            self.myperms2['F2L-A1'] = (" U "," R "," U'"," R'"," F "," R'"," F'"," R ")
            self.myperms2['F2L-B1'] = (" R "," U'"," R'"," U "," F'"," U "," F ")
            self.myperms2['F2L-B2'] = (" U "," R "," U'"," R'") * 3
            self.myperms2['F2L-C'] = (" R "," U'"," R'"," U "," R "," U2"," R'"," U "," R "," U'"," R'")
            self.myperms2['F2L-D'] = (" R "," U'"," R'"," U'"," R "," U'"," R'"," U "," F'"," U'"," F ")
            self.myperms2['F2L-E'] = (" R "," U'"," R'"," U "," R "," U'"," R'")
            self.myperms2['F2L-F'] = (" R "," U "," R'"," U'"," R "," U "," R'")
            self.myperms2['F2L-G'] = (" U'"," R "," U'"," R'"," U2"," R "," U'"," R'")
            self.myperms2['F2L-H'] = (" U "," F'"," U'"," F "," U'"," R "," U "," R'")
            self.myperms2['F2L-I'] = (" R "," U'"," R'")
            self.myperms2['F2L-J'] = (" U'"," R "," U2"," R'"," U "," F'"," U'"," F ")
            self.myperms2['F2L-K'] = (" R "," U'"," R'"," U2"," F'"," U'"," F ")
            self.myperms2['F2L-L'] = (" U'"," R "," U'"," R'"," U "," R "," U "," R'")
            self.myperms2['F2L-M'] = (" U "," F "," R'"," F'"," R "," U "," R "," U "," R'")
            self.myperms2['F2L-N'] = (" R "," U2"," R'"," U'"," R "," U "," R'")

            self.myperms2['F2L-Q'] = (" R "," U "," R'"," U2"," R "," U'"," R'")
            self.myperms2['F2L-R'] = (" R "," U "," R'"," U "," R "," U "," R'")
            self.myperms2['F2L-S'] = (" R "," U2"," R'"," U2"," R "," U'"," R'")  
            self.myperms2['F2L-T'] = (" R "," U "," R'")
            self.myperms2['F2L-U'] = (" R "," U2"," R'"," U "," R "," U'"," R'")
            self.myperms2['F2L-V'] = (" R "," U "," R'"," U "," R "," U'"," R'")

            self.myperms2['OLL-Sune'] = (" R "," U2"," R'"," U'"," R "," U'"," R'")
            self.myperms2['OLL-8'] = (" B'"," R'"," F'"," R "," B "," R'"," F "," R ")
            self.myperms2['OLL-A1'] = (" R'"," F'"," R "," B'"," R'"," F "," R "," B ")
            self.myperms2['OLL-A2'] = (" R2"," D'"," R "," U2"," R'"," D "," R "," U2"," R ")
            self.myperms2['OLL-CrossH'] = (" F ",) + (" R "," U "," R'"," U'") * 3 + (" F'",)
            self.myperms2['OLL-CrossPi'] = (" R "," U2"," R2"," U'"," R2"," U'"," R2"," U2"," R ")

            self.myperms2['OLL-DotH'] = (" R "," U2"," R2"," F "," R "," F'"," U2"," R'"," F "," R "," F'")
            self.myperms2['OLL-DotT'] = (" F "," R "," U "," R'"," U'"," F'"," z "," B "," R "," U "," R'"," U'"," B'"," z'")
            self.myperms2['OLL-DotQ'] = (" z "," B "," R "," U "," R'"," U'"," B'"," z'"," U "," F "," R "," U "," R'"," U'"," F'")

            self.myperms2['OLL-Square'] = (" x "," L "," U2"," R'"," U'"," R "," U'"," L'"," x'")
            self.myperms2['OLL-SL'] = (" x "," L "," U "," R'"," U "," R "," U2"," L'"," x'")
            self.myperms2['OLL-SC'] = (" x "," L "," U "," R'"," U "," R'"," F "," R "," F'"," R "," U2"," L'"," x'")
            self.myperms2['OLL-Y'] = (" R "," U "," R'"," U'"," R'"," F "," R2"," U "," R'"," U'"," F'")
            self.myperms2['OLL-LargeLI'] = (" F "," U "," R "," U'"," R2"," F'"," R "," U "," R "," U'"," R'")
            self.myperms2['OLL-LargeLJ'] = (" x "," L "," U "," L'"," x'"," R "," U "," R'"," U'"," x "," L "," U'"," L'"," x'")
            self.myperms2['OLL-LC'] = (" F ",) + (" R "," U "," R'"," U'") * 2 + (" F'",)
            self.myperms2['OLL-LJ'] = (" x "," L "," U "," L'"," x'") + (" R "," U "," R'"," U'") * 2 + (" x "," L "," U'"," L'"," x'")
            self.myperms2['OLL-LL'] = (" x "," L "," U'"," x2"," L2"," U "," x2"," L2"," U "," x2"," L2"," U'"," x "," L ")

            self.myperms2['OLL-IC'] = (" F ",) + (" U "," R "," U'"," R'") * 2 + (" F'",)
            self.myperms2['OLL-IO'] = (" x "," L "," U "," L'"," x'") + (" U "," R "," U'"," R'") * 2 + (" x "," L "," U'"," L'"," x'")
            self.myperms2['OLL-ID'] = (" R'"," U'") + (" F "," R'"," F'"," R ") * 2 + (" U "," R ")
            self.myperms2['OLL-III'] = (" R "," U2"," R2"," U'"," R "," U'"," R'"," U2"," F "," R "," F'")

            self.myperms2['OLL-Diagonal'] = (" R "," U "," R'"," U "," R'"," F "," R ", " F'"," U2"," R'"," F "," R "," F'")
            self.myperms2['OLL-VU'] = (" F "," R'"," F'"," R "," U2"," F "," R'"," F'"," R "," U'"," R "," U'"," R'")
            self.myperms2['OLL-VV'] = (" x'"," L'"," R "," U "," R "," U "," R'"," U'"," x "," L "," R2"," F "," R "," F'")

            self.myperms2['OLL-SXI'] = (" R "," U "," R'"," U'"," R "," U'"," R'"," F'"," U'"," F "," R "," U "," R'")
            self.myperms2['OLL-SXJ'] = (" R "," U "," R'"," U "," R "," U2"," R'"," F "," R "," U "," R'"," U'"," F'")

            self.myperms2['OLL-PL'] = (" F "," U "," R "," U'"," R'"," F'")
            self.myperms2['OLL-PJ'] = (" R'"," U'"," F "," U "," R "," U'"," R'"," F'"," R ")

            self.myperms2['OLL-LargeS'] = (" R'"," F "," R "," U "," R'"," U'"," F'"," U "," R ")

            self.myperms2['OLL-TH'] = (" R "," U "," R'"," U'"," R'"," F "," R "," F'")
            self.myperms2['OLL-TU'] = (" F "," R "," U "," R'"," U'"," F'")

            self.myperms2['OLL-CT'] = (" R'"," U'"," R'"," F "," R "," F'"," U "," R ")
            self.myperms2['OLL-CU'] = (" R "," U "," R2"," U'"," R'"," F "," R "," U "," R "," U'"," F'")

            self.myperms2['OLL-SquareXU'] = (" R "," U2"," R2"," F "," R "," F'"," R "," U2"," R'")
            self.myperms2['OLL-SquareXV'] = (" F "," R "," U'"," R'"," U'"," R "," U "," R'"," F'")

            self.myperms2['OLL-W'] = (" R "," U "," R'"," U "," R "," U'"," R'"," U'"," R'"," F "," R "," F'")

            self.myperms2['OLL-X'] = (" R'", ' F2', ' R ', " L'", ' U2', ' L2', " R'", " F'", ' R ', " L'", ' U2', " R'", ' L ', ' F2', ' R ', " L'")
            self.myperms2['OLL-R'] = (" B'", " R'", ' F ', ' R ', ' B ', " F'", " U'", " F'", ' U ', ' F ')
            self.myperms2['OLL-H'] = (" F'", " U'", ' F ', ' U ', ' F ', " B'", " R'", " F'", ' R ', ' B ')


        if self.Centers:
            self.myperms2 = {k:self.myperms2[k] for k in self.myperms2 if k[:4] not in ['Edge','Swap'] and k[:7] not in ['MidEdge'] and k[:2] not in ['CP']}

            self.myperms2['WingSwapSkew-H'] = ("2R2", ' B ', "2D'", ' B ', '2R ', ' B2', ' U2', ' B ', '2D ', " B'", ' U2', '2R2')
            self.myperms2['WingSwapSkew-G'] = ('2L2', ' B ', '2U ', ' B ', "2L'", ' B2', ' U2', ' B ', "2U'", " B'", ' U2', '2L2')
            self.myperms2['WingSwapSkew-D'] = ("2R'", ' B ', "2D'", ' B ', '2R ', ' B2', ' U2', ' B ', '2D ', " B'", ' U2', '2R ')
            self.myperms2['WingSwapSkew-C'] = ('2L ', ' B ', '2U ', ' B ', "2L'", ' B2', ' U2', ' B ', "2U'", " B'", ' U2', "2L'")           
            self.myperms2['WingSwapSkew-Ex'] = (' B ', "2D'", ' B ', '2R ', ' B2', ' U2', ' B ', '2D ', " B'", ' U2')
            self.myperms2['WingSwapSkew-Ey'] = (' B ', '2U ', ' B ', "2L'", ' B2', ' U2', ' B ', "2U'", " B'", ' U2')     
            self.myperms2['WingSwapSkew-Fx'] = ('2R ', ' B ', "2D'", ' B ', '2R ', ' B2', ' U2', ' B ', '2D ', " B'", ' U2', "2R'")
            self.myperms2['WingSwapSkew-Fy'] = ("2L'", ' B ', '2U ', ' B ', "2L'", ' B2', ' U2', ' B ', "2U'", " B'", ' U2', '2L ')

            self.myperms2['Swap_A'] = ('2R ', ' D2', "2R'", ' D2', '2L ', ' D2', ' B2', '2L ', ' B2', "2L'", ' D2')
            self.myperms2['Swap_B'] = ("2R'", ' U ', "2B'", " U'", ' B2', ' U ', '2B ', ' U ', "2R'", ' U2', ' B2', '2R ')
            self.myperms2['Swap_I'] = ('2L ', ' F2', '2L ', '2R ', ' F2', "2R'", ' U2', '2R2', ' B2', '2R ', ' B2', '2R2', ' U2')
            self.myperms2['Swap_J'] = (" F'", "2D'", ' F ', ' U2', " F'", '2D ', " F'", "2R'", ' F2', ' U2')
            self.myperms2['Swap_K'] = ('2R2', " F'", "2D'", ' F ', ' U2', " F'", '2D ', " F'", "2R'", ' F2', ' U2', '2R2')

            
            

            

       

    def _expand_registered_myperms(self):
        """登録済みmyperms2を対称変換展開してmypermsへ写す。"""
        for key in self.myperms2.keys():
            L = self.make_transformations(self.myperms2[key],tuple())
            if self.size < 6:
                Num = 48
            elif len([x for x in self.myperms2[key] if x[0] in ['2','3']]) != 0:
                Num = 96
            else:
                Num = 48
            for i in range(Num):
                   
                if i <= 9:
                    SI = '0' + str(i)
                else:
                    SI = str(i)
                       
                self.myperms[key + SI] = L[0][i]        

        


                
    

    def _init_cube_state_and_moves(self):
        face_keys = ['U','D','F','B','L','R']
        self._init_surface_size()
        self._init_state_colors()
        self._apply_state_masks()
        self.state_0 = self.state.copy()
        self._init_face_nums()
        face_turn_map = self._build_face_turn_map()
        self._init_move_tables(face_keys, face_turn_map)
        self._init_move_keys(face_keys)
        self._init_scramble_sets()
        side_strips = self._build_side_strips()
        self._apply_side_strips(side_strips)
        self._apply_axis_rotations(side_strips)
        self._finalize_axis_rotations()
        self._init_piece_indices()
        self._init_default_colors()

    def _init_surface_size(self):
        self.surface_num = self.size ** 2

    def _init_state_colors(self):
        self.state = np.zeros(self.surface_num * 6,dtype = str)
        self.state[0:self.surface_num] = 'R'
        self.state[self.surface_num:2 * self.surface_num] = 'O'
        self.state[2 * self.surface_num:3 * self.surface_num] = 'Y'
        self.state[3 * self.surface_num:4 * self.surface_num] = 'W'
        self.state[4 * self.surface_num:5 * self.surface_num] = 'G'
        self.state[5 * self.surface_num:6 * self.surface_num] = 'B'

    def _apply_state_masks(self):
        if self.F2L:
            self._mask_f2l_state()
        if self.OLL:
            self._mask_oll_state()
        if self.Cross:
            self._mask_cross_state()
        if self.Centers:
            self._mask_centers_state()
        if self.Edges:
            self._mask_edges_state()

    def _mask_f2l_state(self):
        self.state[0:9] = 'X'
        for i in range(2,6):
            self.state[i * 9 + 0] = 'X'
            self.state[i * 9 + 3] = 'X'
            self.state[i * 9 + 4] = 'X'

    def _mask_oll_state(self):
        self.state[0:9] = 'R'
        for i in range(2,6):
            self.state[i * 9 + 0] = 'X'
            self.state[i * 9 + 3] = 'X'
            self.state[i * 9 + 4] = 'X'

    def _mask_cross_state(self):
        self.state[0:8] = 'X'
        for i in range(2,6):
            self.state[i * 9 + 0] = 'X'
            self.state[i * 9 + 1] = 'X'
            self.state[i * 9 + 2] = 'X'
            self.state[i * 9 + 3] = 'X'
            self.state[i * 9 + 4] = 'X'
            self.state[i * 9 + 5] = 'X'
            self.state[i * 9 + 7] = 'X'
        self.state[9:13] = 'X'

    def _mask_centers_state(self):
        for i in range(6):
            start = i * self.surface_num + 4 * (self.size - 1)
            end = (i + 1) * self.surface_num
            self.state[start:end] = 'X'

    def _mask_edges_state(self):
        for i in range(6):
            end = i * self.surface_num + 4 * (self.size - 1)
            self.state[i * self.surface_num:end] = 'X'

    def _init_face_nums(self):
        self.Nums = {}
        self.Nums['R'] = R_Nums[self.size]
        self.Nums['O'] = self.Nums['R'][::-1,::-1] + self.surface_num
        self.Nums['Y'] = self.Nums['R'][::-1,::-1] + self.surface_num * 2
        self.Nums['W'] = self.Nums['R'] + self.surface_num * 3
        self.Nums['G'] = np.flip(self.Nums['R'].T,axis = 0) + self.surface_num * 4
        self.Nums['B'] = np.flip(self.Nums['R'].T,axis = 1) + self.surface_num * 5

    def _build_face_turn_map(self):
        face_turn_map = np.zeros(0,dtype = 'i')
        quarter_turn = np.array([3,0,1,2],dtype = 'i')
        for i in range(self.surface_num // 4):
            face_turn_map = np.r_[face_turn_map,quarter_turn + 4 * i]
        if self.size % 2 == 1:
            face_turn_map = np.r_[face_turn_map,np.array([self.surface_num - 1])]
        return face_turn_map

    def _init_move_tables(self, face_keys, face_turn_map):
        all_indices = np.arange(self.surface_num * 6,dtype = 'i')
        for j in range(6):
            for i in range(self.size // 2):
                key = self._layer_key(face_keys[j], i)
                self.move[key] = all_indices.copy()
            face_key = " " + face_keys[j] + " "
            self.move[face_key][self.surface_num * j:self.surface_num * (j+1)] = face_turn_map + self.surface_num * j

        if self.size % 2 == 1:
            self.move[" M "] = all_indices.copy()
            self.move[" S "] = all_indices.copy()
            self.move[" E "] = all_indices.copy()

        self.move[" x "] = all_indices.copy()
        self.move[" y "] = all_indices.copy()
        self.move[" z "] = all_indices.copy()

    def _layer_key(self, face_key, layer_index):
        if layer_index != 0:
            return str(layer_index + 1) + face_key + " "
        return " " + face_key + " "

    def _init_move_keys(self, face_keys):
        self.move_keys = [" " + s + t for s in face_keys for t in [" ","'","2"]]
        self.move_keys += [str(i + 1) + s + t for i in range(1,self.size // 2) for s in face_keys for t in [" ","'","2"]]
        if self.size % 2 == 1:
            self.move_keys += [" E "," E'"," E2"," S "," S'"," S2"," M "," M'"," M2"]
        self.move_keys += [" y "," y'"," y2"," z "," z'"," z2"," x "," x'"," x2"]
        self.move_len = len(self.move_keys)
        self.key_to_num = {}
        for i in range(self.move_len):
            self.key_to_num[self.move_keys[i]] = i

    def _init_scramble_sets(self):
        self.my_scrambles2 = {0:{}}
        for key in self.move_keys:
            self.my_scrambles2[0][key] = set([])
        self.counter = {1:{},2:{},3:{},4:{},5:{},6:{},7:{}}

    def _build_side_strips(self):
        side_strips = {}
        for i in range(self.size // 2):
            self._add_layer_side_strips(side_strips, i)
        if self.size % 2 == 1:
            self._add_slice_side_strips(side_strips)
        return side_strips

    def _add_layer_side_strips(self, side_strips, layer_index):
        key_prefix = " " if layer_index == 0 else str(layer_index + 1)
        i = layer_index
        side_strips[key_prefix + 'U' + " "] = [self.Nums['Y'][i,:],self.Nums['G'][:,-1-i],self.Nums['W'][-1-i,::-1],self.Nums['B'][::-1,i]]
        side_strips[key_prefix + 'D' + " "] = [self.Nums['Y'][-1-i,:],self.Nums['B'][::-1,-1-i],self.Nums['W'][i,::-1],self.Nums['G'][:,i]]
        side_strips[key_prefix + 'F' + " "] = [self.Nums['R'][-1-i,:],self.Nums['B'][-1-i,:],self.Nums['O'][-1-i,:],self.Nums['G'][-1-i,:]]
        side_strips[key_prefix + 'B' + " "] = [self.Nums['R'][i,:],self.Nums['G'][i,:],self.Nums['O'][i,:],self.Nums['B'][i,:]]
        side_strips[key_prefix + 'L' + " "] = [self.Nums['R'][:,i],self.Nums['Y'][:,i],self.Nums['O'][::-1,-1-i],self.Nums['W'][:,i]]
        side_strips[key_prefix + 'R' + " "] = [self.Nums['R'][:,-1-i],self.Nums['W'][:,-1-i],self.Nums['O'][::-1,i],self.Nums['Y'][:,-1-i]]

    def _add_slice_side_strips(self, side_strips):
        side_strips[" M "] = [self.Nums['R'][:,self.size // 2],self.Nums['Y'][:,self.size // 2],self.Nums['O'][::-1,self.size // 2],self.Nums['W'][:,self.size // 2]]
        side_strips[" S "] = [self.Nums['R'][self.size // 2,:],self.Nums['B'][self.size // 2,:],self.Nums['O'][self.size // 2,:],self.Nums['G'][self.size // 2,:]]
        side_strips[" E "] = [self.Nums['Y'][self.size // 2,:],self.Nums['B'][::-1,self.size // 2],self.Nums['W'][self.size // 2,::-1],self.Nums['G'][:,self.size // 2]]

    def _apply_side_strips(self, side_strips):
        for key in side_strips.keys():
            for i in range(4):
                for j in range(self.size):
                    self.move[key][side_strips[key][i][j]] = side_strips[key][i-1][j]
            self.move[key[:2] + "'"] = np.argsort(self.move[key])
            self.move[key[:2] + "2"] = self.move[key][self.move[key]]

    def _apply_axis_rotations(self, side_strips):
        for key in side_strips.keys():
            axis_key = " " + self.axis[key[1]] + " "
            if key[1] in ["R","U","F","S"]:
                self.move[axis_key] = self.move[axis_key][self.move[key]]
            else:
                self.move[axis_key] = self.move[axis_key][self.move[self.invert_str(key)]]

    def _finalize_axis_rotations(self):
        for key in [" x "," y "," z "]:
            self.move[key[:2] + "'"] = np.argsort(self.move[key])
            self.move[key[:2] + "2"] = self.move[key][self.move[key]]

    def _init_piece_indices(self):
        self.center_num = (self.size - 2) ** 2
        self.edge_pairs = [((0,0),(2,0)),
                           ((0,1),(4,0)),
                           ((0,2),(3,0)),
                           ((0,3),(5,0)),
                           ((2,3),(4,1)),
                           ((4,3),(3,1)),
                           ((3,3),(5,1)),
                           ((5,3),(2,1)),
                           ((1,0),(3,2)),
                           ((1,1),(4,2)),
                           ((1,2),(2,2)),
                           ((1,3),(5,2))]
        self.AB = AB[self.size]
        self.CL = [((0,0),(2,3),(4,0)),
                   ((0,1),(4,3),(3,0)),
                   ((0,2),(3,3),(5,0)),
                   ((0,3),(5,3),(2,0)),
                   ((1,0),(3,1),(4,2)),
                   ((1,1),(4,1),(2,2)),
                   ((1,2),(2,1),(5,2)),
                   ((1,3),(5,1),(3,2))]
        self.center_index = [(i + self.surface_num * j,) for j in range(6) for i in range(4 * (self.size - 1),self.surface_num)]
        self.edge_index = [(p[0][0] * self.surface_num + p[0][1] + 4 * ab[0],p[1][0] * self.surface_num + p[1][1] + 4 * ab[1]) for ab in self.AB for p in self.edge_pairs]
        self.corner_index = [(cl[0][0] * self.surface_num + cl[0][1],cl[1][0] * self.surface_num + cl[1][1],cl[2][0] * self.surface_num + cl[2][1]) for cl in self.CL]
        self._init_num_to_piece()

    def _init_num_to_piece(self):
        self.num_to_piece = {}
        for i in range(6 * self.surface_num):
            if i % self.surface_num < 4:
                self.num_to_piece[i] = [x for x in self.corner_index if i in x][0]
            elif i % self.surface_num < 4 * (self.size - 1):
                self.num_to_piece[i] = [x for x in self.edge_index if i in x][0]
            else:
                self.num_to_piece[i] = (i,)

    def _init_default_colors(self):
        self.default_color = {}
        for x in self.center_index:
            self.default_color[x] = self.state_0[x[0]]
        for x in self.edge_index:
            self.default_color[x] = self.state_0[x[0]] + self.state_0[x[1]]
        for x in self.corner_index:
            self.default_color[x] = self.state_0[x[0]] + self.state_0[x[1]] + self.state_0[x[2]]

    def _init_color_keys_and_groups(self):
        # エッジ/コーナー配色の識別ID（色並び→番号）
        self.edge_key = {'RB': 0,'BR': 1,'RY': 2,'YR': 3,
                         'RG': 4,'GR': 5,'RW': 6,'WR': 7,
                         'BY': 8,'YB': 9,'YG':10,'GY':11,
                         'GW':12,'WG':13,'WB':14,'BW':15,
                         'OG':16,'GO':17,'OW':18,'WO':19,
                         'OB':20,'BO':21,'OY':22,'YO':23,
                         }

        self.corner_key = {'RBY': 0,'BYR': 1,'YRB': 2,
                           'RYG': 3,'YGR': 4,'GRY': 5,
                           'RGW': 6,'GWR': 7,'WRG': 8,
                           'RWB': 9,'WBR':10,'BRW':11,
                           'OGY':12,'GYO':13,'YOG':14,
                           'OYB':15,'YBO':16,'BOY':17,
                           'OBW':18,'BWO':19,'WOB':20,
                           'OWG':21,'WGO':22,'GOW':23,
                           }

        if self.F2L or self.Edges or self.Cross:
            self.edge_key['XX'] = 0
            self.corner_key['XXX'] = 0

        if self.OLL:
            self.edge_key['RX'] = 0
            self.edge_key['XR'] = 1
            self.corner_key['RXX'] = 0
            self.corner_key['XRX'] = 1
            self.corner_key['XXR'] = 2


            


        # ID順に色並びを並べたリスト
        self.edge_colors = sorted(self.edge_key.keys(),key = lambda x :self.edge_key[x])
        self.corner_colors = sorted(self.corner_key.keys(),key = lambda x :self.corner_key[x])

        # 入力ベクトルの総次元（盤面情報の固定長表現）
        self.ips = 36*self.surface_num + 144 * self.size - 240
        
        # 完全解状態の特徴量（教師データ基準）
        self.perfect_data = self.makedata()                         


        # グループごとのマスクベクトルを作成
        base_vector = np.zeros((1,self.ips),dtype = 'f')
        self.group_val = {}
        self.total_val = {}

        group_vector = base_vector.copy()
        group_vector[0,-192:] = self.perfect_data[-192:]
        self.group_val['A'] = group_vector
        if self.size % 2 == 1:
            group_vector = base_vector.copy()
            group_vector[0,36 * self.center_num:36 * self.center_num + 288] = self.perfect_data[36 * self.center_num:36 * self.center_num + 288]
            self.group_val['B'] = group_vector
            if self.size >= 5:
                group_vector = base_vector.copy()
                group_vector[0,36 * self.center_num + 288:36 * self.center_num + 864] = self.perfect_data[36 * self.center_num + 288:36 * self.center_num + 864]
                self.group_val['C'] = group_vector
                if self.size == 7:
                    group_vector = base_vector.copy()
                    group_vector[0,36 * self.center_num + 864:-192] = self.perfect_data[36 * self.center_num + 864:-192]
                    self.group_val['c'] = group_vector
                else:
                    self.group_val['c'] = base_vector.copy()

            else:
                self.group_val['C'] = base_vector.copy()
                self.group_val['c'] = base_vector.copy()
            
        else:
            self.group_val['B'] = base_vector.copy()
            if self.size >= 4:      
                group_vector = base_vector.copy()
                group_vector[0,36 * self.center_num:36 * self.center_num + 576] = self.perfect_data[36 * self.center_num:36 * self.center_num + 576]
                self.group_val['C'] = group_vector
                if self.size == 6:
                    group_vector = base_vector.copy()
                    group_vector[0,36 * self.center_num + 576:-192] = self.perfect_data[36 * self.center_num + 576:-192]
                    self.group_val['c'] = group_vector
                else:
                    self.group_val['c'] = base_vector.copy()

            else:
                self.group_val['C'] = base_vector.copy()
                self.group_val['c'] = base_vector.copy()

        
        for key in ['D','d','E','e','F','f','G']:
            if not self.Centers:
                group_vector = base_vector.copy()
                for i in range(6):
                    for j in self.Group_Nums[key]:
                        group_vector[0,i + 6 * (i * self.center_num + j - 4 * (self.size - 1))] = 1
                self.group_val[key] = group_vector
            else:
                group_vector = base_vector.copy()
                self.group_val[key] = group_vector
        

        # 各グループのマスク総和（スコア正規化等に利用）
        for key in ['A','B','C','c','D','d','E','e','F','f','G']:
            self.total_val[key] = np.sum(self.group_val[key])
        
        
    


    def _init_myperms_index(self):
        # (ピース, 色)→該当パーム群 の逆引きテーブルを構築
        self.myperms_dict = {}
        for x in self.center_index:
            for c in ['R','O','B','G','Y','W','X']:
                if self.default_color[x] != c:
                    self.myperms_dict[(x,c)] = []
                
        for x in self.edge_index:
            for c in self.edge_key:
                if self.default_color[x] != c:
                    self.myperms_dict[(x,c)] = []


        for x in self.corner_index:
            for c in self.corner_key:
                if self.default_color[x] != c:
                    self.myperms_dict[(x,c)] = []
        
        
        # 各パームを実際に適用して、どのピースが変化するかを登録
        for key in self.myperms.keys():
            if key[:9] != 'BigCenter' and key[:4] not in ["Side"] and key[:3] not in ["L2E","L4I","L4J"] and key[:5] not in ['Super']:
                X = self.myperms[key]
                # 逆順適用で一度位置をずらし、色の変化を観測
                for m in self.invert_moves(X):
                    self.make_move(m)


                for x in self.center_index:
                    c = self.state[x[0]] 
                    if c != self.default_color[x]:
                        self.myperms_dict[(x,c)].append(key)

                for x in self.edge_index:
                    c = self.state[x[0]] + self.state[x[1]]
                    if c != self.default_color[x]:
                        self.myperms_dict[(x,c)].append(key)

                for x in self.corner_index:
                    c = self.state[x[0]] + self.state[x[1]] + self.state[x[2]]
                    if c != self.default_color[x]:
                        self.myperms_dict[(x,c)].append(key)                
                        
                

                # 元に戻す
                for m in X:
                    self.make_move(m)


        # グループ順序のインデックスリスト（評価用）
        self.myperms_order = {}
        
        for key in ['A','B','C','c','D','d','E','e','F','f','G']:
            self.myperms_order[key] = []
            for i in [0,1,2,3,4,5]:
                self.myperms_order[key] += list(np.array(self.Group_Nums[key]) + self.surface_num * i)
                


    def myperms_dict_key(self,S):
        L = []
        for key in self.myperms_dict:
            if S in self.myperms_dict[key]:
                L.append(key)

        return L

    
    def return_axis(self,Moves):
        return tuple([self.axis[x[1]] for x in Moves])
    

    def create_new_set(self):
        i = len(self.my_scrambles2.keys())
        self.my_scrambles2[i] = {}
        for k in self.my_scrambles2[0].keys():
            self.my_scrambles2[i][k] = set([]) 

    def make_move(self,key):
        self.state = self.state[self.move[key]]


    def scramble(self,N,Move = None,difficult_mode = False,scramble_mode = None,flip = None,rotate = None,swap = False,add_moves = False,transform_N = None,flip_inside = None):
        if Move != None:
            return self._apply_moves_and_return(Move)

        if scramble_mode not in ['Centers','myperms','Edges','Slices','OLL']:
            return self._simple_scramble(N)

        return self._guided_scramble(N,add_moves,transform_N,flip_inside)

    def _apply_moves_and_return(self, Move):
        for m in Move:
            self.make_move(m)
        return tuple(Move)

    def _simple_scramble(self, N):
        move_lis = self._generate_simple_scramble_moves(N)
        self._apply_scramble_moves(move_lis)
        return tuple(move_lis)

    def _generate_simple_scramble_moves(self, N):
        move_lis = []
        for _ in range(N):
            move_lis.append(random.choice(self.move_keys))
        return tuple(move_lis)

    def _guided_scramble(self, N, add_moves, transform_N, flip_inside):
        move_count = self._init_scramble_count()
        transform_index = self._resolve_transform_index(transform_N)
        use_flip_inside = self._resolve_flip_inside(flip_inside)

        move_lis = []
        for level_index in range(N):
            selected_moves = self._guided_scramble_moves(level_index,move_count,add_moves)
            transformed_moves = self._transform_scramble_moves(selected_moves,transform_index,use_flip_inside)
            self._append_scramble_moves(move_lis,transformed_moves)
            self._apply_scramble_moves(transformed_moves)

        return tuple(move_lis)

    def _init_scramble_count(self):
        count = heapdict()
        for key in self.move_keys:
            count[key] = 0
        return count

    def _guided_scramble_moves(self, level_index, move_count, add_moves):
        candidates = self._collect_scramble_candidates(level_index)
        selected_moves = self._select_scramble_candidate(candidates,move_count,add_moves,level_index)
        self._update_count(move_count,selected_moves)
        self._update_counter_stats(level_index,selected_moves)
        return selected_moves

    def _transform_scramble_moves(self, moves, transform_index, use_flip_inside):
        transformed_moves = self.transform(moves,transform_index)
        if use_flip_inside:
            transformed_moves = self.flip_inside_moves(transformed_moves)
        return transformed_moves

    def _append_scramble_moves(self, move_lis, moves):
        move_lis += list(moves)

    def _apply_scramble_moves(self, moves):
        for move in moves:
            self.make_move(move)

    def _resolve_transform_index(self, transform_N):
        if transform_N is not None:
            return transform_N
        if self.F2L or self.OLL:
            return random.choice([0])
        if self.size >= 6:
            return random.randrange(96)
        return random.randrange(48)

    def _resolve_flip_inside(self, flip_inside):
        if flip_inside is not None:
            return flip_inside
        return bool(random.randint(0,1))

    def _collect_scramble_candidates(self, level_index):
        move_keys = sorted(self.move_keys,key = lambda key:len(self.my_scrambles2[1][key]))
        candidates = []
        for key in move_keys:
            candidates += list(self.my_scrambles2[level_index][key])
        return candidates

    def _select_scramble_candidate(self, candidates, Count, add_moves, level_index):
        if add_moves:
            return self._select_candidate_max(candidates,Count,level_index)
        return self._select_candidate_min(candidates,Count,level_index)

    def _select_candidate_max(self, candidates, Count, level_index):
        top_V = -1
        top_V2 = 0
        M = ()
        for s in candidates:
            V = 0
            for m in s:
                V += Count[m]
            if level_index == 0:
                V2 = random.uniform(0,1)
            else:
                V2 = 0
            if top_V < V or (top_V == V and top_V2 < V2):
                top_V = V
                top_V2 = V2
                M = s
        return M

    def _select_candidate_min(self, candidates, Count, level_index):
        top_V = 1.0e+8
        top_V2 = 1
        M = ()
        for s in candidates:
            V = 0
            for m in s:
                V += Count[m]
            if level_index == 0:
                V2 = random.uniform(0,1)
            else:
                V2 = 1
            if top_V > V or (top_V == V and top_V2 > V2):
                top_V = V
                top_V2 = V2
                M = s
        return M

    def _update_count(self, Count, M):
        for m in M:
            Count[m] += 1

    def _update_counter_stats(self, level_index, M):
        if level_index != 0 and level_index < 8:
            if M not in self.counter[level_index]:
                self.counter[level_index][M] = 1
            else:
                self.counter[level_index][M] += 1

    def swap_2_3(self,move):
        if move[0] == "2":
            return "3" + move[1:]
        elif move[0] == "3":
            return "2" + move[1:]
        else:
            return move



    def flip_moves(self,Moves,axis = None):
        """指定軸の鏡映ルールで手順列を変換する。"""
        return self.move_ops.flip_moves(Moves,axis = axis)

    def rotate_moves(self,Moves,axis = None):
        """指定回転ルールで手順列を回転変換する。"""
        return self.move_ops.rotate_moves(Moves,axis = axis)

    def diag_flip_moves(self,Moves):
        """対角反転ルールで手順列を変換する。"""
        return self.move_ops.diag_flip_moves(Moves)

    def invert_str(self,s):
        """1手だけ逆回転に変換する。"""
        return self.move_ops.invert_str(s)

    def invert_moves(self,Moves):
        """手順列を逆順・逆回転にした列を返す。"""
        return self.move_ops.invert_moves(Moves)

    def swap_moves(self,Moves):
        """2層・3層の手を入れ替える補助変換を適用する。"""
        return self.move_ops.swap_moves(Moves)

    def flip_inside(self,s):
        """1手だけ内外反転ルールで変換する。"""
        return self.move_ops.flip_inside(s)

    def flip_inside_moves(self,Moves):
        """内外反転ルールで手順列を変換する。"""
        return self.move_ops.flip_inside_moves(Moves)
    


    def reduce(self,move_lis):
        L = []
        states = [''.join(self.state)]
        Indices = []
        idx = 0
        for m in move_lis:
            self.make_move(m)
            s = ''.join(self.state)
            if s in states:
                i = states.index(s)
                L = L[:i]
                states = states[:i+1]
                Indices = Indices[:i]

            else:
                L.append(m)
                states.append(''.join(self.state))
                Indices.append(idx)

            idx += 1

        
        for m in self.invert_moves(move_lis):
            self.make_move(m)

        
                


        return (tuple(L),Indices) 

    def simplify(self,move_lis):
        """同じ面・同じ層の連続手をまとめて手順列を簡約する。"""
        return self.move_ops.simplify(move_lis)

    def conjugate(self,A,B):
        """共役 A B A^-1 を作って簡約した手順列を返す。"""
        return self.move_ops.conjugate(A,B)

    def commutator(self,A,B):
        """交換子 A B A^-1 B^-1 を作って簡約した手順列を返す。"""
        return self.move_ops.commutator(A,B)
        
    def reset(self):
        self.state[:] = self.state_0

    def makedata(self):
        centers = np.zeros(6 * self.center_num,dtype = str)
        for i in range(6):
            centers[self.center_num*i:self.center_num*(i+1)] = self.state[4 * (self.size-1)+self.surface_num * i:self.surface_num * (i+1)]

        Z = np.zeros((6 * self.center_num,6),dtype = 'f')
        for i in range(6):
            Z[:,i][centers == self.colors[i]] = 1

        X = np.zeros(self.ips,dtype = 'f')
        B = 36 * self.center_num

        X[:B] = Z.reshape(-1)
    

        for ei in self.edge_index:
            if self.state[ei[0]] + self.state[ei[1]] != 'XX':
                X[B + self.edge_key[self.state[ei[0]] + self.state[ei[1]]]] = 1
                B += 24

        for ci in self.corner_index:
            if self.state[ci[0]] + self.state[ci[1]] + self.state[ci[2]] != 'XXX':
                X[B + self.corner_key[self.state[ci[0]] + self.state[ci[1]] + self.state[ci[2]]]] = 1
                B += 24


        return X
        
    def is_perfect(self):
        return (self.state == self.state_0).all()


    def transform(self,s,i,flip_inside = False,invert = False):
        """変換indexに対応する対称変換を手順列へ適用する。"""
        return self.move_ops.transform(s,i,flip_inside = flip_inside,invert = invert)

    def _transformation_key(self, transform_index, invert = False):
        """変換indexから、実際に適用する変換手順列を取り出す。"""
        return self.move_ops._transformation_key(transform_index,invert = invert)

    def _apply_transform_step(self, moves, transform_step):
        """変換手順1つ分だけ手順列へ反映する。"""
        return self.move_ops._apply_transform_step(moves,transform_step)

    def make_transformations(self,s,Moves):
        """全ての対称変換について、scramble列とmove列の組を作る。"""
        return self.move_ops.make_transformations(s,Moves)



    def state_to_str(self):
        return reduce(lambda x,y : x+y , self.state)

    def set_state(self,S):
        if len(S) == 6 * self.surface_num:
            self.state[:] = np.array(list(S))


class Affine:
    def __init__(self,ips,ops):
        self.W = np.random.randn(ops,ips).astype('f') / math.sqrt(ips / 2)
        self.B = np.random.randn(ops).astype('f')
        self.B[:] = 0
        self.dW = np.zeros_like(self.W,dtype = 'f')
        self.dB = np.zeros_like(self.B,dtype = 'f')
        self.x = np.empty((0,0),dtype = 'f')
        self.dx = np.empty((0,0),dtype = 'f')
        self.out = np.empty((0,0),dtype = 'f')


    def forward(self,x):
        self.x = x
        self.out = self.W @ x
        self.out += self.B.reshape(-1,1)

        return self.out

    def backward(self,dO):
        self.dx = self.W.T @ dO
        self.dW = dO @ self.x.T
        self.dB = np.sum(dO,axis = 1)

        return self.dx

def relu(x):
    y = x.copy()
    y[y<0] = 0

    return y

class ReLU:
    def __init__(self):
        self.out = np.empty((0,0),dtype = 'f')

    def forward(self,x):
        self.out = relu(x)
        return self.out

    def backward(self,dO):
        dO = dO * np.sign(self.out)
        return dO

def huber(x):
    y = x ** 2 / 2
    y[y>0.5] = abs(x[y>0.5]) - 0.5

    return y


def hard_sigmoid(x):
    y = x.copy()
    y[y > 1] = 1
    y[y < -1] = -1

    return y

class Hard_Sigmoid:
    def __init__(self):
        self.out = np.empty((0,0),dtype = 'f')

    def forward(self,x):
        self.out = hard_sigmoid(x)
        return self.out

    def backward(self,dO):
        dO[self.out == 1] = 0
        dO[self.out == -1] = 0
        return dO

def sigmoid(x):
    return np.where(x > 40,1.0,np.exp(x) / (1 + np.exp(x)))

class Sigmoid:
    def __init__(self):
        self.out = np.empty((0,0),dtype = 'f')

    def forward(self,x):
        self.out = sigmoid(x)
        return self.out

    def backward(self,dO):
        dO *= self.out * (1.0 - self.out)
        return dO



class Q_loss:
    def __init__(self,g):
        self.args = np.zeros(0,dtype = 'i')
        self.x = np.zeros(0,dtype = 'f')
        self.rewards = np.zeros(0,dtype = 'f')
        self.maxargs = np.zeros(0,dtype = 'i')
        self.v = np.zeros(0,dtype = 'f')
        self.X = np.zeros(0,dtype = 'i')
        self.g = g

        

    def forward(self,x,args,rewards):
        self.args = args
        self.x = x
        self.rewards = rewards

        self.maxargs = np.argmax(x[:,1:],axis = 0)

        self.X = np.arange(1,x.shape[1])

        self.v = self.x[self.args,self.X - 1] - self.rewards - self.g * self.x[self.maxargs,self.X]


        return np.sum(self.v ** 2)/2
        #return np.sum(huber(self.v))

    def backward(self):
        dO = np.zeros_like(self.x)

        #dv = self.v.copy()
        #dv[dv >= 1] = 1
        #dv[dv <= -1] = -1
        #dO[self.args,self.X - 1] += dv
        
        dO[self.args,self.X - 1] += self.v
        dO[self.maxargs,self.X] -= self.g * self.v
        


        return dO
        
class MSE:
    def __init__(self):
        self.x = np.zeros(0,dtype = 'f')
        self.t = np.zeros(0,dtype = 'f')
        self.w = np.ones((1,0),dtype = 'f')

    def forward(self,x,t,w = None):
        self.x = x
        self.t = t
        if w is None:
            self.w = np.ones_like(t,dtype = 'f')
        else:
            self.w = w

        return np.sum(self.w * (x - t) ** 2) / 2
    
    def backward(self):
        return self.w * (self.x - self.t)
    

class Soft_Target_Cross_Entropy:
    def __init__(self):
        self.y = np.zeros((0,0),dtype = 'f')
        self.t = np.zeros((0,0),dtype = 'f')
        self.w = np.ones((1,0),dtype = 'f')

    def forward(self,x,t,w = None):
        self.t = t
        self.y = softmax(x)
        if w is None:
            self.w = np.ones((1,t.shape[1]),dtype = 'f')
        else:
            self.w = w
        return -np.sum(self.w * t * np.log(self.y + 1.0e-7))

    def backward(self):
        return self.w * (self.y - self.t)


def softmax(x):
    y = x.copy()
    y -= np.max(y,axis = 0)
    y = np.exp(y)
    

    return y / np.sum(y,axis = 0)


def softmax_H(x):
    y = x.copy()
    y -= np.max(y,axis = 1)
    y = np.exp(y)
    

    return y / np.sum(y,axis = 1)    




def cross_entropy(y,t):
    return -np.sum(t * np.where(y != 0 , np.log(y),-100))



        

class Softmax_Cross_Entropy:
    def __init__(self):
        self.x = np.zeros(0,dtype = 'f')
        self.y = np.zeros(0,dtype = 'f')
        self.t = np.zeros(0,dtype = 'f')
        self.Indices = None

    def forward(self,x,args,rewards,Indices,t = None):
        self.Indices = Indices
        self.x = x
        self.y = np.zeros((self.x.shape[0],0),dtype = 'i')
        self.t = np.zeros((self.x.shape[0],0),dtype = 'i')
        for i in range(len(Indices) - 1):
            self.y = np.c_[self.y,softmax(x[:,Indices[i]:Indices[i+1]-1])]

        if t is None:
            self.t = np.zeros_like(self.y,dtype = 'f')
            self.t[args,np.arange(self.t.shape[1])] = 1
        else:
            self.t = t
        return cross_entropy(self.y,self.t)

    def backward(self):
        dO = np.zeros_like(self.x)
        for i in range(len(self.Indices) -1):
            dO[:,self.Indices[i]:self.Indices[i+1] - 1] = self.y[:,self.Indices[i] - i:self.Indices[i+1] - i - 1] - self.t[:,self.Indices[i] - i:self.Indices[i+1] - i - 1]
        return dO

class Myloss:
    def __init__(self):
        self.x = np.zeros(0,dtype = 'f')
        self.y = np.zeros(0,dtype = 'f')
        self.t = np.zeros(0,dtype = 'f')
        self.Indices = None

    def forward(self,x,Indices):

        self.y = np.zeros((1,Indices[-1]),dtype = 'f')
        self.t = np.zeros((1,Indices[-1]),dtype = 'f')
        for i in range(len(Indices) - 1):
            self.y[:,Indices[i]:Indices[i+1]] = softmax_H(x[:,Indices[i]:Indices[i+1]])
            self.t[0,Indices[i+1]-1] = 1.0
        
        return cross_entropy(self.y,self.t)
        
        #self.x = x
        #self.Indices = Indices
        #self.y = np.zeros((1,0),dtype = 'f')
        #for i in range(len(Indices) - 1):
        #    self.y = np.c_[self.y,self.x[:,Indices[i] + 1:Indices[i + 1]] - self.x[:,Indices[i]:Indices[i + 1] - 1]]
        
        #self.y = sigmoid(self.y)

        #return np.sum(self.y)
        

    def backward(self):
        return self.y - self.t
        #dO = np.zeros_like(self.x)
        #for i in range(len(self.Indices) - 1):
        #    dO[:,self.Indices[i]:self.Indices[i + 1] - 1] += self.y[:,self.Indices[i] - i:self.Indices[i + 1] - (i + 1)] * (1.0 - self.y[:,self.Indices[i] - i:self.Indices[i + 1] - (i + 1)])
        #    dO[:,self.Indices[i] + 1:self.Indices[i + 1]] -= self.y[:,self.Indices[i] - i:self.Indices[i + 1] - (i + 1)] * (1.0 - self.y[:,self.Indices[i] - i:self.Indices[i + 1] - (i + 1)])  
                        


        #return dO
    

class Batch_Normalization:
    def __init__(self,size):
        self.size = size
        self.m = np.zeros(size,dtype = 'f')
        self.s = np.ones(size,dtype = 'f')
        self.g = np.random.uniform(0.5,2,(size,)).astype('f')
        self.b = np.random.uniform(-0.5,0.5,(size,)).astype('f')
        self.dg = None
        self.db = None
        self.m_batch = np.zeros(size,dtype = 'f')
        self.s_batch = np.zeros(size,dtype = 'f')
        self.x_bar = None

        self.N = 0 


        self.train_m = None
        self.train_s = None
        self.x = None
        self.y = None

    def forward(self,x,loss = False):
        if loss:
            self.x = x
            self.train_m = np.average(x,axis = 1)
            self.train_s = np.std(x,axis = 1)
            self.x_bar = (x - self.train_m.reshape(-1,1)) / (self.train_s.reshape(-1,1) + 1.0e-7)
            self.y = self.g.reshape(-1,1) * self.x_bar + self.b.reshape(-1,1)

            self.m_batch += self.train_m
            self.s_batch += self.train_s
            self.N += 1

            return self.y

        else:
            x_bar = (x - self.m.reshape(-1,1)) / (self.s.reshape(-1,1) + 1.0e-7)

            return self.g.reshape(-1,1) * x_bar + self.b.reshape(-1,1)
        

    def backward(self,dO):
        self.dg = np.sum(self.x_bar * dO,axis = 1)
        self.db = np.sum(dO,axis = 1)

        return self.g.reshape(-1,1) / (self.train_s.reshape(-1,1) + 1.0e-7) * (dO- (self.db.reshape(-1,1) + self.x_bar * self.dg.reshape(-1,1)) / self.x.shape[1])

    def set_ms(self):
        self.m[:] = self.m_batch / self.N
        self.s[:] = self.s_batch / self.N

        #print(self.N,np.average(self.m),np.average(self.s))

        self.N = 0
        self.m_batch[:] = 0
        self.s_batch[:] = 0
        

            

        
            
        


class data:
    def __init__(self,scramble,moves,rewards):
        self.scramble = scramble
        self.moves = moves
        self.rewards = rewards
        self.succeeded = False


class data_search3:
    def __init__(self,scramble,moves,rewards,root_value,value_trace,best_value,stats,policy_target = None,search_mode = 'search3',sample_weight = 1.0,value_targets = None,root_value_raw = None,value_trace_raw = None,best_value_raw = None):
        self.scramble = scramble
        self.moves = moves
        self.rewards = rewards
        self.root_value = root_value
        self.value_trace = value_trace
        self.best_value = best_value
        self.root_value_raw = root_value if root_value_raw is None else root_value_raw
        self.value_trace_raw = value_trace if value_trace_raw is None else value_trace_raw
        self.best_value_raw = best_value if best_value_raw is None else best_value_raw
        self.stats = stats
        self.policy_target = policy_target
        self.search_mode = search_mode
        self.search_depth3 = 100
        self.sample_weight = sample_weight
        self.value_targets = value_targets
        self.succeeded = False


class SearchResult:
    def __init__(self, succeeded, moves, root_value, value_trace, best_value, stats, policy_target = None, search_mode = 'search2', end_reason = 'budget', attempt_results = None, attempt_index = None, root_value_raw = None, value_trace_raw = None, best_value_raw = None):
        self.succeeded = succeeded
        self.moves = tuple(moves)
        self.root_value = root_value
        self.value_trace = list(value_trace)
        self.best_value = best_value
        self.root_value_raw = root_value if root_value_raw is None else root_value_raw
        self.value_trace_raw = list(value_trace) if value_trace_raw is None else list(value_trace_raw)
        self.best_value_raw = best_value if best_value_raw is None else best_value_raw
        self.stats = stats
        self.policy_target = policy_target
        self.search_mode = search_mode
        self.end_reason = end_reason
        self.attempt_results = [] if attempt_results is None else list(attempt_results)
        self.attempt_index = attempt_index

    def __getitem__(self, index):
        legacy_values = (
            self.succeeded,
            self.moves,
            self.root_value,
            self.value_trace,
            self.best_value,
            self.stats,
        )
        return legacy_values[index]
        




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
        counter = np.zeros(2,dtype = 'i')
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
        batch_size = min(len(frontier),100)
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
        features = np.zeros((self.ips,batch_size))
        priority_weights = np.zeros(batch_size)
        invalid_move_mask = np.zeros((move_count,batch_size),dtype = bool)

        for index, key in enumerate(key_list):
            self._apply_moves(key)
            self._apply_inverse_mask(key, invalid_move_mask, index)
            if self.cube.is_perfect():
                self._revert_moves(key)
                value_history = self._build_value_history(value_by_key, key, self.ai.perfect_val)
                early_result = SearchResult(True, key, value_history[0], value_history, self.ai.perfect_val, counter, search_mode = 'search2', end_reason = 'solved')
                return features[:, :1], priority_weights[:1], invalid_move_mask[:, :1], early_result

            features[:,index] = self.cube.makedata().reshape(-1)
            priority_weights[index] = -priorities[index]
            self._revert_moves(key)

        return features, priority_weights, invalid_move_mask, None

    def _apply_inverse_mask(self, key, invalid_move_mask, column_index):
        if len(key) > 0:
            removed_moves = {self.cube.invert_str(key[-1])}
        else:
            removed_moves = set([])
        filtered_moves = filter(lambda move: move[:2] in removed_moves,self.cube.move_keys)
        for move in filtered_moves:
            move_index = self.cube.move_keys.index(move)
            invalid_move_mask[move_index,column_index] = True

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
                result = SearchResult(False, best_key, root_value, value_history, value_by_key[best_key], counter, search_mode = 'search2', end_reason = 'budget')
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
                frontier[next_key] = -move_priors[move_index,key_index]

    def _finalize_search(self, best_key, value_by_key, counter):
        for move in best_key:
            self.cube.make_move(move)
        is_perfect = self.cube.is_perfect()
        for move in self.cube.invert_moves(best_key):
            self.cube.make_move(move)
        value_history = self._build_value_history(value_by_key, best_key)
        end_reason = 'solved' if is_perfect else 'budget'
        return SearchResult(is_perfect, best_key, value_history[0], value_history, value_by_key[best_key], counter, search_mode = 'search2', end_reason = end_reason)

    def _apply_moves(self, key):
        for move in key:
            self.cube.make_move(move)

    def _revert_moves(self, key):
        for move in self.cube.invert_moves(key):
            self.cube.make_move(move)

    def _build_value_history(self, value_by_key, key, tail_value = None):
        value_history = []
        for index in range(len(key)):
            value_history.append(value_by_key[key[:index]])
        if tail_value is None:
            value_history.append(value_by_key[key])
        else:
            value_history.append(tail_value)
        return value_history


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
        prediction = self.ai._predict_search2(feature.reshape(-1,1))
        self.prediction_cache[state_key] = prediction
        return prediction

    def _predict_leaf_batch(self, pending_leaves):
        if len(pending_leaves) == 0:
            return
        features = np.zeros((self.ips,len(pending_leaves)))
        for index, pending_leaf in enumerate(pending_leaves):
            features[:,index] = pending_leaf['feature']
        predictions = self.ai._predict_search2(features)
        for index, pending_leaf in enumerate(pending_leaves):
            state_key = pending_leaf['state_key']
            prediction = predictions[:,index:index + 1]
            self.prediction_cache[state_key] = prediction
            node_P = prediction[:-1].reshape(-1)
            node_V = prediction[-1,0]
            child_node = self.node_cache.get(state_key)
            if child_node is None:
                child_node = self._create_node(state_key, node_P, node_V)
            else:
                child_node.P[:] = node_P
                child_node.value = node_V
            pending_leaf['parent_node'].children[pending_leaf['move_label']] = child_node
            pending_leaf['path_nodes'].append(child_node)
            pending_leaf['node_value'] = sigmoid(node_V)

    def _create_node(self, state_key, node_P, node_value = None,C = 0.05):
        node = Node(node_P, state_key, node_value,C = self.ai.search3_C)
        self.node_cache[state_key] = node
        return node

    def _create_node_from_current_state(self,C = 0.05):
        state_key = self._state_key()
        node_PV = self._predict_current_state()
        node_P = node_PV[:-1].reshape(-1)
        node_V = node_PV[-1,0]
        node = self.node_cache.get(state_key)
        if node is None:
            node = self._create_node(state_key, node_P, node_V, C = C)
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

    def _ensure_root_node(self,C = 0.05):
        self._sync_root()
        root_prediction = self._predict_current_state()
        root_value = root_prediction[-1,0]
        if self.root_node is None:
            root_P = root_prediction[:-1].reshape(-1)
            self.root_node = self._create_node(self._state_key(), root_P, root_value,C = C)
            self.root_state_key = self._state_key()
        return root_value

    def _evaluate_move_sequence(self, moves):
        if len(moves) == 0:
            return sigmoid(self._predict_current_state()[-1,0])
        for move in moves:
            self.cube.make_move(move)
        leaf_value = sigmoid(self._predict_current_state()[-1,0])
        for move in self.cube.invert_moves(tuple(moves)):
            self.cube.make_move(move)
        return leaf_value

    def _value_trace_for_moves(self, root_value, moves):
        value_trace = [root_value]
        if len(moves) == 0:
            return value_trace
        for move in moves:
            self.cube.make_move(move)
            value_trace.append(sigmoid(self._predict_current_state()[-1,0]))
        for move in self.cube.invert_moves(tuple(moves)):
            self.cube.make_move(move)
        return value_trace

    def _raw_value_trace_for_moves(self, root_value_raw, moves):
        value_trace = [root_value_raw]
        if len(moves) == 0:
            return value_trace
        for move in moves:
            self.cube.make_move(move)
            value_trace.append(self._predict_current_state()[-1,0])
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
        for depth in range(len(path_indices) - 1,-1,-1):
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

    def search3(self, N, C = 0.05):
        root_value_raw = self._ensure_root_node(C = C)
        root_value = sigmoid(root_value_raw)
        root_node = self.root_node
        solved_move = None
        remaining_playouts = N
        batch_size = min(getattr(self.ai,'search_batch3',32), N)
        max_depth = max(1, getattr(self.ai,'search_depth3',100))
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
        stats = np.array([np.max(local_visits), total_playouts],dtype = 'i')

        if solved_move is not None:
            best_moves = solved_move
            best_value = 1.0
            raw_value_trace = self._raw_value_trace_for_moves(root_value_raw, best_moves)
            raw_best_value = raw_value_trace[-1]
            value_trace = self._value_trace_for_moves(root_value, best_moves)
            if len(value_trace) > 0:
                value_trace[-1] = best_value
            return SearchResult(True, best_moves, root_value, value_trace, best_value, stats, root_node.visited.copy(), 'search3', 'solved', root_value_raw = root_value_raw, value_trace_raw = raw_value_trace, best_value_raw = raw_best_value)

        best_moves = self._principal_variation(root_node)
        if len(best_moves) == 0:
            best_moves = (self.cube.move_keys[np.argmax(root_node.visited)],)
        raw_value_trace = self._raw_value_trace_for_moves(root_value_raw, best_moves)
        best_value_raw = raw_value_trace[-1]
        best_value = sigmoid(best_value_raw)
        value_trace = self._value_trace_for_moves(root_value, best_moves)
        return SearchResult(False, best_moves, root_value, value_trace, best_value, stats, root_node.visited.copy(), 'search3', 'budget', root_value_raw = root_value_raw, value_trace_raw = raw_value_trace, best_value_raw = best_value_raw)
                


        

class Node:
    def __init__(self,P,state_key = None,value = None,C = 0.05):
        self.P = P
        self.state_key = state_key
        self.value = value
        self.val = np.zeros_like(P,dtype = 'f')
        self.visited = np.zeros_like(P,dtype = 'i')
        self.S = 0
        self.C = C
        self.children = {}
        

    def select_node(self, invalid_index = None):
        score = np.where(self.visited != 0,self.val / self.visited,0.5) + self.C * self.P * np.sqrt(max(1,self.S)) / (1 + self.visited)
        if invalid_index is not None:
            score[invalid_index] = -1000000000
        if self.S == 0:
            if invalid_index is not None:
                prior = self.P.copy()
                prior[invalid_index] = -1000000000
                return np.argmax(prior)
            return np.argmax(self.P)
        return np.argmax(score)






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

if __name__ == '__main__':
    F = Frame()
    F.pack()
    F.mainloop()