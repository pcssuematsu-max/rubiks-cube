import numpy as np
import random
from collections import OrderedDict,Counter
import math
import cProfile
import tkinter as Tk
import os
from functools import reduce
import sys
import threading
import pickle

sys.path.append('/Users/uematsukousuke/anaconda3/lib/python3.7/site-packages')
from heapdict import heapdict

np.set_printoptions(suppress=True)


perfect_val = 1.0e+8






class Frame(Tk.Frame):
    def __init__(self,cube_size = 7):
        self.cube_size = cube_size
        Tk.Frame.__init__(self,None)
        self.master.title('Rubiks')



        self.cube = Rubiks_3()

        #[0,1,4,6,17,2,7,10,22,33]        

        SX = [

              self.cube.myperms['T-Perm-A000'] + ("F+ ","R+ ","U+ ","R- ","U- ","F- "),
              self.cube.myperms['Y-Perm-A000'] + ("F+ ","R+ ","U+ ","R- ","U- ","F- "),
              self.cube.myperms['EF-Q000'],
              self.cube.myperms['EF-A000'],
              self.cube.myperms['EF-B000'],
              self.cube.myperms['q-Perm000'],
              self.cube.myperms['e-Perm000'],
              self.cube.myperms['o-Perm000'] + self.cube.myperms['o-Perm-B000'],
              self.cube.myperms['s-Perm000'] + self.cube.myperms['s-Perm-B000'],
              self.cube.myperms['o-Perm000'] + self.cube.myperms['o-Perm-C000'],
              self.cube.myperms['s-Perm000'] + self.cube.myperms['s-Perm-C000'],
              self.cube.myperms['EP-U00-000'],
              self.cube.myperms['EP-U01-000'],
              self.cube.myperms['T-Perm-A000'],
              self.cube.myperms['Y-Perm-A000'],
              ('R- ', 'F--', 'U- ', 'L- ', 'U+ ', 'L+ ', 'F++', 'R+ '),
              ('F+ ', 'U+ ', 'F+ ', 'R+ ', 'Q+ ', 'R- ', 'F- ', 'R+ ', 'Q- ', 'U- ', 'R- ', 'F- '),
              ('P+ ', 'L+ ', 'R+ ', 'P- ', 'Q+ ', 'P+ ', 'L- ', 'Q- ', 'R- ', 'Q+ ', 'P- ', 'Q- '),
              ('P+ ', 'U+ ', 'L+ ', 'U+ ', 'L- ', 'U--', 'P- ', 'F+ ', 'L+ ', 'F- ', 'U+ ', 'F+ ', 'U- ', 'L- ', 'F- '),
              ]


        S0 = [


              ]
        S1 = [

              ]
        
        S2 = []
        S3 = []
        
        
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

        #self.scramble_mode = ['inside','outside','out-to-in','in-to-out','alternate','2-1-2','double','']
        self.scramble_mode = ['myperms']

        self.stage = 0
        self.stage_num = len(self.scramble_mode)
        self.N = 0
        self.AI_idx = 0
        
        self.perf_num = np.zeros(self.stage_num,dtype = 'i')
        

        self.AIs = [Rubiks_3_AI([512,512,512,512,512,512,512,512],cube_size = cube_size,Activation = 'ReLU',cube = self.cube),
                    Rubiks_3_AI([512,512,512,512,512,512,512,512],cube_size = cube_size,Activation = 'ReLU',cube = self.cube),
                    Rubiks_3_AI([512,512,512,512,512,512,512,512],cube_size = cube_size,Activation = 'ReLU',cube = self.cube),
                    Rubiks_3_AI([512,512,512,512,512,512,512,512],cube_size = cube_size,Activation = 'ReLU',cube = self.cube),
                    Rubiks_3_AI([512,512,512,512,512,512,512,512],cube_size = cube_size,Activation = 'ReLU',cube = self.cube),
                    Rubiks_3_AI([512,512,512,512,512,512,512,512],cube_size = cube_size,Activation = 'ReLU',cube = self.cube),
                    Rubiks_3_AI([512,512,512,512,512,512,512,512],cube_size = cube_size,Activation = 'ReLU',cube = self.cube),
                    Rubiks_3_AI([512,512,512,512,512,512,512,512],cube_size = cube_size,Activation = 'ReLU',cube = self.cube),
                    Rubiks_3_AI([512,512,512,512,512,512,512,512],cube_size = cube_size,Activation = 'ReLU',cube = self.cube),
                    Rubiks_3_AI([512,512,512,512,512,512,512,512],cube_size = cube_size,Activation = 'ReLU',cube = self.cube),]


                   
                
        self.AInum = len(self.AIs)
        self.level = 1 * np.ones((self.AInum,self.stage_num),dtype = 'i')
        self.myval_AI = Rubiks_3_AI([2],cube_size = cube_size)
        self.myval_AI.params['W1'][:] = 0
        self.myval_AI.params['B1'][:] = 0
        self.myval_AI.params['WO_V'][:] = 1        
        L = [((0,0),(2,0)),((0,1),(4,0)),((0,2),(3,0)),((0,3),(5,0)),
             ((2,1),(5,3)),((2,3),(4,1)),((3,1),(4,3)),((3,3),(5,1)),
             ((1,0),(3,2)),((1,1),(4,2)),((1,2),(2,2)),((1,3),(5,2))]


        self.move_keys = self.cube.move_keys


##################################


##        L_AB = AB[self.cube_size]
##
##        surface_num = self.cube_size ** 2
##        for i in range(6):
##            self.myval_AI.params['W1'][64 + i,7 * i * (surface_num) + 4 * (self.cube_size - 1):(7 * i + 1) * (surface_num)] = 1.0
##
##        CL = [((0,0),(2,3),(4,0)),
##              ((0,1),(3,0),(4,3)),
##              ((0,2),(3,3),(5,0)),
##              ((0,3),(2,0),(5,3)),
##              ((1,0),(3,1),(4,2)),
##              ((1,1),(2,2),(4,1)),
##              ((1,2),(2,1),(5,2)),
##              ((1,3),(3,2),(5,1))]
##
##        for i in range(8):
##            for j in CL[i]:
##                self.myval_AI.params['W1'][70 + i,7 * j[0] * (surface_num) + j[1]] = 2.0
##
##        self.myval_AI.params['B1'][70:78] = -4.9
##        self.myval_AI.params['WM_V'] *= 0
##        for i in range(self.myval_AI.params['WM_V'].shape[0]):
##            self.myval_AI.params['WM_V'][i,i] = 1
##        
##
##        self.myval_AI.params['BO_V'][:] = 0.0
##        
##
##        idx = 0
##        for x in L:
##            for i in range(self.cube_size - 2):
##                ab = L_AB[i]
##                self.myval_AI.params['W1'][idx,4 * ab[0] + x[0][1] + 7 * x[0][0] * surface_num] = 2.0
##                self.myval_AI.params['W1'][idx,4 * ab[1] + x[1][1] + 7 * x[1][0] * surface_num] = 2.0
##                self.myval_AI.params['B1'][idx] = -3.0                    
##
##                idx += 1

#################################

        x = self.cube.makedata()
        x[300:900] *= 100
        x[900:1200] *= 10000
        x[1500:1800] *= 10
        x[1800:2400] *= 100
        x[2400:2700] *= 1000
        x[2700:3000] *= 10000
        
        self.myval_AI.params['W1'][0] = x
        self.myval_AI.params['WM_V'] *= 0
        for i in range(self.myval_AI.params['WM_V'].shape[0]):
            self.myval_AI.params['WM_V'][i,i] = 1
            
        self.flip_rotate = ['r120','r240','fUD','rUD','fFB','rFB','fLR','rLR','s','n']
        #self.flip_rotate = ['','','','','','','','','','']


        self.my_scramble = []

        #self.my_scramble = SX
        if False:
            self.AI_idx = -1
        else:
            self.my_scramble = []
            self.AI_idx = 0




        #self.level[0,0] = 8
          




        for i in range(self.AInum):
            if i > 0:
                self.AIs[i].datas = self.AIs[0].datas
            self.AIs[i].cube = self.cube




        self.myval_AI.cube = self.cube
        self.myval_AI.datas = self.AIs[0].datas


        

        

        
        for i in range(self.AInum):
            if i in []:
                self.AIs[i].myperms = {k:self.cube.myperms[k] for k in self.cube.myperms}

            
            self.AIs[i].lr = 5.0e-5
            self.AIs[i].wdlr = 5.0e-4
            self.AIs[i].out_C = 1.0
            self.AIs[i].PV_ratio = 4
            self.AIs[i].skip_search = False
            self.AIs[i].weight_decay = True


            self.AIs[i].params['W1'] *= 0.05
            self.AIs[i].params['WO_P'] -= np.average(self.AIs[i].params['WO_P'],axis = 0)
            self.AIs[i].params['WO_V'][:128] -= 1.0
                        
            


            x = self.cube.makedata()





    

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


 

        if True:
            for x in Datas:
                d = data(x,self.cube.invert_moves(x),None)
                d.succeeded = True
                self.AIs[0].datas.append(d)

        for i in range(self.AInum):
            self.AIs[i].indices = list(range(len(self.AIs[0].datas)))
            

        self.myperms_N = 0
        self.move_buttons = Tk.Frame(self,relief = Tk.RIDGE,bd = 4)

        
        self.reset_button = Tk.Button(self.move_buttons,text = 'Reset',command = self.reset)
        self.reset_button.grid(row = 0, column = 0,columnspan = len(self.move_keys) // 6)
        self.stopper_button = Tk.Button(self.move_buttons,text = 'Not stopping',command = self.stopper)
        self.stopper_button.grid(row = 7,column = 0,columnspan = len(self.move_keys) // 6)
        self.my_solve_button = Tk.Button(self.move_buttons,text = 'start solving',command = self.my_solve)
        self.my_solve_button.grid(row = 8,column = 0,columnspan = len(self.move_keys) // 6)
        self.make_myperm_button = Tk.Button(self.move_buttons,text = 'make myperm',command = self.make_myperm)
        self.make_myperm_button.grid(row = 9,column = 0,columnspan = len(self.move_keys) // 6)


        self.SV = State_viewer(self)
        self.SV.grid(row = 0,column = 0,columnspan = 2)
        self.MV = Move_viewer(self)
        self.MV.grid(row = 0,column = 2,rowspan = 2)

        self.PV = Prob_viewer(self,self.move_keys)
        self.PV.grid(row = 1,column = 1)
        

        
        for i in range(len(self.move_keys)):
            B = Move_Button(self.move_buttons,self.move_keys[i],self.cube)
            B.grid(row = i % 6 + 1,column = i // 6)

        self.move_buttons.grid(row = 1,column = 0)        

        self.stop = False

        self.last_perms = {}

        self.move_lis = []
        self.key_lis = []
        self.val_lis = []
        self.val_lis2 = []
        self.s = None
        self.phase = -1
        self.search_TF = False
        self.end_solve = False


        self.add_idx = [[],[],[],[],[],[],[],[],[],[]]
        self.add_indices = [0] + list(reduce(lambda x,y:x + y,self.add_idx))

        self.transform_idx = [0,1,4,6,17,2,7,10,22,33]

        self.learn_idx = 0
        
    def set_level(self,N):
        #self.load_lists()
        self.loadparams_all()
        self.level[:] = N
        

    def sum_and_var(self,i):
        for k in self.AIs[i].params.keys():
            print(i,k)
            print(np.sum(self.AIs[i].params[k]),np.var(self.AIs[i].params[k]))
            print(np.max(self.AIs[i].params[k]),np.min(self.AIs[i].params[k]))                    
            print(np.sum(self.AIs[i].v[k]))


    def svd_W1(self,i):
        Z = np.linalg.svd(F.AIs[i].params['W1'])
        for j in range(10):
            O = np.argsort(Z[2][j])
            print(Z[1][j],np.where(Z[0][:,j] > 0)[0].shape[0],np.where(Z[0][:,j] < 0)[0].shape[0])
            print(O[:20])
            print(O[-20:])


    def save_lists(self):
        os.chdir('/Users/uematsukousuke/Documents')
        f = open('Datas.binaryfile','wb')
        pickle.dump(self.AIs[0].datas,f)
        f.close()
        os.chdir('/Users/uematsukousuke/Documents/Python/Megaminx')

    def load_lists(self):
        os.chdir('/Users/uematsukousuke/Documents')
        f = open('Datas.binaryfile','rb')
        L = pickle.load(f)
        f.close()
        os.chdir('/Users/uematsukousuke/Documents/Python/Megaminx')

        for i in range(self.AInum):
            self.AIs[i].datas = L
            self.AIs[i].indices = list(range(len(L)))
        

        


        
    
    def saveparams_all(self):
        self.save_lists()
        for i in range(self.AInum):
            self.saveparams(i)

    def loadparams_all(self):
        for i in range(self.AInum):
            self.loadparams(i)

    def max_val(self,T0 = (),T1 = ()):
        keys = self.search_myperms(T0,T1)
        X = np.zeros((self.cube.ips,len(keys)),dtype = 'f')
        X2 = np.zeros((self.cube.ips,1),dtype = 'f')
        i = 0
        for k in keys:
            self.cube.reset()
            for m in self.cube.invert_moves(self.cube.myperms[k]):
                self.cube.make_move(m)
                x = self.cube.makedata()
                X[:,i] = x

            i += 1


        for i in range(self.AInum):
            V = self.AIs[i].predict(X,policy = False,value = True).reshape(-1)
            O = np.argsort(V)

            
            top_arg = O[-10:]
            top_key = []
            for o in top_arg:
                top_key.append(keys[o])
                
            
            top_val = V[top_arg]

            print(i,top_key,self.AIs[i].perfect_val - top_val)

            top_arg = O[:10]
            top_key = []
            for o in top_arg:
                top_key.append(keys[o])
            top_val = V[top_arg]

            print(i,top_key,self.AIs[i].perfect_val - top_val)
            V = self.AIs[i].predict(X2,policy = False,value = True).reshape(-1)
                      

        

        self.cube.reset()

    def lpk(self):
        for key in sorted(self.last_perms.keys()):
            X = [len(x) for x in self.last_perms[key]]
            if key + '000' in self.cube.myperms:
                M = min(X)
                N = len(self.cube.myperms[key + '000'])
                if M < N:
                    print(key,M,N,set(X),'<----------------')
                else:
                    print(key,M,N,set(X))
            else:
                print(key,min(X),set(X))
                

    def lp_show(self,key,M = None):
        X = [len(x) for x in self.last_perms[key]]
        if M == None:
            M = min(X)
        for x in self.last_perms[key]:
            if len(x) == M:
                print(x)

    



    def search_myperms(self,T0,T1):
        if T1 != ():
            return [k for k in self.cube.myperms if self.cube.myperms[k][-len(T1):] == T1 and self.cube.myperms[k][:len(T0)] == T0]
        else:
            return [k for k in self.cube.myperms if self.cube.myperms[k][:len(T0)] == T0]

    def normalize(self,i):
        for key in self.AIs[i].params.keys():
            if key[0] == 'W':
                V = np.sqrt(np.var(self.AIs[i].params[key],axis = 1).reshape(-1,1)) * np.sqrt(self.AIs[i].params[key].shape[1])
                self.AIs[i].params[key] /= V
                self.AIs[i].params['B' + key[1:]] /= V.reshape(-1)
            elif key[:3] == 'BNg':
                self.AIs[i].params[key][:] = 1
            elif key[:3] == 'BNb':
                self.AIs[i].params[key][:] = 0


        F.AIs[i].set_perfect_val()
                
                    
    def re_activate(self,i):
        for key in self.AIs[i].params.keys():
            if key[0] == 'W' and key not in ['WO_P','WO_V']:
                W = np.where(np.abs(self.AIs[i].v['B' + key[1:]]) == 0)[0]
                print(key,W)
                print(key,self.AIs[i].params['B' + key[1:]][W])
                self.AIs[i].params['B' + key[1:]][W] = 0.1
                if key[1] != '1':
                    for j in range(W.shape[0]):
                        self.AIs[i].params[key][W[j],W[j] % self.AIs[i].params[key].shape[1]] = -1.0
                        self.AIs[i].params[key][W[j],(W[j] + 1) % self.AIs[i].params[key].shape[1]] = -1.0


    def set_color(self,S):
        self.SV.set_color(S)
    
    def reset(self):
        self.cube.reset()
        self.set_color(self.cube.state)

    def make_myperm(self):
        Frame = Tk.Toplevel(self)
        Frame.title('make myperm')
        E = Tk.Entry(master = Frame,width = 20)
        E.grid(row = 0,column = 0)
        B = make_myperm_OK(Frame,self,E)
        B.grid(row = 1,column = 0)

    def my_solve(self):
        succeeded = False
        if not self.stop:
            self.my_solve_button.configure(state = Tk.DISABLED)
            if self.AI_idx != -1:
                AI = self.AIs[self.AI_idx]
            else:
                AI = self.myval_AI
            
            if self.phase == -1:
                self.cube.reset()

                if self.AI_idx != -1:
                    if self.N >= 10:
                        scramble_num = self.level[self.AI_idx,self.stage]
                    else:
                        scramble_num = self.level[self.AI_idx,self.stage]

                    add_moves = (self.N % 20 < 10)
                    while self.cube.is_perfect():
                        self.cube.reset()
                        if self.flip_rotate[self.AI_idx][0] == 'r':
                            self.s = self.cube.scramble(scramble_num,difficult_mode = True,scramble_mode = self.scramble_mode[self.stage],rotate = self.flip_rotate[self.AI_idx][1:],add_moves = add_moves)
                        elif self.flip_rotate[self.AI_idx][0] == 'f':
                            self.s = self.cube.scramble(scramble_num,difficult_mode = True,scramble_mode = self.scramble_mode[self.stage],flip = self.flip_rotate[self.AI_idx][1:],add_moves = add_moves)

                        elif self.flip_rotate[self.AI_idx][0] == 's':
                            self.s = self.cube.scramble(scramble_num,difficult_mode = True,scramble_mode = self.scramble_mode[self.stage],swap = True,add_moves = add_moves)
                        else:
                            self.s = self.cube.scramble(scramble_num,difficult_mode = True,scramble_mode = self.scramble_mode[self.stage],add_moves = add_moves)
                else:
                    self.cube.reset()
                    self.s = self.cube.scramble(0,Move = self.my_scramble[self.N])
                self.phase += 1
                if self.AI_idx == -1:
                    self.search_TF = False
                else:
                    self.search_TF = True
                self.move_lis = []
                self.key_lis = []
                self.val_lis = []
                self.val_lis2 = []
                self.end_solve = False
                
                

            else:
                if self.search_TF:
                    current_state = self.cube.state.copy()
                    if len(self.val_lis) == 0:
                        x = self.cube.makedata().reshape(-1,1)
                        s = self.cube.state.reshape(1,-1)
                        if AI.myval:
                            V = AI.myval_predict(x,s).reshape(-1)
                        else:
                            V = AI.predict(x,policy = False,value = True).reshape(-1)

                        self.move_lis.append(tuple([]))
                        self.key_lis.append('')
                        self.val_lis.append(V[0])
                        self.val_lis2.append([])

                    
                    #T = AI.search(AI.search_num,0,(),(),Counter = np.zeros(2,dtype = 'i'))
                    T = AI.search2(AI.search_num)
                    VL2 = [x - self.AIs[self.AI_idx].perfect_val for x in T[3]]
                    reduced_lis = self.cube.reduce(T[1])
                    simplified_lis = self.cube.simplify(T[1])
                    #print(len(reduced_lis[0]),len(T[1]))
                    
                    self.move_lis.append(reduced_lis[0])
                    self.key_lis.append(str(T[5][0]) + '/' + str(T[5][1]))
                    self.val_lis.append(T[2])
                    self.val_lis2.append([VL2[0]] + [VL2[i + 1] for i in reduced_lis[1]])
                    if T[0]:
                        succeeded = True
                        x = self.cube.makedata().reshape(-1,1)
                        self.end_solve = True
                        perfect_key = ''
                        
                        s = ''.join(self.cube.state)
                        if s not in F.myperms_col:
                            for key in ['A','B']:
                                v = self.cube.total_val[key] - (self.cube.group_val[key] @ x)[0][0]
                                if v > 0.01:
                                    perfect_key += key + str(int(round(v,0)))
                        else:
                            perfect_key = F.myperms_col[s][:-3]
                            simplified_lis = self.cube.transform(simplified_lis,int(F.myperms_col[s][-3:]))
                            #print(perfect_key)

                        
                        
                    for m in reduced_lis[0]:
                        self.cube.make_move(m)

                    if (self.cube.state == current_state).all():
                        #if len(AI.myperms) == 0:
                        if False:
                            self.end_solve = True
                            for x in self.move_lis:
                                self.s += tuple(x)
                            self.my_scramble.append(self.s)
                            
                        else:
                            self.search_TF = False
                            #if AI.myval:
                            if True:
                                for x in self.move_lis:
                                    self.s += tuple(x)

                                self.move_lis = []
                                self.key_lis = []
                                self.val_lis = []
                                self.val_lis2 = []
                    
                else:
                    if True:
                        AI = self.myval_AI
                
                    if len(self.val_lis) == 0:
                        x = self.cube.makedata().reshape(-1,1)
                        s = self.cube.state.reshape(1,-1)
                        if AI.myval:
                            V = AI.myval_predict(x,s).reshape(-1)
                        else:
                            V = AI.predict(x,policy = False,value = True).reshape(-1)

                        self.move_lis.append(tuple([]))
                        self.key_lis.append('')
                        self.val_lis.append(V[0])
                        self.val_lis2.append([])

                    s = ''.join(self.cube.state)
                    if s in self.myperms_col:
                        key = self.myperms_col[s]
                        val = perfect_val
                        for m in self.cube.myperms[key]:
                            self.cube.make_move(m)

                        self.val_lis.append(val)
                        self.val_lis2.append([])
                        self.key_lis.append(key)
                        self.move_lis.append(self.cube.myperms[key])
                        succeeded = True

                        self.end_solve = True
                        

                        
                    else:

                        x = self.cube.makedata().reshape(-1,1)
                        top_group = 'A'
                        top_val = 0
                        
                        for key in ['A','B']:
                            v = self.cube.total_val[key] - (self.cube.group_val[key] @ x)[0][0]
                            if v > 0.001 and v > top_val:
                                top_val = v
                                top_group = key

                        


                        myperms_key = []
                        top_key = (0,'O')
                        

                        for i in self.cube.myperms_order[top_group]:
                            x = self.cube.num_to_piece[i]
                            c = reduce(lambda z,w:z+w,[self.cube.state[n] for n in x])
                            if c != self.cube.default_color[x]:
                                top_key = (x,c)
                                myperms_key = self.cube.myperms_dict[top_key]
                                                            
                                break
        
                        if False:
                            EvalNum = 96
                        else:
                            EvalNum = len(myperms_key)

                        
                        #X = np.empty((36 * self.cube.surface_num,EvalNum),dtype = 'f')
                        X = np.empty((self.cube.ips,EvalNum),dtype = 'f')
                        S = np.empty((EvalNum,12 * self.cube.surface_num),dtype = str)

                        Len = len(myperms_key)
                        idx = 0
                        TF = False
                        perfect_key = ''
                        Base = 0
                        Continue = False
                        for key in myperms_key:
                            for m in AI.myperms[key]:
                                self.cube.make_move(m)

                            if self.cube.is_perfect():
                                TF = True
                                perfect_key = key
                                
                            
                            
                            x = self.cube.makedata()
                            X[:,idx] = x
                            S[idx,:] = self.cube.state
                        


                            for m in self.cube.invert_moves(AI.myperms[key]):
                                self.cube.make_move(m)

                            idx += 1
                            if TF:
                                break

                            if idx == EvalNum or Base + idx == Len:
                                idx = 0
                                if AI.myval:
                                    V = AI.myval_predict(X,S).reshape(-1)
                                else:
                                    V = AI.predict(X,policy = False,value = True).reshape(-1)

                                val = np.max(V)
                                if len(self.val_lis) == 0 or self.val_lis[-1] + 0.0001 < val:
                                    args = np.where(V >= val - 0.01)[0]
                                    new_keys = []
                                    new_moves = []
                                    #X = np.empty((36 * self.cube.surface_num,0),dtype = 'f')
                                    X = np.empty((self.cube.ips,0),dtype = 'f')
                                    S = np.empty((0,12 * self.cube.surface_num),dtype = str)
                                    for i in args:
                                        key = myperms_key[i + Base]
                                        j = 0
                                        for m in AI.myperms[key]:
                                            j += 1
                                            self.cube.make_move(m)
                                            x = self.cube.makedata()
                                            X = np.c_[X,x.reshape(-1,1)]
                                            S = np.r_[S,self.cube.state.reshape(1,-1)]
                                            new_keys.append(key + '(' + str(j) + ')')
                                            new_moves.append(AI.myperms[key][:j])


                                        for m in self.cube.invert_moves(AI.myperms[key]):
                                            self.cube.make_move(m)

                                    if AI.myval:
                                        V = AI.myval_predict(X,S).reshape(-1)
                                    else:
                                        V = AI.predict(X,policy = False,value = True).reshape(-1)
                                    
                                    toparg = np.argmax(V)
                                    val = V[toparg]

                                    
                                    
                                    best_key = new_keys[toparg]
                                    best_move = new_moves[toparg]

                                    
##                                    toparg = np.argmax(V) + Base
##                                    best_key = myperms_key[toparg]
##                                    best_move = self.cube.myperms[best_key]

                                    
                                    
                                    self.key_lis.append(best_key)
                                    self.move_lis.append(best_move)
                                    self.val_lis.append(val)
                                    self.val_lis2.append([])
                                    for m in best_move:
                                        self.cube.make_move(m)
                                    Continue = True
                                    break



                                else:
                                    Base += EvalNum
                                    
                                


                        if TF:
                            succeeded = True
                            self.val_lis.append(perfect_val)
                            self.key_lis.append(perfect_key)
                            self.val_lis2.append([])
                            self.move_lis.append(AI.myperms[perfect_key])
                            self.end_solve = True
                        elif not Continue:
                            print (top_key)
                            self.end_solve = True
                            if self.AI_idx != -1:
                                for x in self.move_lis:
                                    self.s += tuple(x)
                                self.my_scramble.append(self.s)



                self.phase += 1
            #self.move_lis = [self.cube.reduce(x) for x in self.move_lis]

            
            x = self.cube.makedata().reshape(-1,1)
            W = softmax(AI.predict(x,policy = True,value = False).reshape(-1))
            self.PV.put_val(W)
            

            
            self.MV.set_str(self.s,self.move_lis,self.key_lis,self.val_lis,self.val_lis2,self.perf_num[self.stage],self.N)
            self.set_color(AI.cube.state)
            if self.end_solve:
                if self.phase > 0 and succeeded:
                    if self.search_TF:
                        self.perf_num[self.stage] += 1


                    idx = 0
                    z = ()
                    v = self.val_lis[0]
                    v_last = self.val_lis[-1]
                    for x in self.move_lis:
                        z += x
                        #z = self.cube.simplify(z)
                        
                        #if  and (self.val_lis[idx] - v > 0 or self.val_lis[idx] > v_last - 1):
                        if len(z) > 0:
                            R = np.zeros(len(z),dtype = 'f')
                            R[-1] = 10
                            Datas = self.cube.make_transformations(self.s,z)
                        



                            L = len(AI.datas)
    
                            add_num = len(self.add_indices)
                            for i in range(add_num):
                                d = data(Datas[0][self.add_indices[i]],Datas[1][self.add_indices[i]],R)
                                d.succeeded = True
                                AI.datas.append(d)
                        
                            k = 0     
                            for i in range(self.AInum):
                                if i in [3,5,7,8,1,9,0,2,4,6]:
                                    self.AIs[i].indices.append(L)
                                for j in range(len(self.add_idx[i])):
                                    k += 1
                                    self.AIs[i].indices.append(L + k)
                                


##                            for k in range(self.AInum):
##                                self.AIs[k].indices += [L + i for i in range(add_num)]


                            self.s += z


                            z = ()
                            v = self.val_lis[idx]

                        idx += 1

                            

                                           
                    Len = len(self.move_lis[-1])
                    if self.search_TF:
                        if len(self.move_lis) >= 2:
                            T = tuple(simplified_lis)
                            if T not in self.myperms_vals:
                                print(perfect_key,len(T))
                                if perfect_key not in self.last_perms:
                                    self.last_perms[perfect_key] = set([])
                                self.last_perms[perfect_key].add(T)

                        L = len(self.move_lis)
                        max_level = max(0,int(- self.val_lis2[1][0] / 5))
                        #max_level = L - 1
                        if max_level >= len(self.cube.my_scrambles2):
                            for i in range(max_level - len(self.cube.my_scrambles2) + 1):
                                self.cube.create_new_set()

                        for i in range(1,L):
                            T = self.cube.invert_moves(self.move_lis[i])

                            level = max(0,int(- self.val_lis2[i][0] / 5))                           
                            #if - self.val_lis2[i][0] < 5:
                            #    level = 0
                            #else:
                            #    level = L - i
                            
                            self.cube.my_scrambles2[level][T[-1]].add(T)
                        
                    
                self.N += 1
                #self.AIs[self.AI_idx].skip_search = not self.AIs[self.AI_idx].skip_search
                self.AI_idx += 1
                self.AI_idx %= self.AInum
                #if self.N == 200:
                if self.N == 210 or (self.N % 10 == 0 and self.N < 190 and self.perf_num[0] < (self.N / 20) ** 2 * 2):
                    self.N = 0
                    self.stage += 1
                    if self.stage == self.stage_num:
                        self.stage = 0

                        print(self.perf_num)
                        if np.sum(self.perf_num) >= 190:
                            self.level[:] += 1


                        print(self.level[:])
                        self.my_scramble = []
                        self.perf_num[:] = 0
                            

                            
                        #for i in range(self.AInum):
                        self.learn()
##                        while i < self.AInum:
##                            if len(self.AIs[i].indices) >= 2000:
##                                X = self.AIs[i].learn()
##                                err = X[0]
##                                print(X)
##                                if i in []:
##                                    self.AIs[i].indices = list(range(len(self.AIs[i].datas)))
##
##                                self.AIs[i].set_perfect_val()
##
##                            i += 1

                                



                self.phase = -1

            if self.cube.is_perfect():
                self.after(10,self.my_solve)
            else:
                self.after(10,self.my_solve)


    def learn(self):
        self.AIlearn(list(range(10)))
        #t1 = threading.Thread(target = self.AIlearn,args = ([0,2,4,6,8],))
        #t2 = threading.Thread(target = self.AIlearn,args = ([1,3,5,7,9],))

        #t1.start()
        #t2.start()

        #t1.join()
        #t2.join()
        


    def AIlearn(self,Indices):
        for i in Indices:
            if len(self.AIs[i].indices) >= 0:
                X = self.AIs[i].learn(transformation = self.transform_idx[i])
                err = X[0]
                print(i,X)
                self.AIs[i].set_perfect_val()
    


    def stopper(self):
        self.stop = not self.stop
        if self.stop:
            self.stopper_button.configure(text = 'Stopping')
            self.my_solve_button.configure(state = Tk.NORMAL)
        else:
            self.stopper_button.configure(text = 'Not stopping')

                    
    def loadparams(self,N):
        Dir = os.getcwd()
        os.chdir('/Users/uematsukousuke/Documents')
        os.chdir('./AIdatas_M' + str(N))
        for key in self.AIs[N].params.keys():
            self.AIs[N].params[key][:] = np.load(key + '.npy')
            self.AIs[N].v[key][:] = np.load(key + '_v.npy')
            self.AIs[N].h[key][:] = np.load(key + '_h.npy')

        os.chdir(Dir)
        self.AIs[N].set_perfect_val()

    def saveparams(self,N):
        Dir = os.getcwd()
        os.chdir('/Users/uematsukousuke/Documents')
        os.chdir('./AIdatas_M' + str(N))
        for key in self.AIs[N].params.keys():
            np.save(key + '.npy',self.AIs[N].params[key])
            np.save(key + '_v.npy',self.AIs[N].v[key])
            np.save(key + '_h.npy',self.AIs[N].h[key])

        os.chdir(Dir)            



    def myfunc(self):
        for key in F.cube.my_scrambles2[0].keys():
            N = min(21,len(F.cube.my_scrambles2))
            V = np.zeros(N,dtype = 'i')
            for i in range(N):
                V[i] = len(F.cube.my_scrambles2[i][key])

            print(key,V)

    def myfunc2(self,N = 0):
        for k in self.cube.my_scrambles2[N].keys():
            for x in self.cube.my_scrambles2[N][k]:
                print(x[0],x[-1])

            
class make_myperm_OK(Tk.Button):
    def __init__(self,master,frame,entry):
        Tk.Button.__init__(self,master,text = 'OK',command = self.make_myperm)
        self.frame = frame
        self.entry = entry
        self.master = master

    def make_myperm(self):
        text = self.entry.get()
        if text in self.frame.myperms_keys:
            for m in self.frame.cube.myperms[text]:
                self.frame.cube.make_move(m)

            self.frame.set_color(self.frame.cube.state)
            
        self.master.destroy()




class State_viewer(Tk.Canvas):
    def __init__(self,master):
        self.coordinate_corner = [(0,-17),(16,-5),(10,14),(-10,14),(-16,-5)]
        self.coordinate_edge = [(0,14),(-13,4.5),(-8,-12),(8,-12),(13,4.5)]
        self.corner_r = 6
        self.edge_r = 4
        self.center_r = 10
        
        D = 125
        self.center = [(0,0),(0,42.5),(-40,12.5),(-25,-35),(25,-35),(40,12.5),(D,-42.5),(D+40,-12.5),(D+25,35),(D-25,35),(D-40,-12.5),(D,0)]
        self.center = [(x[0] + 70,x[1] + 100) for x in self.center]
        self.zero_position = [0,0,1,2,3,4,0,1,2,3,4,0]
        self.PM = [1,-1,-1,-1,-1,-1,1,1,1,1,1,-1]
        self.color = {'U':"#FFFFFF",
                      'F':"#7F0000",
                      'L':"#007F00",
                      'P':"#5F00BF",
                      'Q':"#BFBF00",
                      'R':"#0000BF",
                      'B':"#FF7F00",
                      'X':"#007FFF",
                      'G':"#FFDF7F",
                      'H':"#FF007F",
                      'Y':"#7FFF00",
                      'D':"#7F7F7F"}

        self.bd_color = self.color
        Tk.Canvas.__init__(self,master,relief = Tk.RAISED , bd = 4,width = 525,height = 400 ,bg = '#BFBFBF')
        i = 0

        for c in self.color:
            self.create_oval(2 * (self.center[i][0] - self.center_r),
                                 2 * (self.center[i][1] - self.center_r),
                                 2 * (self.center[i][0] + self.center_r),
                                 2 * (self.center[i][1] + self.center_r),
                    fill = self.color[c],outline = self.bd_color[c],tags = 'centers')
            if i in [1,2,3,4,5]:
                fill_color = "#FFFFFF"
            else:
                fill_color = "#000000"
            self.create_text(2*self.center[i][0] ,2*self.center[i][1],text = c,font = ('Comic Sans MS',20,'bold'),fill = fill_color,tags = 'texts')
            i += 1

        
        



        

    def set_color(self,S):
        self.delete('circles')

        for i in range(120):
            if i % 10 < 5:
                self.create_oval(2 * (self.center[i // 10][0] + self.PM[i // 10]*self.coordinate_corner[(i+self.zero_position[i // 10]) % 5][0] - self.corner_r),
                                 2 * (self.center[i // 10][1] + self.PM[i // 10]*self.coordinate_corner[(i+self.zero_position[i // 10]) % 5][1] - self.corner_r),
                                 2 * (self.center[i // 10][0] + self.PM[i // 10]*self.coordinate_corner[(i+self.zero_position[i // 10]) % 5][0] + self.corner_r),
                                 2 * (self.center[i // 10][1] + self.PM[i // 10]*self.coordinate_corner[(i+self.zero_position[i // 10]) % 5][1] + self.corner_r),
                    fill = self.color[S[i]],outline = self.bd_color[S[i]],tags = 'circles')
            else:
                self.create_oval(2 * (self.center[i // 10][0] + self.PM[i // 10]*self.coordinate_edge[(i+self.zero_position[i // 10]) % 5][0] - self.edge_r),
                                 2 * (self.center[i // 10][1] + self.PM[i // 10]*self.coordinate_edge[(i+self.zero_position[i // 10]) % 5][1] - self.edge_r),
                                 2 * (self.center[i // 10][0] + self.PM[i // 10]*self.coordinate_edge[(i+self.zero_position[i // 10]) % 5][0] + self.edge_r),
                                 2 * (self.center[i // 10][1] + self.PM[i // 10]*self.coordinate_edge[(i+self.zero_position[i // 10]) % 5][1] + self.edge_r),
                    fill = self.color[S[i]],outline = self.bd_color[S[i]],tags = 'circles')                

        
                                
                                                                                        
        
class Move_viewer(Tk.Canvas):
    def __init__(self,master):
        self.r_size = 800
        self.c_size = 700
        self.text_color = '#FFFFFF'
        self.font = 'Comic Sans MS'
        self.font_size = 14
        self.words_in_a_row = 16
        self.c_dist = 28
        self.r_dist = 16
        Tk.Canvas.__init__(self,master,relief = Tk.RAISED, bd = 4,width = self.c_size,height = self.r_size,bg = '#000000')
        

    def set_str(self,S,M,K,V,V2,scramble_num,N):
        self.delete('text')
        i = 0
        for x in S:
            self.create_text(100 + self.c_dist * (i % self.words_in_a_row),20 + self.r_dist * (i // self.words_in_a_row),text = x,tags = 'text',fill = self.text_color,font = (self.font,self.font_size,'bold'))
            i += 1

            
        self.create_text(50,20,text = str(scramble_num) + '/' + str(N),tags = 'text',fill = self.text_color,font = (self.font,self.font_size,'bold'))
        #self.create_text(40,20,text = N,tags = 'text',fill = self.text_color,font = (self.font,self.font_size,'bold'))
        r = max((len(S) - 1) // self.words_in_a_row - 4,0)
        for i in range(len(M)):
            self.create_text(60,100 + self.r_dist * r,text = K[i],tags = 'text',fill = self.text_color,font = (self.font,self.font_size,'bold'))
            self.create_text(650,100 + self.r_dist * r,text = round(V[i],4),tags = 'text',fill = self.text_color,font = (self.font,self.font_size,'bold'))
            j = 0
            for x in M[i]:
                if len(V2[i]) != 0:
                    color = set_color2(V2[i][j + 1])
                else:
                    color = self.text_color
                self.create_text(150 + self.c_dist * (j % self.words_in_a_row),100 + self.r_dist * (r + j // self.words_in_a_row),text = x,tags = 'text',fill = color,font = (self.font,self.font_size,'bold'))
                j += 1
            if len(M[i]) == 0:
                r += 1
            else:
                r += (len(M[i]) - 1) // self.words_in_a_row + 1  


class Prob_viewer(Tk.Canvas):
    def __init__(self,master,move_keys):
        self.r_size = 320
        self.c_size = 100
        self.font = 'Comic Sans MS'
        Tk.Canvas.__init__(self,master,relief = Tk.RAISED, bd = 4,width = self.c_size,height = self.r_size,bg = '#000000')
        self.move_keys = move_keys
        self.move_len = len(self.move_keys)
        i = 0
        for m in self.move_keys:
            
            i += 1


    def put_val(self,W):
        self.delete('text')
        self.delete('move')
        O = np.argsort(-W)
        W = np.round(W * 100,4)


        for i in range(min(O.shape[0],20)):
            self.create_text(20,20 + 14 * i,font = (self.font,12,'bold'),text = self.move_keys[O[i]]+ ':',tags = 'move',fill = '#FFFFFF')
            self.create_text(70,20 + 14 * i,font = (self.font,12,'bold'),text = str(W[O[i]]) + '%',tags = 'text',fill = set_color(W[O[i]]))


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

DeepBlue = '#00005F'
Blue = '#0000BF'

DeepPurple = '#2F005F'
Purple = '#5F00BF'

DeepMagenta = '#5F002F'
Magenta = '#BF005F'

DeepSilver = '#3F3F3F'
Silver = '#7F7F7F'

LightSilver = '#BFBFBF'

White = '#FFFFFF'







def set_color(x):
    if x > 90:
        return DeepRed
    elif x > 70:
        return DeepYellow
    elif x > 50:
        return DeepGreen
    elif x > 30:
        return DeepBlue
    elif x > 10:
        return DeepPurple
    elif x > 7:
        return Yellow
    elif x > 5:
        return Green
    elif x > 3:
        return Blue
    elif x > 1:
        return Purple
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
 


class Move_Button(Tk.Button):
    def __init__(self,master,m,cube):
        self.m = m
        Tk.Button.__init__(self,master,text = m,command = self.make_move)
        self.cube = cube

    def make_move(self):
        self.cube.make_move(self.m)
        self.master.master.SV.set_color(self.cube.state)



class Square_1:
    def __init__(self):
        self.state = np.array([['B','C','A','B','C','A','B','C','A','B','C','A'],
                               ['R','B','B','B','O','O','O','G','G','G','R','R'],
                               ['R','B','B','B','O','O','O','G','G','G','R','R'],
                               ['E','F','D','E','F','D','E','F','D','E','F','D']],dtyep = str)

        self.state_0 = self.state.copy()
        self.Mid = True

        self.slash_test = {('B','C'),('E','F')}

        


    def make_move(self,m):
        New_S = np.zeros((4,12),dtype = str)

        if m[0] == 'U':
            N = int(m[1:])
            New_S[2] = self.state[2]
            New_S[3] = self.state[3]
            New_S[0:2,N:] = self.state[0:2,:-N]
            New_S[0:2,-N:] = self.state[0:2,:N]
            self.state = New_S

        elif m[0] == 'D':
            N = 12 - int(m[1:])
            New_S[0] = self.state[0]
            New_S[1] = self.state[1]
            New_S[2:4,N:] = self.state[2:4,:-N]
            New_S[2:4,-N:] = self.state[2:4,:N]
            self.state = New_S

        else:
            if self.is_slashable():
                New_S[:,6:] = self.state[:,6:]
                New_S[0,:6] = self.state[3,5:-1:-1]
                New_S[1,:6] = self.state[2,5:-1:-1]
                New_S[2,:6] = self.state[1,5:-1:-1]
                New_S[3,:6] = self.state[0,5:-1:-1]
                self.state = New_S
                

                
                
                


    def is_slashable(self):
        if (self.state[0,11],self.state[0,0]) in self.slash_test:
            return False
        elif (self.state[0,5],self.state[0,6]) in self.slash_test:
            return False
        elif (self.state[3,11],self.state[3,0]) in self.slash_test:
            return False
        elif (self.state[3,5],self.state[3,6]) in self.slash_test:
            return False
        else:
            return True

            


    
        


class Rubiks_3:
    def __init__(self,S = ''):        
        self.color_to_num = {'U':0,'F':1,'L':2,'P':3,'Q':4,'R':5,'B':6,'X':7,'G':8,'H':9,'Y':10,'D':11}
        self.colors = ['U','F','L','P','Q','R','B','X','G','H','Y','D']
        
        self.move = {}

        self.opposite = {}


        self.inverse = {"+ ":"- ","- ":"+ ","++":"--","--":"++"}

        self.mult = {("+ ","+ "):"++",("+ ","++"):"--",("+ ","--"):"- ",("+ ","- "):0,
                     ("++","+ "):"--",("++","++"):"- ",("++","--"):0,("++","- "):"+ ",
                     ("--","+ "):"- ",("--","++"):0,("--","--"):"+ ",("--","- "):"++",
                     ("- ","+ "):0,("- ","++"):"+ ",("- ","--"):"++",("- ","- "):"--"}
                     

        self.flip = {}
        self.flip['UD'] = {"U":"U","F":"F","L":"R","P":"Q","Q":"P","R":"L","B":"B","Y":"X","H":"G","G":"H","X":"Y","D":"D"}


        self.rotate = {}
        self.rotate['UD'] = {"U":"U","F":"L","L":"P","P":"Q","Q":"R","R":"F","B":"Y","Y":"H","H":"G","G":"X","X":"B","D":"D"}
        
        self.rotate['FB'] = {"U":"R","R":"H","H":"G","G":"L","L":"U","D":"X","X":"P","P":"Q","Q":"Y","Y":"D","F":"F","B":"B"}
        
        self.rotate['DU'] = {}
        self.rotate['BF'] = {}
        for key in self.colors:
            self.rotate['DU'][self.rotate['UD'][key]] = key
            self.rotate['BF'][self.rotate['FB'][key]] = key
        


        self.transformation_keys = [(), ('R1',), ('F',), ('R2',), ('r1',), ('r2',), ('R1', 'R1'), ('R1', 'F'), ('R1', 'R2'), ('R1', 'r2'),
                                    ('F', 'R1'),('F', 'R2'), ('F', 'r2'), ('R2', 'R1'), ('R2', 'R2'), ('R2', 'r1'), ('r1', 'R2'),
                                    ('r1', 'r1'), ('r1', 'r2'), ('r2', 'R1'),('r2', 'r1'), ('r2', 'r2'), ('R1', 'R1', 'F'),
                                    ('R1', 'R1', 'R2'), ('R1', 'R1', 'r2'), ('R1', 'F', 'R2'), ('R1', 'F', 'r2'),('R1', 'R2', 'R1'),
                                    ('R1', 'R2', 'R2'), ('R1', 'R2', 'r1'), ('R1', 'r2', 'R1'), ('R1', 'r2', 'r1'), ('R1', 'r2', 'r2'),
         ('F', 'R1', 'R1'), ('F', 'R1', 'R2'), ('F', 'R1', 'r2'), ('F', 'R2', 'R1'), ('F', 'R2', 'R2'), ('F', 'R2', 'r1'),
         ('F', 'r2', 'R1'), ('F', 'r2', 'r1'), ('F', 'r2', 'r2'), ('R2', 'R1', 'R1'), ('R2', 'R1', 'r2'), ('R2', 'R2', 'R1'),
         ('R2', 'R2', 'r1'), ('R2', 'r1', 'R2'), ('R2', 'r1', 'r1'), ('R2', 'r1', 'r2'), ('r1', 'R2', 'R2'), ('r1', 'R2', 'r1'),
         ('r1', 'r1', 'R2'), ('r2', 'R1', 'R1'), ('r2', 'R1', 'r2'), ('r2', 'r2', 'R1'), ('R1', 'R1', 'F', 'R2'), ('R1', 'R1', 'F', 'r2'),
         ('R1', 'R1', 'R2', 'R2'), ('R1', 'R1', 'r2', 'R1'), ('R1', 'R1', 'r2', 'r2'), ('R1', 'F', 'R2', 'R1'), ('R1', 'F', 'R2', 'R2'),
         ('R1', 'F', 'R2', 'r1'), ('R1', 'F', 'r2', 'R1'), ('R1', 'F', 'r2', 'r1'), ('R1', 'F', 'r2', 'r2'), ('R1', 'R2', 'R2', 'r1'),
         ('R1', 'r2', 'R1', 'R1'), ('R1', 'r2', 'R1', 'r2'), ('F', 'R1', 'R1', 'R2'), ('F', 'R1', 'R1', 'r2'), ('F', 'R1', 'R2', 'R2'),
         ('F', 'R1', 'R2', 'r1'), ('F', 'R1', 'r2', 'R1'), ('F', 'R1', 'r2', 'r1'), ('F', 'R1', 'r2', 'r2'), ('F', 'R2', 'R2', 'r1'),
         ('F', 'R2', 'r1', 'R2'), ('F', 'R2', 'r1', 'r1'), ('F', 'r2', 'R1', 'R1'), ('F', 'r2', 'R1', 'r2'), ('F', 'r2', 'r2', 'R1'),
         ('R2', 'R1', 'R1', 'r2'), ('R2', 'R2', 'R1', 'R1'), ('R2', 'R2', 'r1', 'R2'), ('R2', 'R2', 'r1', 'r1'), ('R2', 'r1', 'R2', 'R2'),
         ('R2', 'r1', 'R2', 'r1'), ('r1', 'R2', 'r1', 'R2'), ('r1', 'r1', 'R2', 'R2'), ('r2', 'R1', 'r2', 'R1'), ('r2', 'r2', 'R1', 'R1'),
         ('R1', 'R1', 'F', 'R2', 'R2'), ('R1', 'R1', 'F', 'R2', 'r1'), ('R1', 'R1', 'F', 'r2', 'r2'), ('R1', 'R1', 'R2', 'R2', 'r1'),
         ('R1', 'R1', 'r2', 'R1', 'r2'), ('R1', 'F', 'R2', 'r1', 'R2'), ('R1', 'F', 'R2', 'r1', 'r1'), ('R1', 'F', 'r2', 'r2', 'R1'),
         ('R1', 'R2', 'R2', 'r1', 'R2'), ('R1', 'r2', 'R1', 'r2', 'R1'), ('F', 'R1', 'R1', 'R2', 'R2'), ('F', 'R1', 'R1', 'r2', 'r2'),
         ('F', 'R1', 'R2', 'R2', 'r1'), ('F', 'R1', 'r2', 'R1', 'r2'), ('F', 'R2', 'R2', 'r1', 'R2'), ('F', 'R2', 'R2', 'r1', 'r1'),
         ('F', 'R2', 'r1', 'R2', 'R2'), ('F', 'R2', 'r1', 'R2', 'r1'), ('F', 'r2', 'R1', 'r2', 'R1'), ('F', 'r2', 'r2', 'R1', 'R1'),
         ('R2', 'R2', 'R1', 'R1', 'r2'), ('R1', 'R1', 'F', 'R2', 'r1', 'R2'), ('R1', 'R1', 'F', 'r2', 'r2', 'R1'),
         ('R1', 'R1', 'R2', 'R2', 'r1', 'R2'), ('R1', 'F', 'R2', 'r1', 'R2', 'R2'), ('R1', 'F', 'R2', 'r1', 'R2', 'r1'),
         ('F', 'R1', 'R2', 'R2', 'r1', 'R2'), ('R1', 'R1', 'F', 'R2', 'r1', 'R2', 'R2')]

        self.transformation_dict = {'R1':'DU','R2':'BF','r1':'UD','r2':'FB'}
        

        self.axis = {}
        
        self.myperms = {}
        self.myperms2 = {}

        self.myperms2['OP-Y'] = ("U+ ",)
        self.myperms2['OP-Z'] = ("U++",)

        self.myperms2['T-Perm-A'] = ("R+ ","U+ ","R- ","U- ","R- ","F+ ","R++","U- ","R- ","U- ","R+ ","U+ ","R- ","F- ")
        self.myperms2['T-Perm-B'] = ("U--","R--","U++","R++","U+ ","R--","U- ","R++","U+ ","R--","U++","R++")
        self.myperms2['J-Perm-A'] = ('R+ ', 'U+ ', 'R--', 'F- ', 'R+ ', 'U+ ', 'R+ ', 'U- ', 'R- ', 'F+ ', 'R+ ', 'U- ', 'R- ')
        self.myperms2['J-Perm-B'] = ("R+ ","U++","R- ","U--","R+ ","U- ","R- ","U- ","R- ","U--","R+ ","U+ ","R- ","U+ ","R++","U+ ","R- ")
        self.myperms2['Y-Perm-A'] = ("F+ ","R+ ","U- ","R- ","U- ","R+ ","U+ ","R- ","F- ","R+ ","U+ ","R- ","U- ","R- ","F+ ","R+ ","F- ")
        self.myperms2['Y-Perm-B'] = ("R--","U++","R++","U--","R--","U+ ","R++","U--","R--","U++","R++","U+ ")
        self.myperms2['R-Perm'] = ("U+ ","R--","F+ ","R+ ","U+ ","R+ ","U- ","R- ","F- ","R+ ","U--","R- ","U++","R+ ","U+ ")
        self.myperms2['F-Perm-A'] = ("R++","U++","R--","U+ ","R++","U++","R--","U++")
        self.myperms2['j-Perm-A'] = self.invert_moves(self.myperms2['J-Perm-A'])
        self.myperms2['j-Perm-B'] = self.invert_moves(self.myperms2['J-Perm-B'])
        self.myperms2['t-Perm-B'] = self.invert_moves(self.myperms2['T-Perm-B'])
        self.myperms2['y-Perm-B'] = self.invert_moves(self.myperms2['Y-Perm-B'])




        self.myperms2['O-Perm'] = ("R--","U- ","R++","F++","R--","F--","U- ","F++","R++","F--","R--","U++","R++")
        self.myperms2['S-Perm'] = ("R++","U--","R--","F--","U- ","F++","U- ","R++","U- ","R--","F--","U--","F++")
        self.myperms2['X-Perm'] = ('L- ', 'P- ', 'Q+ ', 'P+ ', 'L+ ', 'P- ', 'Q- ', 'P+ ', 'Q+ ', 'P- ', 'Q- ', 'R+ ', 'Q+ ', 'P+ ', 'Q- ', 'R- ')
        self.myperms2['K-Perm'] = ('F+ ', 'R- ', 'F- ', 'L+ ', 'F+ ', 'R+ ', 'F- ', 'L- ', 'F+ ', 'R+ ', 'F- ', 'L+ ', 'F+ ', 'R- ', 'F- ', 'L- ')
        self.myperms2['W-Perm'] = ('F- ', 'L- ', 'P- ', 'L+ ', 'F+ ', 'L- ', 'P+ ', 'L+ ', 'R+ ', 'Q+ ', 'R- ', 'F+ ', 'R+ ', 'Q- ', 'R- ', 'F- ')

        self.myperms2['Q-Perm'] = ('F--', 'G+ ', 'F- ', 'R--', 'F+ ', 'G- ', 'F- ', 'R++', 'F--', 'P++', 'X- ', 'P+ ', 'Q++', 'P- ', 'X+ ', 'P+ ', 'Q--', 'P++')
        self.myperms2['E-Perm'] = ("R++","U++","R--","U+ ","R++","U- ","R--","U+ ","R++","U- ","R--","U+ ","R++","U++","R--")
  

        #('R++', 'Q--', 'R- ', 'Q+ ', 'R+ ', 'Q+ ', 'R--', 'F- ', 'U- ', 'Q- ', 'U+ ', 'Q+ ', 'F+ ')
        #('P- ', 'Q- ', 'R++', 'Q--', 'R- ', 'Q+ ', 'R+ ', 'Q+ ', 'R--', 'F- ', 'U- ', 'Q- ', 'U+ ', 'Q++', 'F+ ', 'P+ ')
        #('R- ', 'F- ', 'L++', 'F--', 'L- ', 'F+ ', 'L+ ', 'F+ ', 'L--', 'P- ', 'U- ', 'F- ', 'U+ ', 'F++', 'P+ ', 'R+ ')
        #('Q++', 'P--', 'Q- ', 'P+ ', 'Q+ ', 'P+ ', 'Q--', 'R- ', 'U- ', 'P- ', 'U+ ', 'P+ ', 'R+ ')
        #('L- ', 'P- ', 'Q++', 'P--', 'Q- ', 'P+ ', 'Q+ ', 'P+ ', 'Q--', 'R- ', 'U- ', 'P- ', 'U+ ', 'P++', 'R+ ', 'L+ ')
        #('P++', 'L--', 'P- ', 'L+ ', 'P+ ', 'L+ ', 'P--', 'Q- ', 'U- ', 'L- ', 'U+ ', 'L+ ', 'Q+ ')
        #('Q- ', 'R+ ', 'Q+ ', 'U--', 'R- ', 'U--', 'R++', 'U+ ', 'Q+ ', 'U- ', 'Q- ', 'R++', 'U+ ', 'R++', 'U--', 'R- ')
        
        self.myperms2['o-Perm'] = ("R--","U- ","R++","F++","R--","F--","U- ","F++","R++","F--","R--","U++","R++","U- ")
        self.myperms2['s-Perm'] = ("R++","U--","R--","F--","U- ","F++","U- ","R++","U- ","R--","F--","U--","F++","U--")
        
        self.myperms2['x-Perm-A'] = ('L- ', 'Q- ', 'U++', 'Q+ ', 'U+ ', 'L+ ', 'F+ ', 'P+ ', 'U--', 'F- ', 'U- ', 'P- ')
        self.myperms2['x-Perm-B'] = ('Q--', 'R++', 'Q+ ', 'R- ', 'Q- ', 'R- ', 'Q++', 'P+ ', 'U+ ', 'R+ ', 'U++', 'P- ', 'U- ', 'R- ', 'F- ', 'Q- ', 'U++', 'F+ ', 'U+ ', 'Q+ ')
        self.myperms2['x-Perm-C'] = ('L- ', 'U- ', 'P- ', 'U- ', 'P+ ', 'U++', 'L+ ', 'P- ', 'U- ', 'Q- ', 'U+ ', 'Q+ ', 'P+ ', 'L- ', 'U- ', 'P- ', 'U+ ', 'P+ ', 'L+ ', 'Q+ ', 'P+ ', 'U+ ', 'P- ', 'U- ', 'Q- ')
        self.myperms2['x-Perm-D'] = ('L- ', 'U- ', 'P- ', 'U+ ', 'P+ ', 'L+ ', 'R+ ', 'U+ ', 'Q+ ', 'U+ ', 'Q- ', 'U--', 'R- ')
        self.myperms2['x-Perm-E'] = ('L- ', 'U--', 'P- ', 'U+ ', 'P+ ', 'U+ ', 'L+ ', 'R+ ', 'Q+ ', 'U+ ', 'Q- ', 'U- ', 'R- ')
        self.myperms2['x-Perm-Q'] = ('L- ', 'U- ', 'P+ ', 'U+ ', 'L+ ', 'P- ', 'U- ', 'P- ', 'Q+ ', 'U+ ', 'P+ ', 'U- ', 'Q- ', 'U+ ')
        
        
        self.myperms2['k-Perm-A'] = ('Q+ ', 'U--', 'Q- ', 'P- ', 'R- ', 'U++', 'R+ ', 'U+ ', 'P+ ', 'L+ ', 'Q+ ', 'U--', 'L- ', 'U+ ', 'Q- ')
        self.myperms2['k-Perm-B'] = ('L- ', 'U- ', 'P- ', 'U- ', 'P+ ', 'U++', 'L+ ', 'R+ ', 'U+ ', 'Q+ ', 'U- ', 'Q- ', 'R- ')
        self.myperms2['k-Perm-C'] = ('Q+ ', 'U--', 'Q- ', 'P- ', 'R- ', 'U++', 'R+ ', 'U+ ', 'P+ ', 'L+ ', 'Q+ ', 'U--', 'L- ', 'U+ ', 'P+ ', 'L--', 'P++', 'L+ ', 'P- ', 'L- ', 'P- ', 'L++', 'F+ ', 'U+ ', 'P+ ', 'U- ', 'P--', 'F- ', 'Q- ')
        self.myperms2['k-Perm-D'] = ('L- ', 'P- ', 'Q++', 'P--', 'Q- ', 'P+ ', 'Q+ ', 'P+ ', 'Q--', 'R- ', 'U- ', 'P- ', 'U+ ', 'P++', 'R+ ', 'U- ', 'P- ', 'U- ', 'P+ ', 'U++', 'L+ ', 'R+ ', 'U+ ', 'Q+ ', 'U- ', 'Q- ', 'R- ')
        self.myperms2['k-Perm-E'] = ('Q++', 'P--', 'Q- ', 'P+ ', 'Q+ ', 'P+ ', 'Q--', 'R- ', 'U- ', 'P- ', 'U+ ', 'R+ ', 'U++', 'P+ ', 'Q+ ', 'L+ ', 'U--', 'L- ', 'U- ', 'Q- ', 'R- ', 'P- ', 'U++', 'R+ ', 'U- ', 'P+ ')
        self.myperms2['k-Perm-Q'] = ('L- ', 'U- ', 'P- ', 'U+ ', 'P+ ', 'L--', 'G- ', 'L+ ', 'P++', 'L- ', 'G+ ', 'L+ ', 'P--', 'L++', 'U+ ', 'F- ', 'L- ', 'P- ', 'U- ', 'P+ ', 'L+ ', 'U+ ', 'F+ ')

        
        self.myperms2['w-Perm-A'] = ('Q--', 'U--', 'Q++', 'U- ', 'Q--', 'U--', 'Q++', 'U- ', 'P++', 'X- ', 'P+ ', 'Q++', 'P- ', 'X+ ', 'P+ ', 'Q--', 'P++')
        self.myperms2['w-Perm-B'] = ('R+ ', 'Q+ ', 'U+ ', 'Q- ', 'U- ', 'R--', 'U- ', 'F- ', 'U- ', 'F+ ', 'U++', 'F- ', 'L- ', 'F+ ', 'R+ ', 'F- ', 'L+ ', 'F+ ')
        self.myperms2['w-Perm-C'] = ('Q- ', 'U- ', 'R- ', 'U- ', 'R+ ', 'U++', 'Q+ ', 'R- ', 'U- ', 'F- ', 'U+ ', 'F+ ', 'R+ ', 'L- ', 'P- ', 'U- ', 'P+ ', 'U+ ', 'L+ ', 'Q+ ', 'U+ ', 'P+ ', 'U- ', 'P- ', 'Q- ')
        self.myperms2['w-Perm-D'] = ('Q+ ', 'U+ ', 'P+ ', 'U- ', 'P- ', 'Q- ', 'L- ', 'P- ', 'U- ', 'P+ ', 'U+ ', 'L+ ', 'P- ', 'Q- ', 'U- ', 'Q+ ', 'U+ ', 'P+ ', 'R+ ', 'U+ ', 'Q+ ', 'U- ', 'Q- ', 'R- ')
        self.myperms2['w-Perm-E'] = ('R++', 'U++', 'R--', 'U+ ', 'R++', 'U++', 'R--', 'F++', 'U++', 'F--', 'U+ ', 'F++', 'U++', 'F--', 'U--', 'L+ ', 'U++', 'F+ ', 'U- ', 'F- ', 'U- ', 'L- ', 'F+ ', 'R+ ', 'U+ ', 'R- ', 'U- ', 'F- ')
        self.myperms2['w-Perm-Q'] = ('Q- ', 'R+ ', 'Q+ ', 'U--', 'R- ', 'U--', 'R++', 'U+ ', 'Q+ ', 'U- ', 'Q- ', 'R++', 'U+ ', 'R++', 'U--', 'R- ') + ('Q--', 'U--', 'Q++', 'U- ', 'Q--', 'U--', 'Q++', 'U- ', 'P++', 'X- ', 'P+ ', 'Q++', 'P- ', 'X+ ', 'P+ ', 'Q--', 'P++')


        self.myperms2['q-Perm'] = ("R++","U++","R--","U+ ","R++","U++","R--","F++","U++","F--","U+ ","F++","U++","F--","U--")
        self.myperms2['e-Perm'] = ("R- ","U--","R+ ","U- ","R- ","U--","R++","U--","R- ","U- ","R+ ","U--","R- ","U--")


        self.myperms2['o-Perm-B'] = ("F- ","R- ","Q- ","P- ","F+ ","L- ","F- ") + self.myperms2['o-Perm'] + ("F+ ","L+ ","F- ","P+ ","Q+ ","R+ ","F+ ")
        self.myperms2['s-Perm-B'] = ("F- ","R- ","Q- ","P- ","F+ ","L- ","F- ") + self.myperms2['s-Perm'] + ("F+ ","L+ ","F- ","P+ ","Q+ ","R+ ","F+ ")
        self.myperms2['o-Perm-C'] = ("F--","R--","Q--","P--","L--") + self.myperms2['o-Perm'] + ("L++","P++","Q++","R++","F++")
        self.myperms2['s-Perm-C'] = ("F--","R--","Q--","P--","L--") + self.myperms2['s-Perm'] + ("L++","P++","Q++","R++","F++")

        

        self.myperms2['OLL-00-'] = ("F+ ","R+ ","U+ ","R- ","U- ","F- ")
        self.myperms2['OLL-01-'] = ("F+ ","U+ ","R+ ","U- ","R- ","F- ")
        self.myperms2['OLL-02-'] = ("R+ ","U++","R- ","U- ","R+ ","U- ","R- ")
        self.myperms2['OLL-03-'] = ("R+ ","U+ ","R- ","U+ ","R+ ","U--","R- ")
        self.myperms2['OLL-04-'] = ("R- ","U- ","F+ ","U+ ","R+ ","U- ","R- ","F- ","R+ ")
        self.myperms2['OLL-05-'] = ("R- ","F+ ","R+ ","U+ ","R- ","U- ","F- ","U+ ","R+ ")
        self.myperms2['OLL-06-'] = ("R+ ","U+ ","R- ","U- ","R- ","F+ ","R++","U+ ","R- ","U- ","F- ")
        self.myperms2['OLL-07-'] = ("F+ ","U+ ","R+ ","U- ","R--","F- ","R+ ","U+ ","R+ ","U- ","R- ")
        self.myperms2['OLL-08-'] = ("L+ ","F++","R- ","F- ","R+ ","F- ","L- ")
        self.myperms2['OLL-09-'] = ("L+ ","F+ ","R- ","F+ ","R+ ","F--","L- ")
        self.myperms2['OLL-10-'] = ("F+ ","R+ ","U- ","R- ","U- ","R+ ","U+ ","R- ","F- ")
        self.myperms2['OLL-11-'] = ("F+ ","R+ ","U- ","R- ","U+ ","R+ ","U+ ","R- ","F- ")
        self.myperms2['OLL-12-'] = ("F+ ","R+ ","U- ","R- ","U--","R+ ","U+ ","R- ","F- ")
        self.myperms2['OLL-13-'] = ("F+ ","R+ ","U- ","R- ","U++","R+ ","U+ ","R- ","F- ")
        self.myperms2['OLL-14-'] = ("R+ ","U+ ","R- ","U- ","R- ","F+ ","R+ ","F- ")
        self.myperms2['OLL-15-'] = ("F+ ","R- ","F- ","R+ ","U+ ","R+ ","U- ","R- ")
        self.myperms2['OLL-16-'] = ("R+ ","U+ ","R- ","U+ ","R- ","F+ ","R+ ","F- ","U--","R- ","F+ ","R+ ","F- ")
        self.myperms2['OLL-17-'] = ("F+ ","R- ","F- ","R+ ","U++","F+ ","R- ","F- ","R+ ","U- ","R+ ","U- ","R- ")
        self.myperms2['OLL-18-'] = ("R+ ","U++","R--","F+ ","R+ ","F- ","U--","R- ","F+ ","R+ ","F- ")
        self.myperms2['OLL-19-'] = ("F+ ","R- ","F- ","R+ ","U++","F+ ","R- ","F- ","R++","U--","R- ")
        self.myperms2['OLL-20-'] = ("R+ ","U++","R--","F+ ","R+ ","F- ","R+ ","U--","R- ")
        self.myperms2['OLL-21-'] = ("R+ ","U++","R- ","F+ ","R- ","F- ","R++","U--","R- ")
        self.myperms2['OLL-22-'] = ("R+ ","U+ ","R--","U- ","R- ","F+ ","R+ ","U+ ","R+ ","U- ","F- ")
        self.myperms2['OLL-23-'] = ("F+ ","U+ ","R- ","U- ","R- ","F- ","R+ ","U+ ","R++","U- ","R- ")
        self.myperms2['OLL-24-'] = ("R- ","U- ","R- ","F+ ","R+ ","F- ","U+ ","R+ ")
        self.myperms2['OLL-25-'] = ("R- ","U- ","F+ ","R- ","F- ","R+ ","U+ ","R+ ")
        self.myperms2['OLL-26-'] = ("F+ ",) + ("R+ ","U+ ","R- ","U- ") * 2 + ("F- ",)
        self.myperms2['OLL-27-'] = ("F+ ",) + ("U+ ","R+ ","U- ","R- ") * 2 + ("F- ",)
        self.myperms2['OLL-28-'] = ("R- ","U- ") + ("R- ","F+ ","R+ ","F- ") * 2 + ("U+ ","R+ ")
        self.myperms2['OLL-29-'] = ("R- ","U- ") + ("F+ ","R- ","F- ","R+ ") * 2 + ("U+ ","R+ ")
        self.myperms2['OLL-30-'] = ("R+ ","U+ ","R- ","U+ ","R+ ","U- ","R- ","U- ","R- ","F+ ","R+ ","F- ")
        self.myperms2['OLL-31-'] = ("F+ ","R- ","F- ","R+ ","U+ ","R+ ","U+ ","R- ","U- ","R+ ","U- ","R- ")
        self.myperms2['OLL-32-'] = ("R+ ","U+ ","R- ","U++","R+ ","U--","R- ","U+ ","R+ ","U--","R- ")
        self.myperms2['OLL-33-'] = ("R+ ","U++","R- ","U- ","R+ ","U++","R- ","U--","R+ ","U- ","R- ")
        self.myperms2['OLL-34-'] = ("F+ ","R+ ","U+ ","R- ","U- ","F- ","Q+ ","U+ ","P+ ","U- ","P- ","Q- ")
        self.myperms2['OLL-35-'] = ("Q+ ","P+ ","U+ ","P- ","U- ","Q- ","F+ ","U+ ","R+ ","U- ","R- ","F- ")
        self.myperms2['OLL-36-'] = ("Q+ ","U+ ","P+ ","U- ","P- ","Q- ","U+ ","F+ ","R+ ","U+ ","R- ","U- ","F- ")
        self.myperms2['OLL-37-'] = ("F+ ","U+ ","R+ ","U- ","R- ","F- ","U- ","Q+ ","P+ ","U+ ","P- ","U- ","Q- ")     
        self.myperms2['OLL-38-'] = ("L+ ","F+ ","L- ","R+ ","U+ ","R- ","U- ","L+ ","F- ","L- ")
        self.myperms2['OLL-39-'] = ("L+ ","F+ ","L- ","U+ ","R+ ","U- ","R- ","L+ ","F- ","L- ")        
        self.myperms2['OLL-40-'] = ("L+ ","F+ ","L- ","R+ ","U+ ","R- ","U- ","R+ ","U+ ","R- ","U- ","L+ ","F- ","L- ")
        self.myperms2['OLL-41-'] = ("L+ ","F+ ","L- ","U+ ","R+ ","U- ","R- ","U+ ","R+ ","U- ","R- ","L+ ","F- ","L- ")
        self.myperms2['OLL-42-'] = ('L+ ', 'U--', 'L- ', 'U--', 'L+ ', 'U- ', 'L- ')
        self.myperms2['OLL-43-'] = ('L+ ', 'U+ ', 'L- ', 'U++', 'L+ ', 'U++', 'L- ')
        self.myperms2['OLL-44-'] = ("F+ ","R+ ","U++","R- ","U--","F- ")
        self.myperms2['OLL-45-'] = ("F+ ","U++","R+ ","U--","R- ","F- ") 

        

        
        
        
        

        self.myperms2['CO2-A'] = ('F++','H- ','D- ','H+ ','F+ ','H- ','D+ ','H++','F++','U+ ','F--','H- ','F++','U- ')
        self.myperms2['CO2-B'] = ('R- ', 'U+ ', 'L+ ', 'U- ', 'R++', 'Q+ ', 'R- ', 'U+ ', 'L- ', 'U- ', 'R+ ', 'Q- ', 'R- ')
        self.myperms2['CO2-C'] = ('F++','R- ','Y- ','R+ ','F--','U- ','F+ ','R- ','Y+ ','R+ ','F- ','U+ ')
        self.myperms2['CO2-D'] = ('Y+ ', 'R++', 'F- ', 'L- ', 'F+ ', 'R--', 'Y+ ', 'R--', 'F- ', 'L+ ', 'F+ ', 'R++', 'Y--')
        self.myperms2['CO2-E'] = ('Y++', 'R++', 'F- ', 'L- ', 'F+ ', 'R--', 'Y+ ', 'R--', 'F- ', 'L+ ', 'F+ ', 'R++', 'Y++')
        self.myperms2['CO2-b'] = self.invert_moves(self.myperms2['CO2-B'])

        self.myperms2['CO3-U'] = ('Q+ ', 'U- ', 'L- ', 'U+ ', 'Q--', 'R- ', 'Q+ ', 'P--', 'Q- ', 'R+ ', 'Q+ ', 'P++', 'U- ', 'L+ ', 'U+ ')
        self.myperms2['CO3-V'] = ("Q- ",'R++', 'Y- ', 'R+ ', 'F++', 'R- ', 'Y+ ', 'R+ ', 'F--', 'R+ ', 'U+ ', 'L+ ', 'U- ', 'R+ ', 'U+ ', 'L- ', 'U- ',"Q+ ")

        self.myperms2['CO3-I(YRQ)-A'] = self.conjugate(("Q++",),self.myperms2['CO3-V'])
        self.myperms2['CO3-I(YRQ)-B'] = self.invert_moves(self.myperms2['CO3-I(YRQ)-A'])

        self.myperms2['CO3-I(BQP)'] = self.conjugate(("Q- ",),self.myperms2['CO3-V'])
        
        self.myperms2['CO3-I(QBY)-A'] = self.conjugate(("Q--",),self.myperms2['CO3-V'])
        self.myperms2['CO3-I(QBY)-B'] = self.invert_moves(self.myperms2['CO3-I(QBY)-A'])

        self.myperms2['CO3-I(DYB)-A'] = self.conjugate(("B+ ","Q--",),self.myperms2['CO3-V'])
        self.myperms2['CO3-I(DYB)-B'] = self.invert_moves(self.myperms2['CO3-I(DYB)-A'])

        self.myperms2['CO3-II(BQP)'] = ('P- ', 'U+ ', 'R+ ', 'U- ', 'P++', 'U+ ', 'R- ', 'U- ', 'P- ', 'Q+ ', 'P+ ', 'L+ ', 'P- ', 'Q--', 'P+ ', 'L- ', 'P- ', 'Q+ ')

        self.myperms2['CO3-II(QBY)-A'] = self.conjugate(("B+ ",),self.myperms2['CO3-II(BQP)'])
        self.myperms2['CO3-II(QBY)-B'] = self.invert_moves(self.myperms2['CO3-II(QBY)-A'])

        self.myperms2['CO3-II(RYH)'] = self.conjugate(("Y++","B+ ",),self.myperms2['CO3-II(BQP)'])

        self.myperms2['CO3-II(DYB)-A'] = self.conjugate(("B++",),self.myperms2['CO3-II(BQP)'])
        self.myperms2['CO3-II(DYB)-B'] = self.invert_moves(self.myperms2['CO3-II(DYB)-A'])

        self.myperms2['CO3-II(DHY)-A'] = self.conjugate(("D+ ","B++",),self.myperms2['CO3-II(BQP)'])
        self.myperms2['CO3-II(DHY)-B'] = self.invert_moves(self.myperms2['CO3-II(DHY)-A'])

        self.myperms2['CO3-II(DGH)'] = self.conjugate(("D++","B++",),self.myperms2['CO3-II(BQP)'])
        self.myperms2['CO3-II(FHG)'] = self.conjugate(("G+ ","D++","B++",),self.myperms2['CO3-II(BQP)'])



        

        self.myperms2['CP-U00-'] = ('P++', 'X- ', 'P+ ', 'Q++', 'P- ', 'X+ ', 'P+ ', 'Q--', 'P++')
        self.myperms2['CP-U01-'] = ('L+ ', 'P- ', 'Q+ ', 'P+ ', 'L- ', 'P- ', 'Q--', 'P+ ', 'L+ ', 'P- ', 'Q+ ', 'P+ ', 'L- ')
        self.myperms2['CP-U02-'] = ('Q+ ', 'P+ ', 'L+ ', 'P- ', 'Q- ', 'P+ ', 'L- ', 'P- ')
        self.myperms2['CP-U03-'] = ('R+ ', 'Q+ ', 'R- ', 'L+ ', 'F+ ', 'R+ ', 'Q--', 'R- ', 'F- ', 'L- ', 'R+ ', 'Q+ ', 'R- ')
        self.myperms2['CP-U04-'] = ('R- ', 'L+ ', 'F+ ', 'R+ ', 'Q- ', 'R- ', 'F- ', 'L- ', 'R+ ', 'Q+ ')
        self.myperms2['CP-U05-'] = ('R- ', 'Q+ ', 'P+ ', 'Q- ', 'R+ ', 'Q+ ', 'P--', 'Q- ', 'R- ', 'Q+ ', 'P+ ', 'Q- ', 'R+ ')
        self.myperms2['CP-U06-'] = ('Q+ ', 'U- ', 'L- ', 'U+ ', 'Q- ', 'U- ', 'L+ ', 'U+ ')
        self.myperms2['CP-U07-'] = ('Q- ', 'R- ', 'Q+ ', 'P- ', 'Q- ', 'R+ ', 'Q+ ', 'P+ ')
        self.myperms2['CP-U08-'] = ('R- ', 'P+ ', 'L+ ', 'F- ', 'L- ', 'P- ', 'L+ ', 'F+ ', 'R+ ', 'L- ')
        


        self.myperms2['CP-V00-'] = ('P+ ', 'L+ ', 'F+ ', 'R+ ', 'F- ', 'L- ', 'F+ ', 'R- ', 'F- ', 'P- ')
        self.myperms2['CP-V01-'] = ('R- ', 'F+ ', 'R+ ', 'Q- ', 'R- ', 'F--', 'R+ ', 'Q+ ', 'R- ', 'F+ ', 'R+ ')
        self.myperms2['CP-V02-'] = ('F- ', 'L++', 'P++', 'L--', 'F- ', 'L++', 'P--', 'L--', 'F++')
        self.myperms2['CP-V03-'] = ('L+ ', 'F+ ', 'L- ', 'P+ ', 'L+ ', 'F--', 'L- ', 'P- ', 'L+ ', 'F+ ', 'L- ')
        self.myperms2['CP-V04-'] = ('L- ', 'P+ ', 'L+ ', 'F- ', 'L- ', 'P- ', 'L+ ', 'F+ ')
        self.myperms2['CP-V05-'] = ('Q+ ', 'P+ ', 'Q- ', 'R++', 'Y- ', 'R+ ', 'F++', 'R- ', 'Y+ ', 'R+ ', 'F--', 'R++', 'Q+ ', 'P- ', 'Q- ')
        self.myperms2['CP-V06-'] = ('F+ ', 'R+ ', 'Q- ', 'R- ', 'F- ', 'R+ ', 'Q+ ', 'R- ')
        self.myperms2['CP-V07-'] = ("Q- ",'F- ', 'L- ', 'F+ ', 'R- ', 'F- ', 'L+ ', 'F+ ', 'R+ ',"Q+ ")
        self.myperms2['CP-V08-'] = ('Q- ', 'R+ ', 'Q+ ', 'L- ', 'P- ', 'Q- ', 'R- ', 'Q+ ', 'P+ ', 'L+ ')

        #CP-I:UFL,URF
        
        self.myperms2['CP-I(YRQ)00-'] = self.conjugate(("Q++",),self.myperms2['CP-V00-'])
        self.myperms2['CP-I(YRQ)01-'] = self.conjugate(("Q++",),self.myperms2['CP-V01-'])
        self.myperms2['CP-I(YRQ)02-'] = self.conjugate(("Q++",),self.myperms2['CP-V02-'])
        self.myperms2['CP-I(YRQ)03-'] = self.conjugate(("Q++",),self.myperms2['CP-V03-'])
        self.myperms2['CP-I(YRQ)04-'] = self.conjugate(("Q++",),self.myperms2['CP-V04-'])
        self.myperms2['CP-I(YRQ)05-'] = self.conjugate(("Q++",),self.myperms2['CP-V05-'])
        self.myperms2['CP-I(YRQ)06-'] = self.conjugate(("Q++",),self.myperms2['CP-V06-'])
        self.myperms2['CP-I(YRQ)07-'] = self.conjugate(("Q++",),self.myperms2['CP-V07-'])
        self.myperms2['CP-I(YRQ)08-'] = self.conjugate(("Q++",),self.myperms2['CP-V08-'])

        self.myperms2['CP-I(YRQ)09-'] = self.invert_moves(self.myperms2['CP-I(YRQ)00-'])
        self.myperms2['CP-I(YRQ)10-'] = self.invert_moves(self.myperms2['CP-I(YRQ)01-'])
        self.myperms2['CP-I(YRQ)11-'] = self.invert_moves(self.myperms2['CP-I(YRQ)02-'])
        self.myperms2['CP-I(YRQ)12-'] = self.invert_moves(self.myperms2['CP-I(YRQ)03-'])
        self.myperms2['CP-I(YRQ)13-'] = self.invert_moves(self.myperms2['CP-I(YRQ)04-'])
        self.myperms2['CP-I(YRQ)14-'] = self.invert_moves(self.myperms2['CP-I(YRQ)05-'])
        self.myperms2['CP-I(YRQ)15-'] = self.invert_moves(self.myperms2['CP-I(YRQ)06-'])
        self.myperms2['CP-I(YRQ)16-'] = self.invert_moves(self.myperms2['CP-I(YRQ)07-'])
        self.myperms2['CP-I(YRQ)17-'] = self.invert_moves(self.myperms2['CP-I(YRQ)08-'])

        self.myperms2['CP-I(BQP)00-'] = self.conjugate(("Q- ",),self.myperms2['CP-V00-'])
        self.myperms2['CP-I(BQP)01-'] = self.conjugate(("Q- ",),self.myperms2['CP-V01-'])
        self.myperms2['CP-I(BQP)02-'] = self.conjugate(("Q- ",),self.myperms2['CP-V02-'])
        self.myperms2['CP-I(BQP)03-'] = self.conjugate(("Q- ",),self.myperms2['CP-V03-'])
        self.myperms2['CP-I(BQP)04-'] = self.conjugate(("Q- ",),self.myperms2['CP-V04-'])
        self.myperms2['CP-I(BQP)05-'] = self.conjugate(("Q- ",),self.myperms2['CP-V05-'])
        self.myperms2['CP-I(BQP)06-'] = self.conjugate(("Q- ",),self.myperms2['CP-V06-'])
        self.myperms2['CP-I(BQP)07-'] = self.conjugate(("Q- ",),self.myperms2['CP-V07-'])
        self.myperms2['CP-I(BQP)08-'] = self.conjugate(("Q- ",),self.myperms2['CP-V08-'])

        self.myperms2['CP-I(QBY)00-'] = self.conjugate(("Q--",),self.myperms2['CP-V00-'])
        self.myperms2['CP-I(QBY)01-'] = self.conjugate(("Q--",),self.myperms2['CP-V01-'])
        self.myperms2['CP-I(QBY)02-'] = self.conjugate(("Q--",),self.myperms2['CP-V02-'])
        self.myperms2['CP-I(QBY)03-'] = self.conjugate(("Q--",),self.myperms2['CP-V03-'])
        self.myperms2['CP-I(QBY)04-'] = self.conjugate(("Q--",),self.myperms2['CP-V04-'])
        self.myperms2['CP-I(QBY)05-'] = self.conjugate(("Q--",),self.myperms2['CP-V05-'])
        self.myperms2['CP-I(QBY)06-'] = self.conjugate(("Q--",),self.myperms2['CP-V06-'])
        self.myperms2['CP-I(QBY)07-'] = self.conjugate(("Q--",),self.myperms2['CP-V07-'])
        self.myperms2['CP-I(QBY)08-'] = self.conjugate(("Q--",),self.myperms2['CP-V08-'])

        self.myperms2['CP-I(QBY)09-'] = self.invert_moves(self.myperms2['CP-I(QBY)00-'])
        self.myperms2['CP-I(QBY)10-'] = self.invert_moves(self.myperms2['CP-I(QBY)01-'])
        self.myperms2['CP-I(QBY)11-'] = self.invert_moves(self.myperms2['CP-I(QBY)02-'])
        self.myperms2['CP-I(QBY)12-'] = self.invert_moves(self.myperms2['CP-I(QBY)03-'])
        self.myperms2['CP-I(QBY)13-'] = self.invert_moves(self.myperms2['CP-I(QBY)04-'])
        self.myperms2['CP-I(QBY)14-'] = self.invert_moves(self.myperms2['CP-I(QBY)05-'])
        self.myperms2['CP-I(QBY)15-'] = self.invert_moves(self.myperms2['CP-I(QBY)06-'])
        self.myperms2['CP-I(QBY)16-'] = self.invert_moves(self.myperms2['CP-I(QBY)07-'])
        self.myperms2['CP-I(QBY)17-'] = self.invert_moves(self.myperms2['CP-I(QBY)08-'])

        self.myperms2['CP-I(DYB)00-'] = self.conjugate(("B+ ","Q--",),self.myperms2['CP-V00-'])
        self.myperms2['CP-I(DYB)01-'] = self.conjugate(("B+ ","Q--",),self.myperms2['CP-V01-'])
        self.myperms2['CP-I(DYB)02-'] = self.conjugate(("B+ ","Q--",),self.myperms2['CP-V02-'])
        self.myperms2['CP-I(DYB)03-'] = self.conjugate(("B+ ","Q--",),self.myperms2['CP-V03-'])
        self.myperms2['CP-I(DYB)04-'] = self.conjugate(("B+ ","Q--",),self.myperms2['CP-V04-'])
        self.myperms2['CP-I(DYB)05-'] = self.conjugate(("B+ ","Q--",),self.myperms2['CP-V05-'])
        self.myperms2['CP-I(DYB)06-'] = self.conjugate(("B+ ","Q--",),self.myperms2['CP-V06-'])
        self.myperms2['CP-I(DYB)07-'] = self.conjugate(("B+ ","Q--",),self.myperms2['CP-V07-'])
        self.myperms2['CP-I(DYB)08-'] = self.conjugate(("B+ ","Q--",),self.myperms2['CP-V08-'])

        self.myperms2['CP-I(DYB)09-'] = self.invert_moves(self.myperms2['CP-I(DYB)00-'])
        self.myperms2['CP-I(DYB)10-'] = self.invert_moves(self.myperms2['CP-I(DYB)01-'])
        self.myperms2['CP-I(DYB)11-'] = self.invert_moves(self.myperms2['CP-I(DYB)02-'])
        self.myperms2['CP-I(DYB)12-'] = self.invert_moves(self.myperms2['CP-I(DYB)03-'])
        self.myperms2['CP-I(DYB)13-'] = self.invert_moves(self.myperms2['CP-I(DYB)04-'])
        self.myperms2['CP-I(DYB)14-'] = self.invert_moves(self.myperms2['CP-I(DYB)05-'])
        self.myperms2['CP-I(DYB)15-'] = self.invert_moves(self.myperms2['CP-I(DYB)06-'])
        self.myperms2['CP-I(DYB)16-'] = self.invert_moves(self.myperms2['CP-I(DYB)07-'])
        self.myperms2['CP-I(DYB)17-'] = self.invert_moves(self.myperms2['CP-I(DYB)08-'])


        #CP-II:ULP,UQR
        self.myperms2['CP-II(BQP)00-'] = ('U- ', 'Q+ ', 'B+ ', 'Q- ', 'U++', 'Q+ ', 'B- ', 'Q- ', 'U- ')
        self.myperms2['CP-II(BQP)01-'] = ('U- ', 'P- ', 'B- ', 'P+ ', 'U++', 'P- ', 'B+ ', 'P+ ', 'U- ')
        self.myperms2['CP-II(BQP)02-'] = ('U++', 'P--', 'U--', 'P- ', 'Q+ ', 'P+ ', 'L+ ', 'P- ', 'Q- ', 'P+ ', 'L- ', 'U++', 'P++', 'U--')
        self.myperms2['CP-II(BQP)03-'] = ('U- ', 'P- ', 'B- ', 'P+ ', 'L- ', 'U+ ', 'P- ', 'B+ ', 'P+ ', 'U- ', 'L+ ', 'U+ ')
        self.myperms2['CP-II(BQP)04-'] = ('U--', 'P++', 'U++', 'L--', 'U--', 'L++', 'P--', 'L--', 'U++', 'L++')
        self.myperms2['CP-II(BQP)05-'] = ('P- ', 'U+ ', 'R+ ', 'U- ', 'P++', 'U+ ', 'R- ', 'U- ', 'P- ')
        self.myperms2['CP-II(BQP)06-'] = ('Q- ', 'P+ ', 'L+ ', 'P- ', 'Q++', 'P+ ', 'L- ', 'P- ', 'Q- ')
        self.myperms2['CP-II(BQP)07-'] = ('P- ', 'Q- ', 'R- ', 'Q+ ', 'P++', 'Q- ', 'R+ ', 'Q+ ', 'P- ')
        self.myperms2['CP-II(BQP)08-'] = ('Q- ', 'U- ', 'L- ', 'U+ ', 'Q++', 'U- ', 'L+ ', 'U+ ', 'Q- ')


        self.myperms2['CP-II(QBY)00-'] = self.conjugate(("B+ ",),self.myperms2['CP-II(BQP)00-'])
        self.myperms2['CP-II(QBY)01-'] = self.conjugate(("B+ ",),self.myperms2['CP-II(BQP)01-'])
        self.myperms2['CP-II(QBY)02-'] = self.conjugate(("B+ ",),self.myperms2['CP-II(BQP)02-'])
        self.myperms2['CP-II(QBY)03-'] = self.conjugate(("B+ ",),self.myperms2['CP-II(BQP)03-'])
        self.myperms2['CP-II(QBY)04-'] = self.conjugate(("B+ ",),self.myperms2['CP-II(BQP)04-'])
        self.myperms2['CP-II(QBY)05-'] = self.conjugate(("B+ ",),self.myperms2['CP-II(BQP)05-'])
        self.myperms2['CP-II(QBY)06-'] = self.conjugate(("B+ ",),self.myperms2['CP-II(BQP)06-'])
        self.myperms2['CP-II(QBY)07-'] = self.conjugate(("B+ ",),self.myperms2['CP-II(BQP)07-'])
        self.myperms2['CP-II(QBY)08-'] = self.conjugate(("B+ ",),self.myperms2['CP-II(BQP)08-'])

        self.myperms2['CP-II(QBY)09-'] = self.invert_moves(self.myperms2['CP-II(QBY)00-'])
        self.myperms2['CP-II(QBY)10-'] = self.invert_moves(self.myperms2['CP-II(QBY)01-'])
        self.myperms2['CP-II(QBY)11-'] = self.invert_moves(self.myperms2['CP-II(QBY)02-'])
        self.myperms2['CP-II(QBY)12-'] = self.invert_moves(self.myperms2['CP-II(QBY)03-'])
        self.myperms2['CP-II(QBY)13-'] = self.invert_moves(self.myperms2['CP-II(QBY)04-'])
        self.myperms2['CP-II(QBY)14-'] = self.invert_moves(self.myperms2['CP-II(QBY)05-'])
        self.myperms2['CP-II(QBY)15-'] = self.invert_moves(self.myperms2['CP-II(QBY)06-'])
        self.myperms2['CP-II(QBY)16-'] = self.invert_moves(self.myperms2['CP-II(QBY)07-'])
        self.myperms2['CP-II(QBY)17-'] = self.invert_moves(self.myperms2['CP-II(QBY)08-'])

        self.myperms2['CP-II(RYH)00-'] = self.conjugate(("Y++","B+ ",),self.myperms2['CP-II(BQP)00-'])
        self.myperms2['CP-II(RYH)01-'] = self.conjugate(("Y++","B+ ",),self.myperms2['CP-II(BQP)01-'])
        self.myperms2['CP-II(RYH)02-'] = self.conjugate(("Y++","B+ ",),self.myperms2['CP-II(BQP)02-'])
        self.myperms2['CP-II(RYH)03-'] = self.conjugate(("Y++","B+ ",),self.myperms2['CP-II(BQP)03-'])
        self.myperms2['CP-II(RYH)04-'] = self.conjugate(("Y++","B+ ",),self.myperms2['CP-II(BQP)04-'])
        self.myperms2['CP-II(RYH)05-'] = self.conjugate(("Y++","B+ ",),self.myperms2['CP-II(BQP)05-'])
        self.myperms2['CP-II(RYH)06-'] = self.conjugate(("Y++","B+ ",),self.myperms2['CP-II(BQP)06-'])
        self.myperms2['CP-II(RYH)07-'] = self.conjugate(("Y++","B+ ",),self.myperms2['CP-II(BQP)07-'])
        self.myperms2['CP-II(RYH)08-'] = self.conjugate(("Y++","B+ ",),self.myperms2['CP-II(BQP)08-'])


        self.myperms2['CP-II(DYB)00-'] = self.conjugate(("B++",),self.myperms2['CP-II(BQP)00-'])
        self.myperms2['CP-II(DYB)01-'] = self.conjugate(("B++",),self.myperms2['CP-II(BQP)01-'])
        self.myperms2['CP-II(DYB)02-'] = self.conjugate(("B++",),self.myperms2['CP-II(BQP)02-'])
        self.myperms2['CP-II(DYB)03-'] = self.conjugate(("B++",),self.myperms2['CP-II(BQP)03-'])
        self.myperms2['CP-II(DYB)04-'] = self.conjugate(("B++",),self.myperms2['CP-II(BQP)04-'])
        self.myperms2['CP-II(DYB)05-'] = self.conjugate(("B++",),self.myperms2['CP-II(BQP)05-'])
        self.myperms2['CP-II(DYB)06-'] = self.conjugate(("B++",),self.myperms2['CP-II(BQP)06-'])
        self.myperms2['CP-II(DYB)07-'] = self.conjugate(("B++",),self.myperms2['CP-II(BQP)07-'])
        self.myperms2['CP-II(DYB)08-'] = self.conjugate(("B++",),self.myperms2['CP-II(BQP)08-'])

        self.myperms2['CP-II(DYB)09-'] = self.invert_moves(self.myperms2['CP-II(DYB)00-'])
        self.myperms2['CP-II(DYB)10-'] = self.invert_moves(self.myperms2['CP-II(DYB)01-'])
        self.myperms2['CP-II(DYB)11-'] = self.invert_moves(self.myperms2['CP-II(DYB)02-'])
        self.myperms2['CP-II(DYB)12-'] = self.invert_moves(self.myperms2['CP-II(DYB)03-'])
        self.myperms2['CP-II(DYB)13-'] = self.invert_moves(self.myperms2['CP-II(DYB)04-'])
        self.myperms2['CP-II(DYB)14-'] = self.invert_moves(self.myperms2['CP-II(DYB)05-'])
        self.myperms2['CP-II(DYB)15-'] = self.invert_moves(self.myperms2['CP-II(DYB)06-'])
        self.myperms2['CP-II(DYB)16-'] = self.invert_moves(self.myperms2['CP-II(DYB)07-'])
        self.myperms2['CP-II(DYB)17-'] = self.invert_moves(self.myperms2['CP-II(DYB)08-'])

        self.myperms2['CP-II(DHY)00-'] = self.conjugate(("D+ ","B++",),self.myperms2['CP-II(BQP)00-'])
        self.myperms2['CP-II(DHY)01-'] = self.conjugate(("D+ ","B++",),self.myperms2['CP-II(BQP)01-'])
        self.myperms2['CP-II(DHY)02-'] = self.conjugate(("D+ ","B++",),self.myperms2['CP-II(BQP)02-'])
        self.myperms2['CP-II(DHY)03-'] = self.conjugate(("D+ ","B++",),self.myperms2['CP-II(BQP)03-'])
        self.myperms2['CP-II(DHY)04-'] = self.conjugate(("D+ ","B++",),self.myperms2['CP-II(BQP)04-'])
        self.myperms2['CP-II(DHY)05-'] = self.conjugate(("D+ ","B++",),self.myperms2['CP-II(BQP)05-'])
        self.myperms2['CP-II(DHY)06-'] = self.conjugate(("D+ ","B++",),self.myperms2['CP-II(BQP)06-'])
        self.myperms2['CP-II(DHY)07-'] = self.conjugate(("D+ ","B++",),self.myperms2['CP-II(BQP)07-'])
        self.myperms2['CP-II(DHY)08-'] = self.conjugate(("D+ ","B++",),self.myperms2['CP-II(BQP)08-'])

        self.myperms2['CP-II(DHY)09-'] = self.invert_moves(self.myperms2['CP-II(DHY)00-'])
        self.myperms2['CP-II(DHY)10-'] = self.invert_moves(self.myperms2['CP-II(DHY)01-'])
        self.myperms2['CP-II(DHY)11-'] = self.invert_moves(self.myperms2['CP-II(DHY)02-'])
        self.myperms2['CP-II(DHY)12-'] = self.invert_moves(self.myperms2['CP-II(DHY)03-'])
        self.myperms2['CP-II(DHY)13-'] = self.invert_moves(self.myperms2['CP-II(DHY)04-'])
        self.myperms2['CP-II(DHY)14-'] = self.invert_moves(self.myperms2['CP-II(DHY)05-'])
        self.myperms2['CP-II(DHY)15-'] = self.invert_moves(self.myperms2['CP-II(DHY)06-'])
        self.myperms2['CP-II(DHY)16-'] = self.invert_moves(self.myperms2['CP-II(DHY)07-'])
        self.myperms2['CP-II(DHY)17-'] = self.invert_moves(self.myperms2['CP-II(DHY)08-'])

        self.myperms2['CP-II(DGH)00-'] = self.conjugate(("D++","B++",),self.myperms2['CP-II(BQP)00-'])
        self.myperms2['CP-II(DGH)01-'] = self.conjugate(("D++","B++",),self.myperms2['CP-II(BQP)01-'])
        self.myperms2['CP-II(DGH)02-'] = self.conjugate(("D++","B++",),self.myperms2['CP-II(BQP)02-'])
        self.myperms2['CP-II(DGH)03-'] = self.conjugate(("D++","B++",),self.myperms2['CP-II(BQP)03-'])
        self.myperms2['CP-II(DGH)04-'] = self.conjugate(("D++","B++",),self.myperms2['CP-II(BQP)04-'])
        self.myperms2['CP-II(DGH)05-'] = self.conjugate(("D++","B++",),self.myperms2['CP-II(BQP)05-'])
        self.myperms2['CP-II(DGH)06-'] = self.conjugate(("D++","B++",),self.myperms2['CP-II(BQP)06-'])
        self.myperms2['CP-II(DGH)07-'] = self.conjugate(("D++","B++",),self.myperms2['CP-II(BQP)07-'])
        self.myperms2['CP-II(DGH)08-'] = self.conjugate(("D++","B++",),self.myperms2['CP-II(BQP)08-'])

        self.myperms2['CP-II(FHG)00-'] = self.conjugate(("G+ ","D++","B++",),self.myperms2['CP-II(BQP)00-'])
        self.myperms2['CP-II(FHG)01-'] = self.conjugate(("G+ ","D++","B++",),self.myperms2['CP-II(BQP)01-'])
        self.myperms2['CP-II(FHG)02-'] = self.conjugate(("G+ ","D++","B++",),self.myperms2['CP-II(BQP)02-'])
        self.myperms2['CP-II(FHG)03-'] = self.conjugate(("G+ ","D++","B++",),self.myperms2['CP-II(BQP)03-'])
        self.myperms2['CP-II(FHG)04-'] = self.conjugate(("G+ ","D++","B++",),self.myperms2['CP-II(BQP)04-'])
        self.myperms2['CP-II(FHG)05-'] = self.conjugate(("G+ ","D++","B++",),self.myperms2['CP-II(BQP)05-'])
        self.myperms2['CP-II(FHG)06-'] = self.conjugate(("G+ ","D++","B++",),self.myperms2['CP-II(BQP)06-'])
        self.myperms2['CP-II(FHG)07-'] = self.conjugate(("G+ ","D++","B++",),self.myperms2['CP-II(BQP)07-'])
        self.myperms2['CP-II(FHG)08-'] = self.conjugate(("G+ ","D++","B++",),self.myperms2['CP-II(BQP)08-'])



        
        self.myperms2['EP-U00-'] = ("L+ ","U+ ","F+ ","U- ","F- ","L- ","R- ","F- ","U- ","F+ ","U+ ","R+ ")
        self.myperms2['EP-U01-'] = ('L+ ', 'U++', 'F+ ', 'U- ', 'F- ', 'U- ', 'L- ', 'F+ ', 'R+ ', 'U+ ', 'R- ', 'U- ', 'F- ')
        self.myperms2['EP-U02-'] = ('R- ', 'F- ', 'U- ', 'F+ ', 'U+ ', 'R+ ', 'L+ ', 'U+ ', 'F+ ', 'U- ', 'F- ', 'L- ')
        self.myperms2['EP-U03-'] = ('F- ', 'U- ', 'L- ', 'U+ ', 'L+ ', 'F+ ', 'R- ', 'U- ', 'F- ', 'U- ', 'F+ ', 'U++', 'R+ ')

        self.myperms2['EP-V00-'] = ('Q+ ', 'U+ ', 'P+ ', 'U+ ', 'P- ', 'U--', 'Q- ', 'P+ ', 'U+ ', 'L+ ', 'U- ', 'L- ', 'P- ')
        self.myperms2['EP-V01-'] = ('F- ', 'L- ', 'Q+ ', 'U++', 'P+ ', 'U- ', 'P- ', 'U- ', 'Q- ', 'P+ ', 'L+ ', 'U+ ', 'L- ', 'U- ', 'P- ', 'L+ ', 'F+ ')
        self.myperms2['EP-V02-'] = ('F- ', 'L--', 'P- ', 'U- ', 'P+ ', 'U+ ', 'L+ ', 'Q+ ', 'U+ ', 'P+ ', 'U- ', 'P- ', 'Q- ', 'L+ ', 'F+ ')
        self.myperms2['EP-V03-'] = ('F- ', 'L- ', 'P- ', 'U- ', 'Q- ', 'U+ ', 'Q+ ', 'P+ ', 'L- ', 'U- ', 'P- ', 'U- ', 'P+ ', 'U++', 'L++', 'F+ ')


        #EP-I:UP,UQ

        self.myperms2['EP-I(RF)00-'] = self.conjugate(("F- ",),self.myperms2['EP-V00-'])
        self.myperms2['EP-I(RF)01-'] = self.conjugate(("F- ",),self.myperms2['EP-V01-'])
        self.myperms2['EP-I(RF)02-'] = self.conjugate(("F- ",),self.myperms2['EP-V02-'])
        self.myperms2['EP-I(RF)03-'] = self.conjugate(("F- ",),self.myperms2['EP-V03-'])

        self.myperms2['EP-I(RF)04-'] = self.invert_moves(self.myperms2['EP-I(RF)00-'])
        self.myperms2['EP-I(RF)05-'] = self.invert_moves(self.myperms2['EP-I(RF)01-'])
        self.myperms2['EP-I(RF)06-'] = self.invert_moves(self.myperms2['EP-I(RF)02-'])
        self.myperms2['EP-I(RF)07-'] = self.invert_moves(self.myperms2['EP-I(RF)03-'])


        self.myperms2['EP-I(QR)00-'] = self.conjugate(("R--","F- ",),self.myperms2['EP-V00-'])
        self.myperms2['EP-I(QR)01-'] = self.conjugate(("R--","F- ",),self.myperms2['EP-V01-'])
        self.myperms2['EP-I(QR)02-'] = self.conjugate(("R--","F- ",),self.myperms2['EP-V02-'])
        self.myperms2['EP-I(QR)03-'] = self.conjugate(("R--","F- ",),self.myperms2['EP-V03-'])

        self.myperms2['EP-I(QR)04-'] = self.invert_moves(self.myperms2['EP-I(QR)00-'])
        self.myperms2['EP-I(QR)05-'] = self.invert_moves(self.myperms2['EP-I(QR)01-'])
        self.myperms2['EP-I(QR)06-'] = self.invert_moves(self.myperms2['EP-I(QR)02-'])
        self.myperms2['EP-I(QR)07-'] = self.invert_moves(self.myperms2['EP-I(QR)03-'])
        
        self.myperms2['EP-I(PQ)00-'] = self.conjugate(("U++","Q- ","U+ "),self.myperms2['EP-U00-'])
        self.myperms2['EP-I(PQ)01-'] = self.conjugate(("U++","Q- ","U+ "),self.myperms2['EP-U01-'])
        self.myperms2['EP-I(PQ)02-'] = self.conjugate(("U++","Q- ","U+ "),self.myperms2['EP-U02-'])
        self.myperms2['EP-I(PQ)03-'] = self.conjugate(("U++","Q- ","U+ "),self.myperms2['EP-U03-'])

        self.myperms2['EP-I(FH)00-'] = self.conjugate(("F--",),self.myperms2['EP-V00-'])
        self.myperms2['EP-I(FH)01-'] = self.conjugate(("F--",),self.myperms2['EP-V01-'])
        self.myperms2['EP-I(FH)02-'] = self.conjugate(("F--",),self.myperms2['EP-V02-'])
        self.myperms2['EP-I(FH)03-'] = self.conjugate(("F--",),self.myperms2['EP-V03-'])

        self.myperms2['EP-I(FH)04-'] = self.invert_moves(self.myperms2['EP-I(FH)00-'])
        self.myperms2['EP-I(FH)05-'] = self.invert_moves(self.myperms2['EP-I(FH)01-'])
        self.myperms2['EP-I(FH)06-'] = self.invert_moves(self.myperms2['EP-I(FH)02-'])
        self.myperms2['EP-I(FH)07-'] = self.invert_moves(self.myperms2['EP-I(FH)03-'])
        
        self.myperms2['EP-I(RH)00-'] = self.conjugate(("R+ ","F- ",),self.myperms2['EP-V00-'])
        self.myperms2['EP-I(RH)01-'] = self.conjugate(("R+ ","F- ",),self.myperms2['EP-V01-'])
        self.myperms2['EP-I(RH)02-'] = self.conjugate(("R+ ","F- ",),self.myperms2['EP-V02-'])
        self.myperms2['EP-I(RH)03-'] = self.conjugate(("R+ ","F- ",),self.myperms2['EP-V03-'])

        self.myperms2['EP-I(RH)04-'] = self.invert_moves(self.myperms2['EP-I(RH)00-'])
        self.myperms2['EP-I(RH)05-'] = self.invert_moves(self.myperms2['EP-I(RH)01-'])
        self.myperms2['EP-I(RH)06-'] = self.invert_moves(self.myperms2['EP-I(RH)02-'])
        self.myperms2['EP-I(RH)07-'] = self.invert_moves(self.myperms2['EP-I(RH)03-'])

        self.myperms2['EP-I(RY)00-'] = self.conjugate(("R++","F- ",),self.myperms2['EP-V00-'])
        self.myperms2['EP-I(RY)01-'] = self.conjugate(("R++","F- ",),self.myperms2['EP-V01-'])
        self.myperms2['EP-I(RY)02-'] = self.conjugate(("R++","F- ",),self.myperms2['EP-V02-'])
        self.myperms2['EP-I(RY)03-'] = self.conjugate(("R++","F- ",),self.myperms2['EP-V03-'])

        self.myperms2['EP-I(RY)04-'] = self.invert_moves(self.myperms2['EP-I(RY)00-'])
        self.myperms2['EP-I(RY)05-'] = self.invert_moves(self.myperms2['EP-I(RY)01-'])
        self.myperms2['EP-I(RY)06-'] = self.invert_moves(self.myperms2['EP-I(RY)02-'])
        self.myperms2['EP-I(RY)07-'] = self.invert_moves(self.myperms2['EP-I(RY)03-'])

        self.myperms2['EP-I(QY)00-'] = self.conjugate(("Y- ","R++","F- ",),self.myperms2['EP-V00-'])
        self.myperms2['EP-I(QY)01-'] = self.conjugate(("Y- ","R++","F- ",),self.myperms2['EP-V01-'])
        self.myperms2['EP-I(QY)02-'] = self.conjugate(("Y- ","R++","F- ",),self.myperms2['EP-V02-'])
        self.myperms2['EP-I(QY)03-'] = self.conjugate(("Y- ","R++","F- ",),self.myperms2['EP-V03-'])

        self.myperms2['EP-I(QY)04-'] = self.invert_moves(self.myperms2['EP-I(QY)00-'])
        self.myperms2['EP-I(QY)05-'] = self.invert_moves(self.myperms2['EP-I(QY)01-'])
        self.myperms2['EP-I(QY)06-'] = self.invert_moves(self.myperms2['EP-I(QY)02-'])
        self.myperms2['EP-I(QY)07-'] = self.invert_moves(self.myperms2['EP-I(QY)03-'])

        self.myperms2['EP-I(QB)00-'] = self.conjugate(("B- ","Y--","R++","F- ",),self.myperms2['EP-V00-'])
        self.myperms2['EP-I(QB)01-'] = self.conjugate(("B- ","Y--","R++","F- ",),self.myperms2['EP-V01-'])
        self.myperms2['EP-I(QB)02-'] = self.conjugate(("B- ","Y--","R++","F- ",),self.myperms2['EP-V02-'])
        self.myperms2['EP-I(QB)03-'] = self.conjugate(("B- ","Y--","R++","F- ",),self.myperms2['EP-V03-'])
        
        self.myperms2['EP-I(QB)04-'] = self.invert_moves(self.myperms2['EP-I(QB)00-'])
        self.myperms2['EP-I(QB)05-'] = self.invert_moves(self.myperms2['EP-I(QB)01-'])
        self.myperms2['EP-I(QB)06-'] = self.invert_moves(self.myperms2['EP-I(QB)02-'])
        self.myperms2['EP-I(QB)07-'] = self.invert_moves(self.myperms2['EP-I(QB)03-'])

        self.myperms2['EP-I(GH)00-'] = self.conjugate(("H+ ","F--"),self.myperms2['EP-V00-'])
        self.myperms2['EP-I(GH)01-'] = self.conjugate(("H+ ","F--"),self.myperms2['EP-V01-'])
        self.myperms2['EP-I(GH)02-'] = self.conjugate(("H+ ","F--"),self.myperms2['EP-V02-'])
        self.myperms2['EP-I(GH)03-'] = self.conjugate(("H+ ","F--"),self.myperms2['EP-V03-'])

        self.myperms2['EP-I(HY)00-'] = self.conjugate(("H--","F--"),self.myperms2['EP-V00-'])
        self.myperms2['EP-I(HY)01-'] = self.conjugate(("H--","F--"),self.myperms2['EP-V01-'])
        self.myperms2['EP-I(HY)02-'] = self.conjugate(("H--","F--"),self.myperms2['EP-V02-'])
        self.myperms2['EP-I(HY)03-'] = self.conjugate(("H--","F--"),self.myperms2['EP-V03-'])

        self.myperms2['EP-I(HY)04-'] = self.invert_moves(self.myperms2['EP-I(HY)00-'])
        self.myperms2['EP-I(HY)05-'] = self.invert_moves(self.myperms2['EP-I(HY)01-'])
        self.myperms2['EP-I(HY)06-'] = self.invert_moves(self.myperms2['EP-I(HY)02-'])
        self.myperms2['EP-I(HY)07-'] = self.invert_moves(self.myperms2['EP-I(HY)03-'])

        self.myperms2['EP-I(YB)00-'] = self.conjugate(("Y--","R++","F- ",),self.myperms2['EP-V00-'])
        self.myperms2['EP-I(YB)01-'] = self.conjugate(("Y--","R++","F- ",),self.myperms2['EP-V01-'])
        self.myperms2['EP-I(YB)02-'] = self.conjugate(("Y--","R++","F- ",),self.myperms2['EP-V02-'])
        self.myperms2['EP-I(YB)03-'] = self.conjugate(("Y--","R++","F- ",),self.myperms2['EP-V03-'])

        self.myperms2['EP-I(YB)04-'] = self.invert_moves(self.myperms2['EP-I(YB)00-'])
        self.myperms2['EP-I(YB)05-'] = self.invert_moves(self.myperms2['EP-I(YB)01-'])
        self.myperms2['EP-I(YB)06-'] = self.invert_moves(self.myperms2['EP-I(YB)02-'])
        self.myperms2['EP-I(YB)07-'] = self.invert_moves(self.myperms2['EP-I(YB)03-'])

        self.myperms2['EP-I(DH)00-'] = self.conjugate(("H++","F--"),self.myperms2['EP-V00-'])
        self.myperms2['EP-I(DH)01-'] = self.conjugate(("H++","F--"),self.myperms2['EP-V01-'])
        self.myperms2['EP-I(DH)02-'] = self.conjugate(("H++","F--"),self.myperms2['EP-V02-'])
        self.myperms2['EP-I(DH)03-'] = self.conjugate(("H++","F--"),self.myperms2['EP-V03-'])

        self.myperms2['EP-I(DH)04-'] = self.invert_moves(self.myperms2['EP-I(DH)00-'])
        self.myperms2['EP-I(DH)05-'] = self.invert_moves(self.myperms2['EP-I(DH)01-'])
        self.myperms2['EP-I(DH)06-'] = self.invert_moves(self.myperms2['EP-I(DH)02-'])
        self.myperms2['EP-I(DH)07-'] = self.invert_moves(self.myperms2['EP-I(DH)03-'])

        self.myperms2['EP-I(DY)00-'] = self.conjugate(("D- ","H++","F--"),self.myperms2['EP-V00-'])
        self.myperms2['EP-I(DY)01-'] = self.conjugate(("D- ","H++","F--"),self.myperms2['EP-V01-'])
        self.myperms2['EP-I(DY)02-'] = self.conjugate(("D- ","H++","F--"),self.myperms2['EP-V02-'])
        self.myperms2['EP-I(DY)03-'] = self.conjugate(("D- ","H++","F--"),self.myperms2['EP-V03-'])

        self.myperms2['EP-I(DY)04-'] = self.invert_moves(self.myperms2['EP-I(DY)00-'])
        self.myperms2['EP-I(DY)05-'] = self.invert_moves(self.myperms2['EP-I(DY)01-'])
        self.myperms2['EP-I(DY)06-'] = self.invert_moves(self.myperms2['EP-I(DY)02-'])
        self.myperms2['EP-I(DY)07-'] = self.invert_moves(self.myperms2['EP-I(DY)03-'])

        self.myperms2['EP-I(DB)00-'] = self.conjugate(("D--","H++","F--"),self.myperms2['EP-V00-'])
        self.myperms2['EP-I(DB)01-'] = self.conjugate(("D--","H++","F--"),self.myperms2['EP-V01-'])
        self.myperms2['EP-I(DB)02-'] = self.conjugate(("D--","H++","F--"),self.myperms2['EP-V02-'])
        self.myperms2['EP-I(DB)03-'] = self.conjugate(("D--","H++","F--"),self.myperms2['EP-V03-'])



        self.myperms2['EF-A'] = ("F++", "R--", "F- ", "R+ ", "F+ ", "R+ ", "F--",
                                 "L- ", "U- ", "R- ", "U+ ", "R+ ", "L+ ")

        self.myperms2['EF-B'] = ('Q- ', 'R- ', 'F++', 'R--', 'F- ', 'R+ ', 'F+ ', 'R+ ', 'F--', 'L- ', 'U- ', 'R- ', 'U+ ', 'R++', 'L+ ', 'Q+ ')
        self.myperms2['EF-C'] = ('R- ', 'F++', 'R--', 'F- ', 'R+ ', 'F+ ', 'R+ ', 'F--', 'L- ', 'U- ', 'R- ', 'U+ ', 'R++', 'L+ ')
        self.myperms2['EF-D'] = ('R--', 'F++', 'R--', 'F- ', 'R+ ', 'F+ ', 'R+ ', 'F--', 'L- ', 'U- ', 'R- ', 'U+ ', 'R--', 'L+ ')
        self.myperms2['EF-E'] = ('Q+ ', 'R- ', 'F++', 'R--', 'F- ', 'R+ ', 'F+ ', 'R+ ', 'F--', 'L- ', 'U- ', 'R- ', 'U+ ', 'R++', 'L+ ', 'Q- ')
        self.myperms2['EF-F'] = ('H--', 'R++', 'F++', 'R--', 'F- ', 'R+ ', 'F+ ', 'R+ ', 'F--', 'L- ', 'U- ', 'R- ', 'U+ ', 'R- ', 'L+ ', 'H++')
        self.myperms2['EF-G'] = ('Y++', 'R--', 'F++', 'R--', 'F- ', 'R+ ', 'F+ ', 'R+ ', 'F--', 'L- ', 'U- ', 'R- ', 'U+ ', 'R--', 'L+ ', 'Y--')
        self.myperms2['EF-H'] = ('B+ ', 'Y--', 'R--', 'F++', 'R--', 'F- ', 'R+ ', 'F+ ', 'R+ ', 'F--', 'L- ', 'U- ', 'R- ', 'U+ ', 'R--', 'L+ ', 'Y++', 'B- ')

        self.myperms2['EF-Q'] = ('Q- ', 'R+ ', 'Q+ ', 'U--', 'R- ', 'U--', 'R++', 'U+ ', 'Q+ ', 'U- ', 'Q- ', 'R++', 'U+ ', 'R++', 'U--', 'R- ')








        
        self.myperms_group = {'A':set(),
                              'B':set()}


        

        Lis = list(self.myperms2.keys())


        for key in self.myperms2.keys():
            L = self.make_transformations(self.myperms2[key],tuple())
            for i in range(120):
                if i <= 9:
                    SI = '00' + str(i)
                elif i <= 99:
                    SI = '0' + str(i)
                else:
                    SI = str(i)
                       
                self.myperms[key + SI] = L[0][i]        

        


                
    
        self.my_scrambles = []


    

        self.surface_num = 10
        
        self.state = np.zeros(self.surface_num * 12,dtype = str)
        for i in range(12):
            self.state[i*self.surface_num:(i+1)*self.surface_num] = self.colors[i]

        
        self.state_0 = self.state.copy()




        self.move_keys = [s + t for s in self.colors for t in ["+ ","++","- ","--"]]

        

            
        self.move_len = len(self.move_keys)
        self.key_to_num = {}
        for i in range(self.move_len):
            self.key_to_num[self.move_keys[i]] = i

        self.my_scrambles2 = {0:{}}
        for key in self.move_keys:
            self.my_scrambles2[0][key] = set([])

        
        K = {"U":[(0,1,2,3,4),(5,6,7,8,9),(12,22,32,42,52),(13,23,33,43,53),(15,25,35,45,55)],
             "F":[(10,11,12,13,14),(15,16,17,18,19),(2,51,94,80,23),(3,52,90,81,24),(5,59,97,88,26)],
             "L":[(20,21,22,23,24),(25,26,27,28,29),(3,11,84,70,33),(4,12,80,71,34),(6,19,87,78,36)],
             "P":[(30,31,32,33,34),(35,36,37,38,39),(4,21,74,60,43),(0,22,70,61,44),(7,29,77,68,46)],
             "Q":[(40,41,42,43,44),(45,46,47,48,49),(0,31,64,100,53),(1,32,60,101,54),(8,39,67,108,56)],
             "R":[(50,51,52,53,54),(55,56,57,58,59),(1,41,104,90,13),(2,42,100,91,14),(9,49,107,98,16)],
             "B":[(60,61,62,63,64),(65,66,67,68,69),(112,101,44,30,73),(113,102,40,31,74),(115,109,47,38,76)],
             "X":[(70,71,72,73,74),(75,76,77,78,79),(113,61,34,20,83),(114,62,30,21,84),(116,69,37,28,86)],
             "G":[(80,81,82,83,84),(85,86,87,88,89),(114,71,24,10,93),(110,72,20,11,94),(117,79,27,18,96)],
             "H":[(90,91,92,93,94),(95,96,97,98,99),(110,81,14,50,103),(111,82,10,51,104),(118,89,17,58,106)],
             "Y":[(100,101,102,103,104),(105,106,107,108,109),(111,91,54,40,63),(112,92,50,41,64),(119,99,57,48,66)],
             "D":[(110,111,112,113,114),(115,116,117,118,119),(62,72,82,92,102),(63,73,83,93,103),(65,75,85,95,105)]}
             
        self.move = {}

        for k in K:
            A=np.arange(120,dtype = 'i')
            for T in K[k]:
                for i in range(5):
                    A[T[i]] = T[(i - 1) % 5]


            self.move[k + '+ '] = A.copy()
            self.move[k + '++'] = self.move[k + '+ '][A].copy()
            self.move[k + '- '] = np.argsort(self.move[k + '+ '])
            self.move[k + '--'] = np.argsort(self.move[k + '++'])

    
        




        self.edge_key = {'UF': 0,'FU': 1,'UL': 2,'LU': 3,
                         'UP': 4,'PU': 5,'UQ': 6,'QU': 7,
                         'UR': 8,'RU': 9,'FL':10,'LF':11,
                         'LP':12,'PL':13,'PQ':14,'QP':15,
                         'QR':16,'RQ':17,'RF':18,'FR':19,
                         'FG':20,'GF':21,'GL':22,'LG':23,
                         'LX':24,'XL':25,'XP':26,'PX':27,
                         'PB':28,'BP':29,'BQ':30,'QB':31,
                         'QY':32,'YQ':33,'YR':34,'RY':35,
                         'RH':36,'HR':37,'HF':38,'FH':39,
                         'BX':40,'XB':41,'XG':42,'GX':43,
                         'GH':44,'HG':45,'HY':46,'YH':47,
                         'YB':48,'BY':49,'DB':50,'BD':51,
                         'DX':52,'XD':53,'DG':54,'GD':55,
                         'DH':56,'HD':57,'DY':58,'YD':59}

        self.corner_key = {'UPQ': 0,'PQU': 1,'QUP': 2,
                           'UQR': 3,'QRU': 4,'RUQ': 5,
                           'URF': 6,'RFU': 7,'FUR': 8,
                           'UFL': 9,'FLU':10,'LUF':11,
                           'ULP':12,'LPU':13,'PUL':13,
                           'FHG':15,'HGF':16,'GFH':17,
                           'GLF':18,'LFG':19,'FGL':20,
                           'LGX':21,'GXL':22,'XLG':23,
                           'XPL':24,'PLX':25,'LXP':26,
                           'PXB':27,'XBP':28,'BPX':29,
                           'BQP':30,'QPB':31,'PBQ':32,
                           'QBY':33,'BYQ':34,'YQB':35,
                           'YRQ':36,'RQY':37,'QYR':38,
                           'RYH':39,'YHR':40,'HRY':41,
                           'HFR':42,'FRH':43,'RHF':44,
                           'DGH':45,'GHD':46,'HDG':47,
                           'DHY':48,'HYD':49,'YDH':50,
                           'DYB':51,'YBD':52,'BDY':53,
                           'DBX':54,'BXD':55,'XDB':56,
                           'DXG':57,'XGD':58,'GDX':59}


        self.edge_index = [(5,15),(6,25),(7,35),(8,45),(9,55),
                           (19,26),(29,36),(39,46),(49,56),(59,16),
                           (18,88),(87,27),(28,78),(77,37),(38,68),
                           (67,47),(48,108),(107,57),(58,98),(97,17),
                           (69,76),(79,86),(89,96),(99,106),(109,66),
                           (115,65),(116,75),(117,85),(118,95),(119,105)]
        self.corner_index = [(0,32,43),(1,42,53),(2,52,13),(3,12,23),(4,22,33),
                             (10,94,81),(80,24,11),(20,84,71),(70,34,21),(30,74,61),
                             (60,44,31),(40,64,101),(100,54,41),(50,104,91),(90,14,51),
                             (110,82,93),(111,92,103),(112,102,63),(113,62,73),(114,72,83)]

        self.ips = 3000
        
        self.perfect_data = self.makedata()
                         

        X = np.zeros((1,self.ips),dtype = 'f')
        perfect_x = self.makedata()
        self.group_val = {}
        self.total_val = {}

        Y = X.copy()
        Y[0,:1200] = perfect_x[:1200]
        self.group_val['A'] = Y
        Y = X.copy()
        Y[0,1200:] = perfect_x[1200:]
        self.group_val['B'] = Y


        for key in ['A','B']:
            self.total_val[key] = np.sum(self.group_val[key])
        
        
        self.myperms_dict = {}

        self.default_color = {}

        for x in self.edge_index:
            self.default_color[x] = self.state_0[x[0]] + self.state_0[x[1]]
        
        for x in self.corner_index:
            self.default_color[x] = self.state_0[x[0]] + self.state_0[x[1]] + self.state_0[x[2]]

    
        self.num_to_piece = {}
    
        for i in range(120):
            if i % 10 < 5:
                self.num_to_piece[i] = [x for x in self.corner_index if i in x][0]
            else:
                self.num_to_piece[i] = [x for x in self.edge_index if i in x][0]


        for x in self.edge_index:
            for c in self.edge_key:
                if self.default_color[x] != c:
                    self.myperms_dict[(x,c)] = []


        for x in self.corner_index:
            for c in self.corner_key:
                if self.default_color[x] != c:
                    self.myperms_dict[(x,c)] = []


        
        
        for key in self.myperms.keys():
            X = self.myperms[key]
            for m in self.invert_moves(X):
                self.make_move(m)

            for x in self.edge_index:
                c = self.state[x[0]] + self.state[x[1]]
                if c != self.default_color[x]:
                    self.myperms_dict[(x,c)].append(key)

            for x in self.corner_index:
                c = self.state[x[0]] + self.state[x[1]] + self.state[x[2]]
                if c != self.default_color[x]:
                    self.myperms_dict[(x,c)].append(key)      

            for m in X:
                self.make_move(m)


        self.myperms_order = {}
        
        self.myperms_order['A'] = [i for i in range(119,-1,-1) if i % 10 < 5]
        self.myperms_order['B'] = [i for i in range(119,-1,-1) if i % 10 >= 5]                
        
    

    def create_new_set(self):
        i = len(self.my_scrambles2.keys())
        self.my_scrambles2[i] = {}
        for k in self.my_scrambles2[0].keys():
            self.my_scrambles2[i][k] = set([]) 

    def make_move(self,key):
        self.state = self.state[self.move[key]]


    def scramble(self,N,Move = None,difficult_mode = False,scramble_mode = None,flip = None,rotate = None,swap = False,add_moves = False):
        if Move != None:
            for m in Move:
                self.make_move(m)

            return tuple(Move)
        else:
            move_lis = []



            Count = heapdict()
            for k in self.move_keys:
                Count[k] = 0


            transform_idx = random.choice([0,1,4,6,17,2,7,10,22,33])
            #transform_idx = random.randint(0,119)
            #transform_idx = 0
        
            for i in range(N):
                S = set([])
                if i == 0:
                    for key in self.move_keys:
                        S |= self.my_scrambles2[0][key]


                    M = random.choice(list(S))
                    
                

                    
                else:
                    if add_moves:
                        S = self.my_scrambles2[i][next_move]

                        top_V = -1
                        M = ()
                        for s in S:
                            V = 0
                            for m in s:
                                V += Count[m]

                            if top_V < V:
                                top_V = V
                                M = s

                        #print(top_V,M)

                            

                    else:
                        S = self.my_scrambles2[i][next_move]

                        top_V = 1.0e+8
                        M = ()
                        for s in S:
                            V = 0
                            for m in s:
                                V += Count[m]
        
                            if top_V > V:
                                top_V = V
                                M = s
                        #print(top_V,M)


                    

                for m in M:
                    for key in self.move_keys:
                        if key == m:
                            Count[key] += 1


                
                
                #if add_moves:
                #    next_move = Count.peekitem()[0]
                    
                if len(M) > 0:
                    next_move = self.invert_str(M[0])
                M = self.transform(M,transform_idx)
                move_lis += list(M)
                for m in M:
                    self.make_move(m)

                
            if False:
                next_move = Count.peekitem()[0]
                axis = self.axis[next_move[1]]
                n1 = random.choice([m for m in self.move_keys if self.axis[m[1]] != axis])
                #n2 = random.choice([m for m in self.move_keys if self.axis[m[1]] != axis and self.axis[m[1]] != self.axis[n1[1]]])

                self.make_move(next_move)
                self.make_move(n1)
                #self.make_move(n2)
                
                move_lis += (next_move,n1)
            

                    
         

            return tuple(move_lis)
    



    def flip_moves(self,Moves):
        return tuple([self.flip['UD'][x[0]] + self.inverse[x[1:]] for x in Moves])

    def rotate_moves(self,Moves,axis = None):
        if axis in self.rotate:
            return tuple([self.rotate[axis][x[0]] + x[1:] for x in Moves])
        else:
            return tuple(Moves)


    def invert_str(self,s):
        return s[0] + self.inverse[s[1:]]

    def invert_moves(self,Moves):
        return tuple([self.invert_str(x) for x in Moves[::-1]])



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
        L = ()
        for m in move_lis:
            if len(L) > 0 and L[-1][0] == m[0]:
                k = self.mult[L[-1][1:],m[1:]]
                L = L[:-1]
                if k != 0:
                    L += (m[0] + k,)
            else:
                L += (m,)

        return L

    def conjugate(self,A,B):
        return self.simplify(A + B + self.invert_moves(A))

    def commutator(self,A,B):
        return self.simplify(A + B + self.invert_moves(A) + self.invert_moves(B))
        
    def reset(self):
        self.state[:] = self.state_0

    def makedata(self):
        x = np.zeros(self.ips,dtype = 'f')
        idx = 0
        for p in self.corner_index:
            s = self.state[p[0]] + self.state[p[1]] + self.state[p[2]]
            x[60*idx + self.corner_key[s]] = 1
            idx += 1
        
        for p in self.edge_index:
            s = self.state[p[0]] + self.state[p[1]]
            x[60*idx + self.edge_key[s]] = 1
            idx += 1

        return x

    def is_perfect(self):
        return (self.state == self.state_0).all()


    def transform(self,s,i):
        key = self.transformation_keys[i]
        New_s = tuple(s)
        for x in key:
            if x == 'F':
                New_s = self.flip_moves(New_s)
            else:
                New_s = self.rotate_moves(New_s,axis = self.transformation_dict[x.swapcase()])


        return New_s

    def make_transformations(self,s,Moves):
        s_list = []
        Moves_list = []
        for key in self.transformation_keys:
            New_s = tuple(s)
            New_Moves = tuple(Moves)
            for x in key[::-1]:
                if x == 'F':
                    New_s = self.flip_moves(New_s)
                    New_Moves = self.flip_moves(New_Moves)
                else:
                    New_s = self.rotate_moves(New_s,axis = self.transformation_dict[x])
                    New_Moves = self.rotate_moves(New_Moves,axis = self.transformation_dict[x])


            s_list.append(New_s)
            Moves_list.append(New_Moves)
        
                    


        return s_list,Moves_list


    def state_to_str(self):
        return reduce(lambda x,y : x+y , self.state)

    def set_state(self,S):
        if len(S) == 12 * self.surface_num:
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


def cross_entropy(y,t):
    return -np.sum(t * np.where(y != 0 , np.log(y),-100))



        

class Softmax_Cross_Entropy:
    def __init__(self):
        self.x = np.zeros(0,dtype = 'f')
        self.y = np.zeros(0,dtype = 'f')
        self.t = np.zeros(0,dtype = 'f')
        self.Indices = None

    def forward(self,x,args,rewards,Indices):
        self.Indices = Indices
        self.x = x
        self.y = np.zeros((self.x.shape[0],0),dtype = 'i')
        self.t = np.zeros((self.x.shape[0],0),dtype = 'i')
        for i in range(len(Indices) - 1):
            self.y = np.c_[self.y,softmax(x[:,Indices[i]:Indices[i+1]-1])]

        self.t = np.zeros_like(self.y,dtype = 'f')
        self.t[args,np.arange(self.t.shape[1])] = 1

        return cross_entropy(self.y,self.t)

    def backward(self):
        dO = np.zeros_like(self.x)
        for i in range(len(self.Indices) -1):
            dO[:,self.Indices[i]:self.Indices[i+1] - 1] = self.y[:,self.Indices[i] - i:self.Indices[i+1] - i - 1] - self.t[:,self.Indices[i] - i:self.Indices[i+1] - i - 1]
        return dO

class Myloss:
    def __init__(self):
        self.y = np.zeros(0,dtype = 'f')
        self.t = np.zeros(0,dtype = 'f')

    def forward(self,x,Indices):
        #self.y = sigmoid(x[:,:-1] - x[0,-1])

        self.y = np.zeros((1,Indices[-1]),dtype = 'f')
        self.t = np.zeros((1,Indices[-1]),dtype = 'f')
        for i in range(len(Indices) - 1):
            self.y[:,Indices[i]:Indices[i+1]] = softmax_H(x[:,Indices[i]:Indices[i+1]])
            self.t[0,Indices[i+1]-1] = 1.0

        

        #return np.sum(self.y)

        return cross_entropy(self.y,self.t)

    def backward(self):
        #dO = np.zeros((1,self.y.shape[1] + 1),dtype = 'f')
        #dO[:,:-1] += self.y * (1 - self.y)
        
        #dO[0,-1] = -np.sum(dO[:,:-1])


        #return dO

        return self.y - self.t
        

class Batch_Normalization:
    def __init__(self,size):
        self.size = size
        self.m = np.zeros(size,dtype = 'f')
        self.s = np.ones(size,dtype = 'f')
        self.g = np.ones(size,dtype = 'f')
        self.b = np.zeros(size,dtype = 'f')
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
        

class Rubiks_3_AI:
    def __init__(self,Mid,cube_size = 3,Activation = 'ReLU',cube = None,Batch_Normalize = False):
        if cube == None:
            self.cube = Rubiks_3()
        else:
            self.cube = cube
        #self.ips = 36 * self.cube.surface_num
        self.Batch_Normalize = Batch_Normalize
        self.ips = self.cube.ips
        self.ops = self.cube.move_len
        self.Mid = Mid

        self.skip_search = False
        




        self.myval = False
        self.weight_decay = False
        self.cube_size = cube_size
        self.surface_num = self.cube.surface_num







        self.layers = OrderedDict()
        self.params = {}
        self.indices = []
        
        
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
        #self.g = 0.95
        self.wdlr = 1.0e-6
        self.PV_ratio = 1
        self.lr_C = 1
        self.out_C = 1.0
        self.lr_v = 0.99
        self.lr_h = 0.99

        #self.losslayer = Q_loss(self.g)
        self.losslayer = Softmax_Cross_Entropy()
        self.losslayer2 = Myloss()




        self.scramble_num = 3
        self.scramble_num_min = 2
        self.solve_num = 30
        self.datas = []


        self.myperms = {}
        self.nodes = {}
        self.search_num = 10000
        self.perfect_val = 1.0
        self.set_perfect_val()
        
        
        


    def set_perfect_val(self):
        self.perfect_val = self.predict(self.cube.perfect_data.reshape(-1,1),False,True)[0][0]

            
        
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
        self.predict(x,policy = False,value = True,loss = False)

        if layer == "WO_V":
            dO = np.ones((1,x.shape[1]),dtype = 'f')
            dO = self.value_layer.backward(dO)
            dO = self.value_act.backward(dO)
            dO = self.value_mid.backward(dO)

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
        Indices = [0]
        N = 0
        for d in d_Lis: 
            N += len(d.moves) + 1
            Indices.append(N)

        args = np.zeros(N - len(d_Lis),dtype = 'i')
        x = np.zeros((self.ips,N))
        
        N_args = 0
        N_x = 0
        
        for d in d_Lis:
            scramble = self.cube.transform(d.scramble,transformation)
            moves = self.cube.transform(d.moves,transformation)
            
            self.cube.reset()
            self.cube.scramble(0,scramble)
            args[N_args:N_args + len(moves)] = np.array([self.cube.key_to_num[m] for m in moves])
            x[:,N_x] = self.cube.makedata()
            i = 1
            for m in moves:
                self.cube.make_move(m)
                x[:,N_x + i] = self.cube.makedata()
                i += 1
            
            

            N_x += len(moves) + 1
            N_args += len(moves)

            
            


        out = self.predict(x,policy = True,value = True,loss = True)


        l = self.losslayer.forward(out[:-1],args,np.zeros(0),Indices)
        l2 = self.losslayer2.forward(out[-1:],Indices)
        

        return (l,l2)

                        



                        

    def learn(self,transformation = 0,flip_inside = False):
        err = 0
        err2 = 0
        DP = 0.0
        DV = 0.0
        D1 = 0.0
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
            d_lis = [self.datas[n] for n in self.indices[i*Batch_Size:(i+1)*Batch_Size]]
            
            L = self.loss(d_lis,transformation = transformation,flip_inside = flip_inside)
            L0 = L[0] / len(d_lis)
            L1 = L[1] / len(d_lis)
            if L0 > l0_max:
                l0_max = L0
            if L1 > l1_max:
                l1_max = L1
                l1_indices = self.indices[i*Batch_Size:(i+1)*Batch_Size].copy()
                
            err += L0
            err2 += L1
            #print(L0,L1)
            if L0 > 1.0 or L1 > 0.01:
                #if True:
                new_indices += self.indices[i*Batch_Size:(i+1)*Batch_Size]
        
            dO = self.losslayer.backward()
            dO = self.policy_layer.backward(dO)
            
            dO = self.policy_act.backward(dO)
            if self.Batch_Normalize:
                dO = self.policy_BN.backward(dO)
            dO = self.policy_mid.backward(dO)

            
            dO2 = self.losslayer2.backward() * self.PV_ratio
            dO2 = self.value_layer.backward(dO2)
            dO2 = self.value_act.backward(dO2)
            if self.Batch_Normalize:
                dO2 = self.value_BN.backward(dO2)
            dO2 = self.value_mid.backward(dO2)

            #print(np.sum(dO ** 2),np.sum(dO2 ** 2))
            dO += dO2




            reverse_key = list(self.layers)
            reverse_key.reverse()
            for key in reverse_key:
                dO = self.layers[key].backward(dO)




            #if self.weight_decay:
                #self.params['WO_P'] -= self.wdlr * self.params['WO_P']               
                #self.params['WM_P'] -= self.wdlr * self.params['WM_P']
                #self.params['WO_V'] -= self.wdlr * self.params['WO_V']               
                #self.params['WM_V'] -= self.wdlr * self.params['WM_V']            
            
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






            for key in self.affines:
                if self.weight_decay:
                    self.params['W' + key[-1]] -= self.wdlr * self.params['W' + key[-1]]
                
                self.v['W' + key[-1]] += self.lr * self.layers[key].dW
                self.v['B' + key[-1]] += self.lr * self.layers[key].dB

                
                self.h['W' + key[-1]] += self.layers[key].dW ** 2
                self.h['B' + key[-1]] += self.layers[key].dB ** 2


            for key in self.BNs:
                self.v['BNg' + key[-1]] += self.lr * self.layers[key].dg
                self.v['BNb' + key[-1]] += self.lr * self.layers[key].db



            for key in self.v.keys():
                self.params[key] -= self.v[key] / (np.sqrt(self.h[key]) + 1)
                self.v[key] *= self.lr_v
                self.h[key] *= self.lr_h


        self.indices = new_indices + self.indices[Batch_Size * Epoch_Num:]
        #random.shuffle(self.indices)
        
        self.set_perfect_val()
        self.lr_C = min(1,err/Len/10)


        if Epoch_Num == 0:
            return (0,0,0,0,0)
        elif self.Batch_Normalize:
            for key in self.BNs:
                #if self.layers[key].N >= 100:
                self.layers[key].set_ms()
                
            self.policy_BN.set_ms()
            self.value_BN.set_ms()
                


        for key in self.v.keys():
            if key[0] == "W":
                print(key + ":" + str(np.log10(np.average(self.v[key] ** 2 / (self.h[key] + 1)))) + ",",str(np.max(self.h[key])))


        return (err / Epoch_Num,err2 / Epoch_Num,len(self.indices),Len)

                
            
        

    def search2(self,N):
        Vals = {}
        P_unsearched = heapdict()
        P_unsearched[()] = -N * 2
        Continue_Searching = True
        topval = -1000000000
        topkey = ()
        Counter = np.zeros(2,dtype = 'i')
        L = len(self.cube.move_keys)
        while Continue_Searching:
            n = min(len(P_unsearched),100)
            Z = []
            for i in range(n):
                Z.append(P_unsearched.popitem())

            
            keylis = [z[0] for z in Z]
            
            X = np.zeros((self.ips,n))
            RP = np.zeros(n)
            Mask = np.zeros((L,n),dtype = bool)
            for i in range(n):
                key = keylis[i]
                for m in key:
                    self.cube.make_move(m)

                if len(key) > 0:
                    removed = {self.cube.invert_str(key[-1])}
                else:
                    removed = set([])

                F = filter(lambda m: m[:2] in removed,self.cube.move_keys)
                for m in F:
                    im = self.cube.move_keys.index(m)
                    Mask[im,i] = True
                    #print(m,key)

                if self.cube.is_perfect():
                    for m in self.cube.invert_moves(key):
                        self.cube.make_move(m)
                    topval = self.perfect_val
                    topkey = key
                    
                    val_lis = []
                    for j in range(len(topkey)):
                        val_lis.append(Vals[topkey[:j]])

                    val_lis.append(self.perfect_val)

                    return (True,topkey,self.perfect_val,val_lis,0,Counter)

                    

                
                x = self.cube.makedata().reshape(-1)
                X[:,i] = x
                RP[i] = -Z[i][1]

                for m in self.cube.invert_moves(key):
                    self.cube.make_move(m)

                
            out = self.predict(X,policy = True,value = True)

            V = out[-1].reshape(-1)
            P = out[:-1]
            #print(P)
            P[Mask] = -10000
            P = softmax(P) * RP
            W = np.where(P >= 1)
            #print(P[Mask])
            for i in range(n):
                key = keylis[i]
                Vals[key] = V[i]
                if key == ():
                    root_val = V[i]
                    topval = root_val + 0.0001
                    topkey = ()


                V2 = V[i]
                if V2 > topval:
                    topval = V2
                    topkey = key

                if V2 > root_val + 0.0001:
                    Counter[0] += 1

                Counter[1] += 1

                #if topval > root_val + 5 and len(topkey) >= 8 and self.skip_search:
                if (len(topkey) >= 1 and V2 > root_val + 1 and self.skip_search) or (Counter[1] >= N and Counter[0] > 0):
                    val_lis = []
                    for j in range(len(topkey) + 1):
                        val_lis.append(Vals[topkey[:j]])



                    return (False,topkey,Vals[topkey],val_lis,0,Counter)                    
                    


            for w in zip(W[0],W[1]):
                #if len(keylis[w[1]]) < 200 and Vals[keylis[w[1]]] <= root_val:
                if len(keylis[w[1]]) < 200:
                #if len(keylis[w[1]]) < 8 or (len(keylis[w[1]]) < 200 and Vals[keylis[w[1]]] <= root_val):
                    P_unsearched[keylis[w[1]] + (self.cube.move_keys[w[0]],)] = -P[w[0],w[1]]
                    #print(keylis[w[1]] , (self.cube.move_keys[w[0]],),P[w[0],w[1]])

            Continue_Searching = (len(P_unsearched) > 0)
            #Continue_Searching = (Counter[1] <= N and len(P_unsearched) > 0)



        for m in topkey:
            self.cube.make_move(m)

        is_perfect = self.cube.is_perfect()

        for m in self.cube.invert_moves(topkey):
            self.cube.make_move(m)


        val_lis = []
        for j in range(len(topkey) + 1):
            val_lis.append(Vals[topkey[:j]])


        return (is_perfect,topkey,Vals[topkey],val_lis,0,Counter)
                
                
            
            
            

            
        
        

class Node:
    def __init__(self,P):
        self.P = P
        self.val = np.zeros_like(P,dtype = 'f')
        self.visited = np.zeros_like(P,dtype = 'i')
        self.S = 0
        self.C = 2.0
        

    def select_node(self):
        if self.S == 0:
            return np.argmax(self.P)
        else:
            return np.argmax(np.where(self.visited != 0,self.val / self.visited,perfect_val) + self.C * self.P * np.sqrt(self.S) / (1 + self.visited))




def ffffffffff():
    for i in range(10000):
        F.cube.makedata()

if __name__ == '__main__':
    F = Frame()
    F.pack()
