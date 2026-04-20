import numpy as np
import tkinter as Tk
import pickle

from functools import reduce
from cube.rubiks_cube import Rubiks_3
from ai.rubiks_ai import Rubiks_3_AI
from model.search_result import data
from managers.debug_analysis import DebugAnalysisManager
from managers.last_perms_reporter import LastPermsReporter
from managers.learn_manager import LearnManager
from managers.myperm_manager import MyPermManager
from managers.param_manager import ParamManager
from managers.search_data import SearchDataManager
from managers.solve_session import SolveSessionManager, SolveSessionState
from ui.control_panel import ControlPanel
from ui.dialogs import lp_show_key
from ui.viewers import Move_Button, Move_viewer, Prob_viewer, State_viewer, SuccessViewer

np.set_printoptions(suppress=True)

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
                  (" U ","2R "," U'","3F "),
                  (" U ","2R2"," U'","3F "),
                  (" R "," U "," M "," U2"," M'"," U "," R'"),
                  (" R "," U "," M "," U2"," M'"," U "," R'") + self.cube.myperms['ParitySwap-A0-00'],
                  self.cube.invert_moves(self.cube.myperms['BigRJ(0)00']),
                  self.cube.invert_moves(self.cube.myperms['BigRJ(2)00']),
                  self.cube.myperms['Wing3-N04-00'],
                  self.cube.myperms['Wing3-N06-00'],
                  self.cube.myperms['Wing3-Q04-00'],
                  self.cube.myperms['Wing3-Q06-00'],
                  self.cube.myperms['Wing3-O00-00'],
                  self.cube.myperms['Wing3-O02-00'],
                  self.cube.myperms['Wing3-Y00-00'],
                  self.cube.myperms['Wing3-Y02-00'],
                  self.cube.myperms['Wing3-U04A-00'],
                  self.cube.myperms['Wing3-U06A-00'],
                  self.cube.myperms['Wing3-V04A-00'],
                  self.cube.myperms['Wing3-V06A-00'],
                  ("2U "," R2","2U'"," L2","2U "," R2","2U'"," L2"),
                  (" D'", "2F'", ' D ', ' F ', " D'", "2F ", ' D ', " F'"),
                  ("2R "," D ","3F "," D'","2R'"," D ","3F'"," D'","2R'"," D ","3F'"," D'","2R "," D ","3F "," D'"),
                  ("3F2", ' U ', "2R2", " U'", "3F'", ' U ', "2R'", " U'", "3F'", ' U ', "2R'", " U'"),
                  ("3F2", ' U ', "2R'", " U'", "3F'", ' U ', "2R2", " U'", "3F'", ' U ', "2R'", " U'"),
                  ("3F'", " D'", "2R'", ' D ', '3F ', " D'", '2R ', ' D ', '3F ', " D'", '2R ', ' D ', "3F'", " D'", "2R'", ' D ', " L'", '2F2', ' L ', '3U2', " L'", '2F2', ' L ', '3U2'),
                  ('2R ', " U'", '3F ', ' U ', "2R'", " U'", "3F'", '2L2', '2B2', " U'", '3R2', ' U ', '2B2', '2L2', " U'", '3R2', ' U2'),
                  (" S2", ' U ', "2R2", " U'", " S'", ' U ', "2R'", " U'", " S'", ' U ', "2R'", " U'"),
                  (" S2", ' U ', "2R'", " U'", " S'", ' U ', "2R2", " U'", " S'", ' U ', "2R'", " U'"),
                  ("3F2", ' U ', " M2", " U'", "3F'", ' U ', " M'", " U'", "3F'", ' U ', " M'", " U'"),
                  ("3F2", ' U ', " M'", " U'", "3F'", ' U ', " M2", " U'", "3F'", ' U ', " M'", " U'"),
                  ("2F2", ' U ', "2R2", " U'", "2F'", ' U ', "2R'", " U'", "2F'", ' U ', "2R'", " U'"),
                  ("2F2", ' U ', "2R'", " U'", "2F'", ' U ', "2R2", " U'", "2F'", ' U ', "2R'", " U'"),

                  self.cube.invert_moves(self.cube.myperms['Oblique-Center-Opp4-YC-00']),
                  self.cube.invert_moves(self.cube.myperms['Oblique-Center-Opp4-ZB-00']),
                  self.cube.invert_moves(self.cube.myperms['Oblique-Center-Opp4-T-00']),
                  (" M'"," U "," M "," U'"," F'"," M "," F "," M'"),
                  (" M'"," U "," M "," U'"," F "," M "," F'"," M'"),
                  (" M'"," U'"," M "," U "," F'"," M "," F "," M'"),
                  (" M'"," U'"," M "," U "," F "," M "," F'"," M'"),

                  self.cube.myperms['CenterMidEdgeSwap-SG(0)00'],
                  self.cube.myperms['CenterMidEdgeSwap-SH(0)00'],
                  self.cube.myperms['CenterMidEdgeSwap-SG(1)00'],
                  self.cube.myperms['CenterMidEdgeSwap-SH(1)00'],
                  


                ]
            


            
            S0 = [("2L'","2R'",'3D2','2R ',' U ',"2R'",'3D2','2R '," U'","2L "),
                  ("2B ","2R ","3U ","2R'"," U'","2R ","3U'","2R'"," U ","2B'"),
                  
                  
                  
            
                  
                  
                  
                  
                  
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
            ['CoreCenter','ObliqueCenter-A','PlusCenter-Layer2','XCenter-Layer2','ObliqueCenter-B','PlusCenter-Layer3','XCenter-Layer3','Wing-Layer2','Wing-Layer3','Corner','MidEdge'],
            ['Wing-Layer3','Wing-Layer2','MidEdge','Corner','XCenter-Layer2','PlusCenter-Layer2','ObliqueCenter-A','XCenter-Layer3','PlusCenter-Layer3','ObliqueCenter-B','CoreCenter'],
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
            
            
            

        self.AIs[10].search3_C = 0.05
        self.AIs[11].search3_C = 0.05
        self.AIs[12].search3_C = 0.05
        self.AIs[13].search3_C = 0.05
        self.AIs[14].search3_C = 0.05
        self.AIs[15].search3_C = 0.05
        self.AIs[16].search3_C = 0.05
        self.AIs[17].search3_C = 0.05
        self.AIs[18].search3_C = 0.05
        self.AIs[19].search3_C = 0.05

            




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
                self.transform_idx = [0,48,48,0,48,0,48,0,0,48] * 2
            else:
                self.transform_idx = [0,0,0,0,0,0,0,0,0,0] * 2
        elif self.cube_size >= 6:
            self.transform_idx = [0,1,50,3,52,5,54,7,56,64] * 2
        else:
            self.transform_idx = [0,1,2,3,4,5,6,7,8,16] * 2

        self.flip_inside_idx = [False,False,
                                True,False,
                                True,False,
                                True,False,
                                True,True] * 2

        
            

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


if __name__ == '__main__':
    F = Frame()
    F.pack()
    F.mainloop()
