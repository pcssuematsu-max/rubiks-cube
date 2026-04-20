"""Rubiks cube model and move/state utilities."""

import random
from functools import reduce

import numpy as np
from heapdict import heapdict

from core.cube_constants import AB, R_Nums
from cube.move_sequence_ops import MoveSequenceOps


def _build_group_indices_by_size():
    """cube size ごとの group index 定義を返す。"""
    return {
        2: {'A':list(range(4)),'B':[],'C':[],'c':[],'D':[],'d':[],'E':[],'e':[],'F':[],'f':[],'G':[]},
        3: {'A':list(range(4)),'B':list(range(4,8)),'C':[],'c':[],'D':[],'d':[],'E':[],'e':[],'F':[],'f':[],'G':[8]},
        4: {'A':list(range(4)),'B':[],'C':list(range(4,12)),'c':[],'D':list(range(12,16)),'d':[],'E':[],'e':[],'F':[],'f':[],'G':[]},
        5: {'A':list(range(4)),'B':list(range(4,8)),'C':list(range(8,16)),'c':[],'D':list(range(16,20)),'d':[],'E':list(range(20,24)),'e':[],'F':[],'f':[],'G':[24]},
        6: {'A':list(range(4)),'B':[],'C':[4,5,6,7,8,9,10,11],'c':[12,13,14,15,16,17,18,19],'D':[20,21,22,23],'d':[32,33,34,35],'E':[],'e':[],'F':[24,25,26,27],'f':[28,29,30,31],'G':[]},
        7: {'A':list(range(4)),'B':list(range(4,8)),'C':[8,9,10,11,12,13,14,15],'c':[16,17,18,19,20,21,22,23],'D':[24,25,26,27],'d':[40,41,42,43],'E':[28,29,30,31],'e':[44,45,46,47],'F':[32,33,34,35],'f':[36,37,38,39],'G':[48]},
    }


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
        self._init_move_symbol_tables()
        self._init_symmetry_tables()
        self._init_transformation_tables()

        self.move_ops = MoveSequenceOps(self)
        
        self._init_myperm_containers()
        self._register_myperms2()
        self._expand_registered_myperms()

        self._init_cube_state_and_moves()
        self._init_color_keys_and_groups()
        self._init_myperms_index()
        self._init_single_move_and_rotate()


    def _init_move_symbol_tables(self):
        """手の反対面・逆回転・合成結果などの基本表を初期化する。"""
        self.opposite = {"U":"D","D":"U","F":"B","B":"F","L":"R","R":"L","M":"M","S":"S","E":"E","x":"x","y":"y","z":"z"}
        self.inverse = {" ":"'","'":" ","2":"2"}
        self.mult = {(" "," "):"2",(" ","2"):"'",(" ","'"):0,
                     ("2"," "):"'",("2","2"):0,("2","'"):" ",
                     ("'"," "):0,("'","2"):" ",("'","'"):"2"}
        self.axis = {"L":"x","R":"x","M":"x","U":"y","D":"y","E":"y","F":"z","B":"z","S":"z"}

    def _init_symmetry_tables(self):
        """鏡映・回転・対角反転の move table を初期化する。"""
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

    def _init_transformation_tables(self):
        """対称変換の列挙と逆変換表を初期化する。"""
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

    def _init_myperm_containers(self):
        """myperm登録用の辞書とグループ情報を初期化する。"""
        self.myperms = {}
        self.myperms2 = {}
        self._init_group_indices()

    def _init_group_indices(self):
        """group index 定義を読み込み、意味名ベースの受け口を作る。"""
        short_group_indices = _build_group_indices_by_size()[self.size]
        group_names = self._group_name_map()
        self.group_indices = {}
        for short_key, indices in short_group_indices.items():
            index_list = list(indices)
            self.group_indices[short_key] = index_list
            self.group_indices[group_names[short_key]] = index_list


    def _register_myperms2(self):
        """myperms2へ固定手順と派生手順を登録する。"""
        self._register_myperms2_base()
        self._register_myperms2_x_perms()
        self._register_myperms2_odd_size()
        self._register_myperms2_general()
        self._register_myperms2_f2l_oll()

    def _register_myperms2_base(self):
        """基本パターンと大分類の手順を登録する。"""
        # 命名メモ:
        # - SingleMove-* は1手だけ回す補助手順。
        # - X-Center / Plus-Center / Oblique-Center は動かす center の配置族。
        # - 4 / 6 は見た目上で動く center 数、末尾の英字は variant を表す。
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
        self.myperms2['BigQG'] = (' F ', " L'", " U'", ' F ', ' U ', ' F2', " R'", ' F ', " D'", " B'", ' D ', " B'", ' F ', " L'", ' B ', ' L ', ' B ', ' F2', ' R ', " F'", " B'", ' F2', " z'", ' L ', ' D ', " F'", " D'", ' F ')
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
        # 命名メモ:
        # - ParitySwap-* は corner 2つ + midedge 2つの同時 swap。
        # - ParityCycle-* は corner 4つ + edge 2つの置換。
        # - A/B/F/J/K は corner 配置 family、末尾番号は family 内 variant。
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
        # 命名メモ:
        # - CenterMidEdgeSwap-P,Q* は center 4つの cycle と midedge 2つの swap。
        # - CenterMidEdgeSwap-R,S* は center 6つ((2,2,2)-cycle)と midedge 2つの swap。
        # - CenterCornerSwap-* は center 4つの cycle と corner 2つの swap。
        # - Q/P/R は配置 family、末尾の英字や番号は向き違い・variant。
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


            self.myperms2['CenterMidEdgeSwap-SA'] = (' S ', ' D ', ' S ', " D'", ' S ', " D'", ' S ', ' D ', ' S2', " D'", ' S ', ' D2', ' L2', " S'", " D'", " S'", ' D ', ' L2', " D'"," M'"," S2"," M "," S2")
            self.myperms2['CenterMidEdgeSwap-SB'] = (' S ', " D'", ' S ', ' D2', ' L2', " D'", ' S ', " D'", ' S ', ' D2', ' L2', " D'", ' S '," M'"," S2"," M "," S2")
            self.myperms2['CenterMidEdgeSwap-SC(0)'] = (' R2', " S'", ' R2', ' S2', " U'", ' S ', ' U ', ' S ', ' U ', ' S ', " U'", ' S2', ' D ', ' M ', ' D2', " M'", ' D ', " S'"," M'"," S2"," M "," S2")
            self.myperms2['CenterMidEdgeSwap-SD(0)'] = (' R2', " S'", ' R2', ' S2', " U'", ' R2', ' S ', ' U ', ' S ', ' U ', ' S ', " U'", ' S ', " U'", ' R2', ' U '," M'"," S2"," M "," S2")
            self.myperms2['CenterMidEdgeSwap-SE(0)'] = (' S ', " D'", ' S ', ' D ', ' S ', ' D ', ' S ', " D'", ' S ', ' M ', ' U ', ' M ', ' U2', " M'", ' U ', " M2"," S2"," M "," S2")
            self.myperms2['CenterMidEdgeSwap-SF(0)'] = (' S ', ' D ', ' S ', ' D2', ' L2', ' D ', ' S ', ' D ', ' S ', " D'", ' S ', " D'", ' L2', ' D '," M'"," S2"," M "," S2")
            self.myperms2['CenterMidEdgeSwap-SG(0)'] = (' S ', ' R ', ' S ', " R'", ' S ', " R'", ' L2', ' S ', ' R ', ' L2', ' S2', " R'", ' U2', ' R ', " S'", " R'", ' U2', ' R '," M'"," S2"," M "," S2")
            self.myperms2['CenterMidEdgeSwap-SH(0)'] = (" L'", " S'", ' L ', " S'", " L'", " S'", " L'", " S'", ' L ', " S'", ' L ', " E'", ' S2', ' E ', ' S ', ' R2', ' S ', ' R2')

            self.myperms2['CenterMidEdgeSwap-SC(1)'] = (' R2', " S'", ' R2', ' S2', " U'", ' S ', ' U ', ' S ', ' U ', ' S ', " U'", ' S2', ' D ', ' M ', ' D2', " M'", ' D ', " S'"," E "," S2"," E'"," S2")
            self.myperms2['CenterMidEdgeSwap-SD(1)'] = (' R2', " S'", ' R2', ' S2', " U'", ' R2', ' S ', ' U ', ' S ', ' U ', ' S ', " U'", ' S ', " U'", ' R2', ' U '," E "," S2"," E'"," S2")
            self.myperms2['CenterMidEdgeSwap-SE(1)'] = (' S ', " D'", ' S ', ' D ', ' S ', ' D ', ' S ', " D'", ' S ', ' M ', ' U ', ' M ', ' U2', " M'", ' U ', " M'"," E "," S2"," E'"," S2")
            self.myperms2['CenterMidEdgeSwap-SF(1)'] = (' S ', ' D ', ' S ', ' D2', ' L2', ' D ', ' S ', ' D ', ' S ', " D'", ' S ', " D'", ' L2', ' D '," E "," S2"," E'"," S2")
            self.myperms2['CenterMidEdgeSwap-SG(1)'] = (' S ', ' R ', ' S ', " R'", ' S ', " R'", ' L2', ' S ', ' R ', ' L2', ' S2', " R'", ' U2', ' R ', " S'", " R'", ' U2', ' R '," E "," S2"," E'"," S2")
            self.myperms2['CenterMidEdgeSwap-SH(1)'] = (" L'", " S'", ' L ', " S'", " L'", " S'", " L'", " S'", ' L ', " S'", ' L ', " M'", ' S2', ' M ', ' S ', ' R2', ' S ', ' R2')
            
            self.myperms2['CenterMidEdgeSwap-RA'] = (" S'", " U'", " S'", ' U ', " S'", ' U ', " S'", " U'", ' S2', ' U ', ' R2', " U'", ' S ', ' U ', " S'", ' R2', ' U2', ' S ', ' U '," M'"," S2"," M "," S2")
            self.myperms2['CenterMidEdgeSwap-RB'] = (" E'", " M'", ' E ', ' D ', " M'", ' D2', ' F2', ' D ', " M'", ' D ', " M'", ' D2', ' F2', ' D ', " M2"," S2"," M "," S2")
            self.myperms2['CenterMidEdgeSwap-RX'] = (" E'", ' B ', " E'", " B'", " E'", " B'", " E'", ' B ', ' M ', " E'", " F'", ' M ', ' F2', ' D2', " M'", " F'", " M'", ' F ', ' D2', " F'"," M'"," S2"," M "," S2")
            self.myperms2['CenterMidEdgeSwap-RY'] = (' E ', ' R2', " E'", ' R ', " S'", ' L ', " S'", " L'", " S'", " L'", " S'", ' L ', " S'", ' R '," M'"," S2"," M "," S2")
            self.myperms2['CenterMidEdgeSwap-RC(0)'] = (' R ', " S'", ' U ', " S'", " U'", ' S ', ' U2', " S'", ' U2', " S'", " U'", " S'", ' U ', ' S2', ' R2', ' S ', ' R '," M'"," S2"," M "," S2")
            self.myperms2['CenterMidEdgeSwap-RD(0)'] = (" F'", ' U2', ' F ', ' M ', ' F ', ' M ', " F'", ' M ', " F'", ' M ', ' U2', ' F ', ' E ', ' M ', " E'", ' M ', ' U2', " M'", ' U2'," M'"," S2"," M "," S2")
            self.myperms2['CenterMidEdgeSwap-RE(0)'] = (' M ', " E'", " M'", ' F ', " E'", " F'", " E'", " F'", " E'", ' F ', " E'", " M'", " B'", " M'", ' B2', ' M ', " B'", " S2"," M "," S2")
            self.myperms2['CenterMidEdgeSwap-RF(0)'] = (' M ', " E'", " M'", ' F ', " E'", " F'", " E'", " F'", " E'", ' F ', " E'", ' B ', ' M ', ' B2', " M'", ' B '," M'"," S2"," M "," S2")
            self.myperms2['CenterMidEdgeSwap-RG(0)'] = (" D'", " S'", ' U ', " S'", " U'", " S'", " U'", " S'", ' U ', " S'", " D'", " M'", " F'", " M'", ' F ', ' D2', " F'", ' M ', ' F ', " S2"," M "," S2")
            self.myperms2['CenterMidEdgeSwap-RH(0)'] = (" D'", " S'", ' U ', " S'", " U'", " S'", " U'", " S'", ' U ', " S'", ' D ', ' M ', ' D2', " M'", ' D2'," M'"," S2"," M "," S2")
            self.myperms2['CenterMidEdgeSwap-RC(1)'] = (' R ', " S'", ' U ', " S'", " U'", ' S ', ' U2', " S'", ' U2', " S'", " U'", " S'", ' U ', ' S2', ' R2', ' S ', ' R '," E "," S2"," E'"," S2")
            self.myperms2['CenterMidEdgeSwap-RD(1)'] = (" F'", ' U2', ' F ', ' M ', ' F ', ' M ', " F'", ' M ', " F'", ' M ', ' U2', ' F ', ' E ', ' M ', " E'", ' M ', ' U2', " M'", ' U2'," E "," S2"," E'"," S2")
            self.myperms2['CenterMidEdgeSwap-RE(1)'] = (' M ', " E'", " M'", ' F ', " E'", " F'", " E'", " F'", " E'", ' F ', " E'", " M'", " B'", " M'", ' B2', ' M ', " B'", ' M '," E "," S2"," E'"," S2")
            self.myperms2['CenterMidEdgeSwap-RF(1)'] = (' M ', " E'", " M'", ' F ', " E'", " F'", " E'", " F'", " E'", ' F ', " E'", ' B ', ' M ', ' B2', " M'", ' B '," E "," S2"," E'"," S2")




            self.myperms2['CenterCornerSwap-A(0)'] = self.myperms2['ParitySwap-A0-'] + self.myperms2['CenterMidEdgeSwap-QA']
            self.myperms2['CenterCornerSwap-A(1)'] = self.myperms2['ParitySwap-A1-'] + self.myperms2['CenterMidEdgeSwap-QA']
            self.myperms2['CenterCornerSwap-B(0)'] = self.myperms2['ParitySwap-B0-'] + self.myperms2['CenterMidEdgeSwap-QA']
            self.myperms2['CenterCornerSwap-B(1)'] = self.myperms2['ParitySwap-B1-'] + self.myperms2['CenterMidEdgeSwap-QA']
            self.myperms2['CenterCornerSwap-F(0)'] = self.myperms2['ParitySwap-F0-'] + self.myperms2['CenterMidEdgeSwap-QA']
            self.myperms2['CenterCornerSwap-F(1)'] = self.myperms2['ParitySwap-F1-'] + self.myperms2['CenterMidEdgeSwap-QA']           
            self.myperms2['CenterCornerSwap-J(0)'] = self.myperms2['ParitySwap-J0-'] + self.myperms2['CenterMidEdgeSwap-QA']
            self.myperms2['CenterCornerSwap-J(1)'] = self.myperms2['ParitySwap-J1-'] + self.myperms2['CenterMidEdgeSwap-QA']
            self.myperms2['CenterCornerSwap-J(2)'] = self.myperms2['ParitySwap-J2-'] + self.myperms2['CenterMidEdgeSwap-QA']
            self.myperms2['CenterCornerSwap-J(3)'] = self.myperms2['ParitySwap-J3-'] + self.myperms2['CenterMidEdgeSwap-QA']
            self.myperms2['CenterCornerSwap-J(4)'] = self.myperms2['ParitySwap-J4-'] + self.myperms2['CenterMidEdgeSwap-QA']
            self.myperms2['CenterCornerSwap-J(5)'] = self.myperms2['ParitySwap-J5-'] + self.myperms2['CenterMidEdgeSwap-QA']
            self.myperms2['CenterCornerSwap-K(0)'] = self.myperms2['ParitySwap-ZA-'] + self.myperms2['CenterMidEdgeSwap-QA']
            self.myperms2['CenterCornerSwap-K(1)'] = self.myperms2['ParitySwap-ZA-'] + self.myperms2['CenterMidEdgeSwap-QA']

            

    def _register_myperms2_general(self):
        """通常モードで使う汎用手順群を登録する。"""
        self._register_myperms2_classic_perms()
        self._register_myperms2_midedge_general()
        self._register_myperms2_edge_general()
        self._register_myperms2_center_general()

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
        # 命名メモ:
        # - MidEdge3-* は midedge 3個の cycle。
        # - MidEdge4-* は midedge 4個の cycle / 2-2 swap 型。
        # - family 文字は位置関係、末尾 A/B/C... は向き違い。
        # - MidEdgeFlip2/4-* は midedge の flip 用 family。
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
        # 命名メモ:
        # - Wing3Cycle-* は wing 3個の cycle。
        # - Parallel3 / MidEdge3 / Parallel2Plus1 / SameEdgePairPlus1 は
        #   3つの wing の位置関係 family。
        # - WingSwapParallel / WingSwapSkew / WingSwapSkewViaEdge は
        #   wing 2点交換 family。
        # - CornerEdgeBlockSwap-* は corner 2つ + edge block 2つの同時 swap。
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
        

        self.myperms2['CornerEdgeBlockSwap-K00-'] = (' D2', ' L ', ' B ', " L'", ' D2', ' R ', " F'", ' R ', ' F ', ' R2', ' F2', ' D2', ' F ', ' U2', " F'", ' D2', ' F ', ' U2', ' F ')
        self.myperms2['CornerEdgeBlockSwap-K01-'] = (' R2', " D'", ' R ', ' U2', " R'", ' D ', ' R ', ' U2', ' R ', " U'", " L'", ' U ', ' R2', " U'", ' L ', ' U ', ' R2', ' U ', ' R ', " U'", ' R ', ' U ', ' R ', " U'", ' R2')
        self.myperms2['CornerEdgeBlockSwap-K02-'] = (" B'", ' R2', " B'", ' D2', ' L2', ' F2', ' L2', ' D2', ' B ', ' R2', ' D2', " L'", " F'", ' L ', ' D2', " R'", ' B ', ' R ')
        self.myperms2['CornerEdgeBlockSwap-K03-'] = (' B2', ' D ', " B'", ' U2', ' B ', " D'", " B'", ' U2', ' L ', " B'", " U'", ' L ', ' F ', ' U ', ' L2', " U'", ' L ', ' F ', ' L ', " F'", ' L2', ' U ')
        self.myperms2['CornerEdgeBlockSwap-K04-'] = (' U2', ' F ', ' L2', " B'", ' U2', ' B ', ' U2', ' F2', ' L2', " F'", ' L2', ' F ', ' L2', ' U2', ' F2', ' U2', ' B ', ' L2', ' U2', ' R2', ' F ', ' D2', ' R2')
        self.myperms2['CornerEdgeBlockSwap-K05-'] = (' D ', ' R ', " D'", ' U ', ' F2', " U'", ' D ', " R'", ' D2', ' B2', ' D2', " B'", ' D2', ' B ', ' D2', " B'", ' D2', ' R2', " B'", ' R2', " B'", ' D2', ' B2', " D'")
        self.myperms2['CornerEdgeBlockSwap-K06-'] = (' U2', " B'", ' L2', ' F ', ' U2', " F'", ' U2', ' B2', ' L2', ' B ', ' L2', " B'", ' L2', ' U2', ' B2', ' D2', " B'", ' D2', ' R2', ' U2', " F'", ' U2', ' R2')
        self.myperms2['CornerEdgeBlockSwap-K07-'] = (' D ', " R'", ' D ', " U'", ' B2', " D'", ' U ', ' R ', ' D2', ' B2', ' D2', " B'", ' D2', ' B ', ' D2', " B'", ' D2', ' R2', " B'", ' R2', " B'", ' D2', ' B2', " D'")
        self.myperms2['CornerEdgeBlockSwap-K08-'] = (' F2', ' D2', ' B ', ' U2', " B'", ' F ', ' R2', ' L2', ' F ', ' L2', ' D2', ' F ', ' D2', " F'", ' D2', ' F ', ' D2', ' F2', ' D2', ' L2')
        self.myperms2['CornerEdgeBlockSwap-K09-'] = self.conjugate((" L "," R'"),self.myperms2['EZ-H'])


        
        self.myperms2['CornerEdgeBlockSwap-J00-'] = (' L2', ' U2', ' F ', ' U ', " F'", ' U ', ' L2', " D'", ' B ', ' D ')
        self.myperms2['CornerEdgeBlockSwap-J01-'] = (' D2', " R'", " U'", ' R ', ' D2', " R'", ' U ', ' F2', " L'", " U'", ' L ', ' F2', " R'", ' D ', " R'", " D'", " R'")
        self.myperms2['CornerEdgeBlockSwap-J02-'] = (' U ', " B'", ' U ', ' R2', " D'", ' F ', ' D ', ' R2', ' F ', ' U2', ' B ', ' U2', " F'", ' U2')
        self.myperms2['CornerEdgeBlockSwap-J03-'] = (' U2', ' L ', ' D ', " L'", ' U2', ' L ', " D'", ' L2', ' F2', ' R ', ' U ', " R'", ' F2', ' L ', " D'", ' L ', ' D ', " L'")
        self.myperms2['CornerEdgeBlockSwap-J04-'] = (' L2', ' U2', " F'", ' L2', ' D2', ' R2', ' B2', ' D2', ' L2', " U'", " F'", ' U ', ' L2', " D'", ' B ', ' D ')
        self.myperms2['CornerEdgeBlockSwap-J05-'] = (' R2', " D'", " F'", ' D ', ' F ', ' D ', " R'", ' D2', ' F ', ' D ', ' F ', " D'", " F'", ' D ', ' B2', ' L2', ' U ', ' L2', ' B2', ' R2', ' D ', ' R ')
        self.myperms2['CornerEdgeBlockSwap-J06-'] = (" D'", " B'", ' D ', ' L2', " U'", ' F ', ' U ', ' L2', ' D2', ' B ', ' D2', ' U2', ' L2', ' D2', ' F ', ' R2', ' D2', ' L2', ' B ')
        self.myperms2['CornerEdgeBlockSwap-J07-'] = (" L'", ' U2', ' L2', ' R2', " D'", ' L2', ' D ', ' L2', ' R2', " U'", ' L2', " U'", ' L ', ' R ', " D'", ' F ', ' D ', " F'", " D'", " F'", ' D2', ' R ', " D'", " F'", " D'", ' F ', ' D ', ' R2')
        self.myperms2['CornerEdgeBlockSwap-J08-'] = self.conjugate((" F "," B "),self.myperms2['EZ-G'])
        self.myperms2['CornerEdgeBlockSwap-J09-'] = self.conjugate((" L "," R "),self.myperms2['EZ-H'])        
        self.myperms2['CornerEdgeBlockSwap-J10-'] = self.conjugate((" F2",),self.myperms2['EZ-G'])
        self.myperms2['CornerEdgeBlockSwap-J11-'] = self.conjugate((" L2",),self.myperms2['EZ-H'])

        self.myperms2['CornerEdgeBlockSwap-JX'] = (' B2', " L'", ' B2', ' D2', " F'", " R'", ' F ', ' D2', " B'", ' L ', ' B ')
        self.myperms2['CornerEdgeBlockSwap-JY'] = (' F2', " R'", ' F ', ' D2', " B'", ' L ', ' B ', ' D2', ' F ', " L'", ' F ', ' R ', " F'", ' L ')
        self.myperms2['CornerEdgeBlockSwap-JZ'] = (' B2', ' U2', ' B2', ' U2', ' B2', " R'", ' U ', ' F2', " D'", ' L ', ' D ', ' F2', ' U ', " L'", ' U ', ' R ', " U'", ' L ')        
        

        self.myperms2['CornerEdgeBlockSwap-Super00-'] = (" U'", " F'", ' U ', ' B ', " U'", ' F ', ' U ', " B'", ' L ', ' D ', " L'", ' U ', ' L ', " D'", ' L2', ' U ', ' L ', " U'", ' F ', ' R ', ' U ', " R'", " F'", " L'", " U'", ' L ')
        self.myperms2['CornerEdgeBlockSwap-B00-'] = (" L2"," F2"," U2"," L'"," U2"," L2"," F2"," L'"," U2"," L2"," U2"," F2"," L'"," F2")
        self.myperms2['CornerEdgeBlockSwap-F00-'] = (' L ', " F'", ' D2', ' B ', " R'", " B'", ' D2', ' F2', " L'", " F'")
        self.myperms2['CornerEdgeBlockSwap-B01-'] = (' R2', ' B2', ' L2', ' D2', ' F2', ' L2', ' B2', ' R2', ' F2', ' U ', ' F2', ' U2', ' R2', ' U ', ' F2', ' U2', ' F2', ' R2', ' U ', ' R2')
        self.myperms2['CornerEdgeBlockSwap-F01-'] = (" F "," R2"," F "," R "," U "," R'"," U'"," R'"," F "," R2"," U'"," R'"," U'"," R "," U "," R'"," F2"," R2"," F'")
        
        self.myperms2['CornerEdgeBlockSwap-Super05-'] = (' D2', ' B2', ' D2', ' F2', ' U2', ' F2', ' B2', " R'", ' B2', ' D2', ' R2', ' D2', " R'", ' B2', ' R2', ' D2', ' R ', ' D2', ' B2', ' R2')
        self.myperms2['CornerEdgeBlockSwap-Super06-'] = (' D2', ' F2', ' B2', ' U2', ' F2', " R'", ' B ', ' U2', " F'", ' L ', ' F ', ' U2', ' B2', ' R ', " B'")
        
        

    def _register_myperms2_center_general(self):
        """4x4以上で使うCenter系・Bar系の手順を登録する。"""
        # 命名メモ:
        # - X-Center / Plus-Center / Oblique-Center は center の配置 family。
        # - Adjacent3Center / Line3Center は 3面の center 配置 family。
        # - OuterCenterBar / MidCenterBar は center の bar を動かす family。
        if self.size >= 4:
            self.myperms2['X-Center-XA-'] = ("2R2","2F2","2R2","2F2")
            self.myperms2['X-Center-XB-'] = (" U ","2R2","2F2","2R2","2F2"," U'")
            self.myperms2['X-Center-XC-'] = (" U2","2R2","2F2","2R2","2F2"," U2")
            self.myperms2['X-Center-WA-'] = ('2F2', " D'", '2R2', '2F2', '2R2', '2F2', ' D ', '2F2')
            self.myperms2['X-Center-WB-'] = ('2B2', " D'", '2L2', '2B2', '2L2', '2B2', ' D ', '2B2')
            self.myperms2['X-Center-WC-'] = ('2F2', ' U ', '2L2', '2F2', '2L2', '2F2', " U'", '2F2')
            self.myperms2['X-Center-WD-'] = ('2B2', ' U ', '2R2', '2B2', '2R2', '2B2', " U'", '2B2') 
            self.myperms2['X-Center-VA-'] = ("2F'", '2U ', '2F ', "2U'", '2F ', "2R'", "2F'", '2R ')
            self.myperms2['X-Center-VB-'] = ("2F'", '2U ', "2F'", "2U'", '2F ', "2R'", '2F ', '2R ')
            self.myperms2['X-Center-VC-'] = ("2R'", '2F ', '2R ', "2F'", '2U ', "2F'", "2U'", '2F ')
            self.myperms2['X-Center-UA-'] = ('2F2', ' U ', '2R2', " U'", '2R2', '2F2', '2R2', ' U ', '2R2', " U'")
            self.myperms2['X-Center-UB-'] = ('2R2', '2F2', '2R2', '2F2', ' U2', '2R2', '2F2', '2R2', '2F2', ' U2')


            

            self.myperms2['X-Center-8-'] = ("2U2","2R2","2U'","2R2","2U'","2R2","2U'","2R2","2U ")      
            
            self.myperms2['X-Center-6A-'] = ("2R ","2U ","2R'","2U'")
            self.myperms2['X-Center-6B-'] = ("2R ","2U'","2R'","2U ")
            self.myperms2['X-Center-6C-'] = ("2R ","2U2","2R'","2U2")
            self.myperms2['X-Center-6D-'] = ("2R2","2U'","2R2","2U ")
            self.myperms2['X-Center-6E-'] = ("2U'","2R ","2U ","2R2","2F ","2R ","2F'")
            self.myperms2['X-Center-6F-'] = ('2B ', '2D2', '2B ', '2D2', "2L'", "2B'", '2L ', '2U ', "2B'", "2U'")
            self.myperms2['X-Center-6G-'] = ("2R ","2U ","2R ","2U'","2R2")
            self.myperms2['X-Center-6H-'] = ("2R ","2U'","2R ","2U ","2R2")
            self.myperms2['X-Center-6I-'] = ("2R2","2U ","2R'","2U'","2R'")
            self.myperms2['X-Center-6J-'] = ("2R2","2U'","2R'","2U ","2R'")
            self.myperms2['X-Center-6K-'] = ("2R2","2U ","2R2","2U ","2R2","2U2","2R2")
            self.myperms2['X-Center-6L-'] = ("2R2","2U2","2R2","2U ","2R2","2U ","2R2")
            self.myperms2['X-Center-6M-'] = ("2U ","2R2","2U2","2R2","2U ")
            self.myperms2['X-Center-6N-'] = ("2F ","2R ","2F2","2R'","2F ")
            self.myperms2['X-Center-6O-'] = ("2F'","2R ","2F2","2R'","2F'")

            

            self.myperms2['X-Center-4A-'] = ("2R2","2U2","2R'","2U2","2R'")
            self.myperms2['X-Center-4B-'] = ("2R ","2U2","2R ","2U2","2R2")
            self.myperms2['X-Center-4C-'] = ("2U ","2F ","2R ","2F'","2R'","2U'")
            self.myperms2['X-Center-4D-'] = ('2F ', "2D'", '2F2', '2D ', "2F'", '2R2', '2F2', '2R2')
            self.myperms2['X-Center-4D(1)-'] = ("2D'", "2F'", '2D2', '2F2', '2L ', "2F'", "2L'", "2D'")
            self.myperms2['X-Center-4D(2)-'] = ("2F'", '2D2', "2B'", '2D2', '2F ', '2D ', '2B ', "2D'")
            self.myperms2['X-Center-4D(3)-'] = ("2D'", "2F'", '2D ', "2F'", '2R2', '2F ', '2R2', '2F ')
            self.myperms2['X-Center-4D(4)-'] = ('2F ', "2L'", "2F'", '2L ', "2F'", "2D'", '2F ', '2D ')
            self.myperms2['X-Center-4XA-'] = ("2L'"," U ","2R'","2D2","2R "," U'","2D2","2L ")
            self.myperms2['X-Center-4XB-'] = ("2L'"," D'","2R'","2D2","2R "," D ","2D2","2L ")
            self.myperms2['X-Center-4YA-'] = ("2B "," U'","2R ","2U ","2R'"," U ","2U'","2B'")
            self.myperms2['X-Center-4YB-'] = ("2B "," D ","2R ","2U ","2R'"," D'","2U'","2B'")
            self.myperms2['X-Center-4YC-'] = (' D2', '2L ', '2U2', '2L ', '2U2', '2L2', ' D2')
            self.myperms2['X-Center-4YD-'] = (' U2', '2L ', '2U2', '2L ', '2U2', '2L2', ' U2')
            self.myperms2['X-Center-4ZA-'] = (" U2","2R ","2U2","2R'"," U2","2R2","2U2","2R2")
            self.myperms2['X-Center-4ZB-'] = (" D2","2R ","2U2","2R'"," D2","2R2","2U2","2R2")
            self.myperms2['X-Center-4ZC-'] = (' U2', '2R ', '2U2', "2R'", ' U2', '2L2', '2U2', '2L2')
            self.myperms2['X-Center-4ZD-'] = (' D2', '2R ', '2U2', "2R'", ' D2', '2L2', '2U2', '2L2')
            self.myperms2['X-Center-4WA-'] = ('2L ', '2U2', ' D ', '2R ', '2U2', "2R'", " D'", "2L'")
            self.myperms2['X-Center-4WB-'] = ('2L ', '2U2', " U'", '2R ', '2U2', "2R'", " U ", "2L'")



            self.myperms2['X-Center-OppX'] = (" U ", '2R2', " U'", '2F2', ' U ', '2R2', " U'", '2F2')
            self.myperms2['X-Center-OppX(1)'] = (" D'", '2L2', ' D ', '2R2', " D'", '2L2', ' D ', '2R2')
            self.myperms2['X-Center-OppX(2)'] = ('2R2', '2F ', ' L ', "2F'", '2R2', '2F ', " L'", "2F'")
            self.myperms2['X-Center-OppX(3)'] = ('2R2', "2B'", ' R ', '2B ', '2R2', "2B'", " R'", '2B ')
            self.myperms2['X-Center-OppY'] = ('2R2', " U'", '2F2', ' U ', '2R2', " U'", '2F2', ' U ')
            self.myperms2['X-Center-OppY(1)'] = ('2R2', " D'", '2L2', ' D ', '2R2', " D'", '2L2', ' D ')
            self.myperms2['X-Center-OppY(2)'] = ('2F ', ' L ', "2F'", '2R2', '2F ', " L'", "2F'", '2R2')
            self.myperms2['X-Center-OppY(3)'] = ("2B'", ' R ', '2B ', '2R2', "2B'", " R'", '2B ', '2R2')
            self.myperms2['X-Center-OppZ'] = (" U'", '2R2', " U'", '2F2', ' U ', '2R2', " U'", '2F2', ' U2')
            self.myperms2['X-Center-OppZ(1)'] = (" U'", '2R2', " U'", '2L2', ' U ', '2R2', " U'", '2L2', ' U2')
            self.myperms2['X-Center-OppZ(2)'] = ('2R2', " D'", '2F ', '2B ', '2R2', "2F'", "2B'", '2R2', ' D ', '2R2')
            self.myperms2['X-Center-OppZ(3)'] = ('2R2', " D'", '2R2', '2B ', '2F ', '2R2', "2B'", "2F'", ' D ', '2R2')
            self.myperms2['X-Center-OppZ(4)'] = ('2F2', ' D ', '2R ', '2L ', '2F2', "2R'", "2L'", '2F2', " D'", '2F2')
            self.myperms2['X-Center-OppZ(5)'] = ('2F2', ' D ', '2F2', '2L ', '2R ', '2F2', "2L'", "2R'", " D'", '2F2')
            self.myperms2['X-Center-OppZ(6)'] = ('2B2', " D'", '2F2', ' D ', '2B2', " D'", '2L2', '2F2', '2L2', ' D ')
            


            self.myperms2['X-Center-InOut-Diagonal(0)'] = ("2F'", '2U ', '2F ', " U2", "2F'", "2U'", '2F ', " U2")
            self.myperms2['X-Center-InOut-Vertical(0)'] = ('2R ', '2U2', "2R'", " U2", '2R ', '2U2', "2R'", " U2")
            self.myperms2['X-Center-InOut-Diagonal(1)'] = ("2F'", '2U ', '2F ', " D2", "2F'", "2U'", '2F ', " D2")
            self.myperms2['X-Center-InOut-Vertical(1)'] = ('2R ', '2U2', "2R'", " D2", '2R ', '2U2', "2R'", " D2")
            self.myperms2['X-Center-InOut-Vertical(2)'] = ("2R "," U ","2L'"," U'","2R'"," U ","2L "," U'")
            self.myperms2['X-Center-InOut-Vertical(3)'] = ("2L'"," U ","2R "," U'","2L "," U ","2R'"," U'")
            self.myperms2['X-Center-InOut-Diagonal(2)'] = (' U ', "2L'", " U'", '2R ', ' U ', '2L ', " U'", "2R'")
            self.myperms2['X-Center-InOut-Diagonal(3)'] = (' U ', "2R ", " U'", "2L'", ' U ', "2R'", " U'", "2L ")


            
            self.myperms2['X-Center-InIn-Diagonal(0)'] = (' U2', '2R ', '2U2', "2R'", " U2", '2R ', '2U2', "2R'")
            self.myperms2['X-Center-OutOut-Diagonal(0)'] = (" D2", '2R ', '2U2', "2R'", " D2", '2R ', '2U2', "2R'")
            self.myperms2['X-Center-InIn-Vertical(0)'] = (" U2", "2F'", '2U ', '2F ', " U2", "2F'", "2U'", '2F ')
            self.myperms2['X-Center-OutOut-Vertical(0)'] = (" D2", "2F'", '2U ', '2F ', " D2", "2F'", "2U'", '2F ')

            self.myperms2['X-Center-InOut-Diagonal(4)'] = (' U2', "2B'", "2U'", '2B ', ' U2', "2B'", '2U ', '2B ')
            self.myperms2['X-Center-InOut-Diagonal(5)'] = (' D2', "2B'", "2U'", '2B ', ' D2', "2B'", '2U ', '2B ')

            self.myperms2['X-Center-Adjacent3Center-AAA(0)'] = (" F ","2D "," R2","2D'","2R'","2D "," R2","2D'","2R "," F'")
            self.myperms2['X-Center-Adjacent3Center-CCC(0)'] = (" F ","2U'"," R2","2U ","2L ","2U'"," R2","2U ","2L'"," F'")
            self.myperms2['X-Center-Adjacent3Center-BBB(0)'] = (" F'","2D'","2L'"," U2","2L ","2D ","2L'"," U2","2L "," F ")
            self.myperms2['X-Center-Adjacent3Center-DDD(0)'] = (" F'","2U ","2R "," U2","2R'","2U'","2R "," U2","2R'"," F ")

            self.myperms2['X-Center-Adjacent3Center-AAC(0)'] = (" F'","2D "," R2","2D'","2R'","2D "," R2","2D'","2R "," F ")
            self.myperms2['X-Center-Adjacent3Center-CCA(0)'] = (" F'","2U'"," R2","2U ","2L ","2U'"," R2","2U ","2L'"," F ")
            self.myperms2['X-Center-Adjacent3Center-BBD(0)'] = (" F ","2D'","2L'"," U2","2L ","2D ","2L'"," U2","2L "," F'")
            self.myperms2['X-Center-Adjacent3Center-DDB(0)'] = (" F ","2U ","2R "," U2","2R'","2U'","2R "," U2","2R'"," F'")
            
            self.myperms2['X-Center-Adjacent3Center-AAD(0)'] = ("2D "," R2","2D'","2R'","2D "," R2","2D'","2R ")
            self.myperms2['X-Center-Adjacent3Center-CCB(0)'] = ("2U'"," R2","2U ","2L ","2U'"," R2","2U ","2L'")
            self.myperms2['X-Center-Adjacent3Center-BBC(0)'] = ("2D'","2L'"," U2","2L ","2D ","2L'"," U2","2L ")
            self.myperms2['X-Center-Adjacent3Center-DDA(0)'] = ("2U ","2R "," U2","2R'","2U'","2R "," U2","2R'")

            self.myperms2['X-Center-Adjacent3Center-AAB(0)'] = ('2U ', "2L'", ' U2', '2L ', "2U'", "2L'", ' U2', '2L ')
            self.myperms2['X-Center-Adjacent3Center-CCD(0)'] = ("2D'", '2R ', ' U2', "2R'", '2D ', '2R ', ' U2', "2R'")
            self.myperms2['X-Center-Adjacent3Center-DDC(0)'] = ('2D ', ' R2', "2D'", '2L ', '2D ', ' R2', "2D'", "2L'")
            self.myperms2['X-Center-Adjacent3Center-BBA(0)'] = ("2U'", ' R2', '2U ', "2R'", "2U'", ' R2', '2U ', '2R ')

            self.myperms2['X-Center-Adjacent3Center-ADC(0)'] = ("2L'"," D'","2F'",' D ','2L '," D'",'2F ',' D ')
            self.myperms2['X-Center-Adjacent3Center-CBA(0)'] = ("2R "," D'","2B ",' D ',"2R'"," D'","2B'",' D ')
            self.myperms2['X-Center-Adjacent3Center-BAD(0)'] = ("2R "," D ","2F'"," D'","2R'"," D ","2F "," D'")
            self.myperms2['X-Center-Adjacent3Center-DCB(0)'] = ("2L'"," D ","2B "," D'","2L "," D ","2B'"," D'")

            self.myperms2['X-Center-Adjacent3Center-ABC(0)'] = (" U2","2L'"," D'","2F'",' D ','2L '," D'",'2F ',' D '," U2")
            self.myperms2['X-Center-Adjacent3Center-CDA(0)'] = (" U2","2R "," D'","2B ",' D ',"2R'"," D'","2B'",' D '," U2")
            self.myperms2['X-Center-Adjacent3Center-BCD(0)'] = (" U2","2R "," D ","2F'"," D'","2R'"," D ","2F "," D'"," U2")
            self.myperms2['X-Center-Adjacent3Center-DAB(0)'] = (" U2","2L'"," D ","2B "," D'","2L "," D ","2B'"," D'"," U2")

            self.myperms2['X-Center-Line3Center-AAD(0)'] = ("2R "," U ","2L "," U'","2R'"," U ","2L'"," U'")
            self.myperms2['X-Center-Line3Center-CCB(0)'] = ("2L'"," U ","2R'"," U'","2L "," U ","2R "," U'")
            self.myperms2['X-Center-Line3Center-ADA(0)'] = ("2R ", ' F ', '2U2', " F'", "2R'", ' F ', '2U2', " F'")
            self.myperms2['X-Center-Line3Center-CBC(0)'] = ("2L'", ' F ', '2D2', " F'", '2L ', ' F ', '2D2', " F'")

            self.myperms2['X-Center-Line3Center-ADD(0)'] = ("2L2"," F'","2R'"," F ","2L2"," F'","2R "," F ")
            self.myperms2['X-Center-Line3Center-CBB(0)'] = ("2R2"," F'","2L "," F ","2R2"," F'","2L'"," F ")
            self.myperms2['X-Center-Line3Center-AAA(0)'] = ('2U2', '2L ', '2F2', "2L'", ' F2', '2L ', '2F2', "2L'", ' F2', '2U2')
            self.myperms2['X-Center-Line3Center-CCC(0)'] = ('2D2', "2R'", '2B2', '2R ', ' F2', "2R'", '2B2', '2R ', ' F2', '2D2')
            self.myperms2['X-Center-Line3Center-CAA(0)'] = ('2D2', '2R ', '2B2', "2R'", ' B2', '2R ', '2B2', "2R'", ' B2', '2D2')
            self.myperms2['X-Center-Line3Center-ACC(0)'] = ('2U2', "2L'", '2F2', '2L ', ' B2', "2L'", '2F2', '2L ', ' B2', '2U2')

            self.myperms2['X-Center-Line3Center-ADB(0)'] = ('2D2', "2L'", ' U ', '2L ', '2D2', "2L'", " U'", '2L ')
            self.myperms2['X-Center-Line3Center-CBD(0)'] = ('2U2', '2R ', ' U ', "2R'", '2U2', '2R ', " U'", "2R'")
            self.myperms2['X-Center-Line3Center-ABD(0)'] = ('2L ', ' U ', "2L'", '2U2', '2L ', " U'", "2L'", '2U2')
            self.myperms2['X-Center-Line3Center-CDB(0)'] = ("2R'", ' U ', '2R ', '2D2', "2R'", " U'", '2R ', '2D2')
            
            self.myperms2['X-Center-Line3Center-AAC(0)'] = ('2L ', ' U2', "2L'", '2D2', '2L ', ' U2', "2L'", '2D2')
            self.myperms2['X-Center-Line3Center-CCA(0)'] = ("2R'", ' U2', '2R ', '2U2', "2R'", ' U2', '2R ', '2U2')
            self.myperms2['X-Center-Line3Center-ACA(0)'] = ('2U2', '2L ', ' U2', "2L'", '2U2', '2L ', ' U2', "2L'")
            self.myperms2['X-Center-Line3Center-CAC(0)'] = ('2D2', "2R'", ' U2', '2R ', '2D2', "2R'", ' U2', '2R ')

            self.myperms2['X-Center-Line3Center-ACB(0)'] = ('2F2', '2L ', ' D ', '2R ', " D'", "2L'", ' D ', "2R'", " D'", '2F2')
            self.myperms2['X-Center-Line3Center-CAD(0)'] = ('2B2', "2R'", ' D ', "2L'", " D'", '2R ', ' D ', '2L ', " D'", '2B2')
            self.myperms2['X-Center-Line3Center-ABC(0)'] = ('2F2', '2L ', ' F ', '2D2', " F'", "2L'", ' F ', '2D2', '2F2', " F'")
            self.myperms2['X-Center-Line3Center-CDA(0)'] = ('2B2', "2R'", ' F ', '2U2', " F'", '2R ', ' F ', '2U2', '2B2', " F'")
            self.myperms2['X-Center-Line3Center-ABB(0)'] = ('2F2', '2R2', " F'", "2L'", ' F ', '2R2', " F'", '2L ', '2F2', ' F ')
            self.myperms2['X-Center-Line3Center-CDD(0)'] = ('2B2', '2L2', " F'", '2R ', ' F ', '2L2', " F'", "2R'", '2B2', ' F ')
            self.myperms2['X-Center-Line3Center-AAB(0)'] = ('2F2', " F'", '2R2', " F'", "2L'", ' F ', '2R2', " F'", '2L ', '2F2', ' F2')
            self.myperms2['X-Center-Line3Center-CCD(0)'] = ('2B2', " F'", '2L2', " F'", '2R ', ' F ', '2L2', " F'", "2R'", '2B2', ' F2') 
            self.myperms2['X-Center-Line3Center-ABA(0)'] = (' B2', '2F2', '2L ', ' B ', '2R2', " B'", "2L'", ' B ', '2R2', ' B ', '2F2')
            self.myperms2['X-Center-Line3Center-CDC(0)'] = (' B2', '2B2', "2R'", ' B ', '2L2', " B'", '2R ', ' B ', '2L2', ' B ', '2B2')



            if self.size % 2 == 1:
                self.myperms2['Plus-Center-XA-'] = (" S2","2R2"," S2","2R2")
                self.myperms2['Plus-Center-XB-'] = (" U "," S2","2R2"," S2","2R2"," U'")
                self.myperms2['Plus-Center-Y-'] = (" E ","2R2"," E'","2R2")
                self.myperms2['Plus-Center-Z-'] = ('2B ', " E'", '2B2', ' E ', '2B ')
                self.myperms2['Plus-Center-WA-'] = ("2L2"," E2","2L'"," U ","2R'"," E2","2R "," U'","2L'")
                self.myperms2['Plus-Center-WB-'] = ("2R2"," E2","2R "," U ","2L "," E2","2L'"," U'","2R ")
                self.myperms2['Plus-Center-U-'] = ('2R ', ' S2', '2R2', ' S2', '2R ')
                self.myperms2['Plus-Center-V-'] = (" E'", "2B'", ' E ', '2B2', " E'", "2B'", ' E ')
                self.myperms2['Plus-Center-TA-'] = (' M ', '2U2', " M'", '2U ', ' S ', '2U2', " S'", "2U'")
                self.myperms2['Plus-Center-TB-'] = (" U ","2L'", " E'", '2B ', ' E ', "2B'", '2L ', '2B2', ' E2', '2B ', ' E2', '2B '," U'")
                self.myperms2['Plus-Center-TC-'] = (' S2', ' M2', ' D ', '2F2', " D'", ' S2', ' M2', ' D ', '2F2', " D'")

                
                self.myperms2['Plus-Center-6A-'] = ("2R "," E ","2R'"," E'")
                self.myperms2['Plus-Center-6B-'] = (" E ","2R "," E'","2R'")                
                self.myperms2['Plus-Center-6C-'] = ("2R "," E2","2R'"," E2")
                self.myperms2['Plus-Center-6D-'] = (" E2","2R'"," E2","2R ")
                self.myperms2['Plus-Center-6E-'] = ('2U ', " M'", '2B ', ' M ', "2B'", "2U'", " E'", "2F'", " E'", '2F ', ' E2')
                self.myperms2['Plus-Center-6F-'] = ('2U ', ' S ', '2R ', " S'", " E'", '2F ', ' E ', "2F'", "2R'", "2U'")
                self.myperms2['Plus-Center-6G-'] = ("2R "," E ","2R "," E'","2R2")
                self.myperms2['Plus-Center-6H-'] = ("2R2"," E'","2R'"," E ","2R'")
                self.myperms2['Plus-Center-6I-'] = (" M ","2U "," M ","2U'"," M2")
                self.myperms2['Plus-Center-6J-'] = (" M2","2U'"," M'","2U "," M'")                



                self.myperms2['Plus-Center-4A-'] = ("2R2"," E2","2R "," E2","2R ")
                self.myperms2['Plus-Center-4B-'] = ("2R "," E2","2R "," E2","2R2")
                self.myperms2['Plus-Center-4C-'] = ("2U "," S ","2R "," S'","2R'","2U'")
                self.myperms2['Plus-Center-4D-'] = (" M'", "2B'", ' M2', "2U'", " M'", '2U ', '2B ')
                self.myperms2['Plus-Center-4E-'] = ('2U ', " M'", '2U ', " M'", "2U'", ' M2', "2U'")
                self.myperms2['Plus-Center-4XA-'] = ("2L'"," U ","2R'"," E2","2R "," U'"," E2","2L ")
                self.myperms2['Plus-Center-4XB-'] = ("2L'"," D'","2R'"," E2","2R "," D "," E2","2L ")
                self.myperms2['Plus-Center-4YA-'] = ("2B "," U'","2R "," E'","2R'"," U "," E ","2B'")
                self.myperms2['Plus-Center-4YB-'] = ("2B "," D ","2R "," E'","2R'"," D'"," E ","2B'")                
                self.myperms2['Plus-Center-4YC-'] = ('2L ', " U'", '2R ', ' E2', "2R'", " U ", ' E2', "2L'")
                self.myperms2['Plus-Center-4YD-'] = ('2L ', ' D ', '2R ', ' E2', "2R'", " D'", ' E2', "2L'")
                self.myperms2['Plus-Center-4ZA-'] = (' U2', '2R ', ' E2', '2R ', ' E2', '2R2', ' U2')
                self.myperms2['Plus-Center-4ZB-'] = (' D2', '2R ', ' E2', '2R ', ' E2', '2R2', ' D2')
                self.myperms2['Plus-Center-4ZC-'] = (' U2', '2R ', ' E2', "2R'", ' U2', '2L2', ' E2', '2L2')
                self.myperms2['Plus-Center-4ZD-'] = (' D2', '2R ', ' E2', "2R'", ' D2', '2L2', ' E2', '2L2')
                self.myperms2['Plus-Center-4WA-'] = ('2L ', ' E2', ' D ', '2R ', ' E2', "2R'", " D'", "2L'")
                self.myperms2['Plus-Center-4WB-'] = ('2L ', ' E2', " U'", '2R ', ' E2', "2R'", " U ", "2L'")


                self.myperms2['MidCenterBar(VV)'] = (" M'"," U "," L "," R'"," M "," F'"," M "," F "," L'"," R "," M'"," U'")
                self.myperms2['MidCenterBar(HV)'] = (' U ', ' M ', " R'", ' L ', " F'", " M'", ' F ', " M'", ' R ', " L'", " U'", ' M ')
                self.myperms2['MidCenterBar(HH)'] = (' M ', " R'", ' L ', " F'", " M'", ' F ', " M'", ' R ', " L'", " U'", ' M ',' U ')

                self.myperms2['MidCenterBar-Opp(VV)'] = (" M2"," U "," L2"," R2"," M2"," D'"," M2"," D "," L2"," R2"," M2"," U'")
                self.myperms2['MidCenterBar-Opp(HV)'] = (' U ', ' M2', " R2", ' L2', " D'", " M2", ' D ', " M2", ' R2', " L2", " U'", ' M2')

                self.myperms2['MidCenterBar-Adjacent3Center-A'] = (" F "," U "," L "," R'"," M "," F'"," M "," F "," L'"," R "," M'"," U'"," M'"," F'")
                self.myperms2['MidCenterBar-Adjacent3Center-B'] = (" U "," L "," R'"," M "," F'"," M "," F "," L'"," R "," M'"," U'"," M'")
                self.myperms2['MidCenterBar-Adjacent3Center-C'] = (' F ',' L '," R'",' M '," F'",' M ',' F '," L'",' R '," M'"," U'"," M'",' U '," F'")
                self.myperms2['MidCenterBar-Adjacent3Center-D'] = (" L "," R'"," M "," F'"," M "," F "," L'"," R "," M'"," U'"," M'"," U ")                
                self.myperms2['MidCenterBar-Adjacent3Center-E'] = (" B'"," F "," U "," L "," R'"," M "," F'"," M "," F "," L'"," R "," M'"," U'"," M'"," F'"," B ")
                self.myperms2['MidCenterBar-Adjacent3Center-F'] = (" B'"," U "," L "," R'"," M "," F'"," M "," F "," L'"," R "," M'"," U'"," M'"," B ")
                self.myperms2['MidCenterBar-Adjacent3Center-G'] = (' B '," F'"," R'",' L ',' M ',' F ',' M '," F'",' R '," L'"," M'",' U '," M'"," U'",' F '," B'")
                self.myperms2['MidCenterBar-Adjacent3Center-H'] = (" B'"," L "," R'"," M "," F'"," M "," F "," L'"," R "," M'"," U'"," M'"," U "," B ")

                self.myperms2['MidCenterBar-Adjacent3Center-OA'] = (" E'"," U'"," M'"," U "," L "," R'"," M "," F'"," M "," F "," L'"," R "," M'"," E ")
                self.myperms2['MidCenterBar-Adjacent3Center-OB'] = self.invert_moves(self.myperms2['MidCenterBar-Adjacent3Center-OA'])
                self.myperms2['MidCenterBar-Adjacent3Center-OC'] = (" E'"," M'"," U "," L "," R'"," M "," F'"," M "," F "," L'"," R "," M'"," U'"," E ")
                self.myperms2['MidCenterBar-Adjacent3Center-OD'] = self.invert_moves(self.myperms2['MidCenterBar-Adjacent3Center-OC'])



                self.myperms2['Plus-Center-OppX'] = (" U ", '2R2', " U'", ' S2', ' U ', '2R2', " U'", ' S2')
                self.myperms2['Plus-Center-OppX(1)'] = (' U ', '2R2', " U'", ' M2', ' U ', '2R2', " U'", ' M2')
                self.myperms2['Plus-Center-OppX(2)'] = ('2F2', ' D ', ' M2', '2F2', ' M2', '2F2', " D'", '2F2')
                self.myperms2['Plus-Center-OppY'] = ('2R2', " U'", ' S2', ' U ', '2R2', " U'", ' S2', ' U ')
                self.myperms2['Plus-Center-OppY(1)'] = ('2R2', " U'", ' M2', ' U ', '2R2', " U'", ' M2', ' U ')
                self.myperms2['Plus-Center-OppZ'] = (" M2"," U ","2F2"," U'"," M2"," U ","2F2"," U'")
                self.myperms2['Plus-Center-OppZ(1)'] = (' M2', ' U ', '2R2', " U'", ' M2', ' U ', '2R2', " U'")
                

                self.myperms2['Plus-Center-Middle-Inside(0)'] = (" S'", '2U ', ' S ', " U2", " S'", "2U'", ' S ', " U2")
                self.myperms2['Plus-Center-Middle-Outside(0)'] = (" S'", '2U ', ' S ', " D2", " S'", "2U'", ' S ', " D2")
                self.myperms2['Plus-Center-Middle-Vertical(0)'] = ('2R ', ' E2', "2R'", " U2", '2R ', ' E2', "2R'", " U2")
                self.myperms2['Plus-Center-Middle-Vertical(1)'] = ('2R ', ' E2', "2R'", " D2", '2R ', ' E2', "2R'", " D2")
                self.myperms2['Plus-Center-Middle-Vertical(2)'] = ("2R "," U "," M'"," U'","2R'"," U "," M "," U'")
                self.myperms2['Plus-Center-Middle-Vertical(3)'] = ("2L'"," U "," M'"," U'","2L "," U "," M "," U'")
                self.myperms2['Plus-Center-Middle-Vertical(4)'] = (" E'"," L2"," E ","2R'"," E'"," L2"," E ","2R ")
                self.myperms2['Plus-Center-Middle-Vertical(5)'] = (" S'", ' L2', ' S ', "2L'", " S'", ' L2', ' S ', '2L ')

                
                self.myperms2['Plus-Center-Middle-Diagonal(0)'] = (' U2', '2R ', ' E2', "2R'", " U2", '2R ', ' E2', "2R'")
                self.myperms2['Plus-Center-Middle-Diagonal(1)'] = (" D2", '2R ', ' E2', "2R'", " D2", '2R ', ' E2', "2R'")
                self.myperms2['Plus-Center-Middle-Diagonal(2)'] = ("2R'"," E'"," L2"," E ","2R "," E'"," L2"," E ")
                self.myperms2['Plus-Center-Middle-Diagonal(3)'] = ("2L'", " S'", ' L2', ' S ', '2L ', " S'", ' L2', ' S ')

                self.myperms2['Plus-Center-Middle-Inside(1)'] = (" U2", " S'", '2U ', ' S ', " U2", " S'", "2U'", ' S ')
                self.myperms2['Plus-Center-Middle-Outside(1)'] = (" D2", " S'", '2U ', ' S ', " D2", " S'", "2U'", ' S ')

                self.myperms2['Plus-Center-Middle-Inside(2)'] = (' U2', '2F ', ' E ', "2F'", ' U2', '2F ', " E'", "2F'")
                self.myperms2['Plus-Center-Middle-Outside(2)'] = (' D2', '2F ', ' E ', "2F'", ' D2', '2F ', " E'", "2F'")

                self.myperms2['Plus-Center-Middle-Inside(3)'] = (" U ", " M'", " U'", "2L'", " U ", ' M ', " U'", '2L ')
                self.myperms2['Plus-Center-Middle-Outside(3)'] = (" U ", " M'", " U'", "2R ", " U ", ' M ', " U'", "2R'")

                self.myperms2['Plus-Center-Middle-Inside(4)'] = (" F'", '2L ', ' F ', ' M ', " F'", "2L'", ' F ', " M'")
                self.myperms2['Plus-Center-Middle-Outside(4)'] = (" F'", "2R'", ' F ', ' M ', " F'", "2R ", ' F ', " M'")




                self.myperms2['Plus-Center-InOut(0)'] = (" U2","2D'"," M'","2D "," M "," U2"," M'","2D'"," M ","2D ")
                self.myperms2['Plus-Center-InOut(1)'] = (" U2","2U "," M'","2U'"," M "," U2"," M'","2U "," M ","2U'")
                self.myperms2['Plus-Center-InOut(2)'] = (" M'"," U ","2R "," U'"," M "," U ","2R'"," U'")
                self.myperms2['Plus-Center-InOut(3)'] = (" M'"," U ","2L'"," U'"," M "," U ","2L "," U'")                
                self.myperms2['Plus-Center-OutOut(0)'] = ("2D'"," M'","2D "," M "," U2"," M'","2D'"," M ","2D "," U2")
                self.myperms2['Plus-Center-InIn(0)'] = ("2U "," M'","2U'"," M "," U2"," M'","2U "," M ","2U'"," U2")

                self.myperms2['Plus-Center-Adjacent3Center-AAA(0)'] = (" F ","2D "," R2","2D'"," M ","2D "," R2","2D'"," M'"," F'")
                self.myperms2['Plus-Center-Adjacent3Center-CCC(0)'] = (" F ","2U'"," R2","2U "," M ","2U'"," R2","2U "," M'"," F'")
                self.myperms2['Plus-Center-Adjacent3Center-BBB(0)'] = (" F'"," E'","2L'"," U2","2L "," E ","2L'"," U2","2L "," F ")
                self.myperms2['Plus-Center-Adjacent3Center-DDD(0)'] = (" F'"," E'","2R "," U2","2R'"," E ","2R "," U2","2R'"," F ")

                self.myperms2['Plus-Center-Adjacent3Center-AAC(0)'] = (" F'","2D "," R2","2D'"," M ","2D "," R2","2D'"," M'"," F ")
                self.myperms2['Plus-Center-Adjacent3Center-CCA(0)'] = (" F'","2U'"," R2","2U "," M ","2U'"," R2","2U "," M'"," F ")
                self.myperms2['Plus-Center-Adjacent3Center-BBD(0)'] = (" F "," E'","2L'"," U2","2L "," E ","2L'"," U2","2L "," F'")
                self.myperms2['Plus-Center-Adjacent3Center-DDB(0)'] = (" F "," E'","2R "," U2","2R'"," E ","2R "," U2","2R'"," F'")
            
                self.myperms2['Plus-Center-Adjacent3Center-AAD(0)'] = ("2D "," R2","2D'"," M ","2D "," R2","2D'"," M'")
                self.myperms2['Plus-Center-Adjacent3Center-CCB(0)'] = ("2U'"," R2","2U "," M ","2U'"," R2","2U "," M'")
                self.myperms2['Plus-Center-Adjacent3Center-BBC(0)'] = (" E'","2L'"," U2","2L "," E ","2L'"," U2","2L ")
                self.myperms2['Plus-Center-Adjacent3Center-DDA(0)'] = (" E'","2R "," U2","2R'"," E ","2R "," U2","2R'")

                self.myperms2['Plus-Center-Adjacent3Center-DDC(0)'] = ('2L2', " F'", ' E ', ' F ', '2L ', " F'", " E'", ' F ', '2L ')
                self.myperms2['Plus-Center-Adjacent3Center-BBA(0)'] = ('2R2', " F'", ' E ', ' F ', "2R'", " F'", " E'", ' F ', "2R'")
                self.myperms2['Plus-Center-Adjacent3Center-CCD(0)'] = ('2D ', ' F ', " M'", " F'", '2D ', ' F ', ' M ', " F'", '2D2')
                self.myperms2['Plus-Center-Adjacent3Center-AAB(0)'] = ("2U'", ' F ', " M'", " F'", "2U'", ' F ', ' M ', " F'", '2U2')
                

                self.myperms2['Plus-Center-Adjacent3Center-ADC(0)'] = ("2L'"," D'"," S'",' D ','2L '," D'",' S ',' D ')
                self.myperms2['Plus-Center-Adjacent3Center-CBA(0)'] = ("2R "," D'"," S'",' D ',"2R'"," D'"," S ",' D ')
                self.myperms2['Plus-Center-Adjacent3Center-BAD(0)'] = (" M'", ' D ', "2F'", " D'", ' M ', ' D ', "2F ", " D'")
                self.myperms2['Plus-Center-Adjacent3Center-DCB(0)'] = (" M'", ' D ', '2B ', " D'", ' M ', ' D ', "2B'", " D'")

                self.myperms2['Plus-Center-Adjacent3Center-ABC(0)'] = (" U2","2L'"," D'"," S'",' D ','2L '," D'",' S ',' D '," U2")
                self.myperms2['Plus-Center-Adjacent3Center-CDA(0)'] = (" U2","2R "," D'"," S'",' D ',"2R'"," D'"," S ",' D '," U2")
                self.myperms2['Plus-Center-Adjacent3Center-BCD(0)'] = (" U2"," M'", "2F'", ' M ', ' U ', " M'", " U'", '2F ', ' U ', ' M ', " U ")
                self.myperms2['Plus-Center-Adjacent3Center-DAB(0)'] = (" U2"," M'", "2B ", ' M ', ' U ', " M'", " U'", "2B'", ' U ', ' M ', " U ")

                self.myperms2['Plus-Center-Line3Center-BBA(0)'] = ("2R "," U "," M "," U'","2R'"," U "," M'"," U'")
                self.myperms2['Plus-Center-Line3Center-BBC(0)'] = ('2R '," U'",' M ',' U ',"2R'"," U'"," M'",' U ')
                self.myperms2['Plus-Center-Line3Center-BDC(0)'] = (" U2","2L'"," U "," M "," U'","2L "," U "," M'"," U ")
                self.myperms2['Plus-Center-Line3Center-BDA(0)'] = (" U2","2L'"," U'",' M ',' U ',"2L "," U'"," M'"," U'")
                self.myperms2['Plus-Center-Line3Center-BAB(0)'] = ("2R ", ' F ', ' E2', " F'", "2R'", ' F ', ' E2', " F'")
                self.myperms2['Plus-Center-Line3Center-BCB(0)'] = ("2R ", " F'", ' E2', " F ", "2R'", " F'", ' E2', " F ")

                self.myperms2['Plus-Center-Line3Center-ABB(0)'] = ("2R2"," F "," M "," F'","2R2"," F "," M'"," F'")
                self.myperms2['Plus-Center-Line3Center-CBB(0)'] = ("2R2"," F'"," M "," F ","2R2"," F'"," M'"," F ")
                self.myperms2['Plus-Center-Line3Center-CAB(0)'] = (" F'","2R2"," F'"," M "," F ","2R2"," F'"," M'"," F2")
                self.myperms2['Plus-Center-Line3Center-ACB(0)'] = (" F ","2R2"," F "," M "," F'","2R2"," F "," M'"," F2")

                self.myperms2['Plus-Center-Line3Center-AAB(0)'] = (" M'"," U'","2R'"," U "," M "," U'","2R "," U ")
                self.myperms2['Plus-Center-Line3Center-CCB(0)'] = (" M'"," U ","2R'"," U'"," M "," U ","2R "," U'")
                self.myperms2['Plus-Center-Line3Center-ABA(0)'] = (" M'", " F'", '2U2', ' F ', ' M ', " F'", '2U2', ' F ')
                self.myperms2['Plus-Center-Line3Center-CBC(0)'] = (" M'", ' F ', '2D2', " F'", ' M ', ' F ', '2D2', " F'")

                self.myperms2['Plus-Center-Line3Center-BAA(0)'] = (" M2"," F'","2R'"," F "," M2"," F'","2R "," F ")
                self.myperms2['Plus-Center-Line3Center-BCC(0)'] = (" M2"," F ","2R'"," F'"," M2"," F ","2R "," F'")

                self.myperms2['Plus-Center-Line3Center-BDD(0)'] = ("2L ", " S ", ' R2', " S'", '2L2', " S ", ' R2', " S'", "2L ")
                self.myperms2['Plus-Center-Line3Center-BBB(0)'] = ('2L ', ' E2', "2L'", ' U2', '2L ', ' E2', '2L2', ' E2', '2L ', ' U2', "2L'", ' E2', '2L ')
                self.myperms2['Plus-Center-Line3Center-BDB(0)'] = (' E2', "2L'", ' U2', '2L ', ' E2', "2L'", ' U2', '2L ')
                self.myperms2['Plus-Center-Line3Center-BBD(0)'] = ('2L ', ' U2', "2L'", ' E2', '2L ', ' U2', "2L'", ' E2')
                self.myperms2['Plus-Center-Line3Center-BCA(0)'] = (" S ", "2U ", " S'", ' U2', " S ", '2U2', " S'", ' U2', " S ", "2U ", " S'")
                self.myperms2['Plus-Center-Line3Center-BAC(0)'] = (" S'", '2D ', ' S ', ' U2', " S'", '2D2', ' S ', ' U2', " S'", '2D ', ' S ')

                self.myperms2['Plus-Center-Line3Center-CCA(0)'] = ("2U2"," B "," M "," B'","2U2"," B "," M'"," B'")
                self.myperms2['Plus-Center-Line3Center-AAC(0)'] = ("2D2"," B "," M "," B'","2D2"," B "," M'"," B'")
                self.myperms2['Plus-Center-Line3Center-ACA(0)'] = (' F ', " M'", " F'", '2U2', ' F ', ' M ', " F'", '2U2')
                self.myperms2['Plus-Center-Line3Center-CAC(0)'] = (' F ', " M'", " F'", '2D2', ' F ', ' M ', " F'", '2D2')
                self.myperms2['Plus-Center-Line3Center-CCC(0)'] = (" B2","2U2"," B "," M "," B'","2U2"," B "," M'"," B ")
                self.myperms2['Plus-Center-Line3Center-AAA(0)'] = (" B2","2D2"," B "," M "," B'","2D2"," B "," M'"," B ")

                self.myperms2['Plus-Center-Line3Center-ABD(0)'] = (' E2', '2R ', " U'", "2R'", ' E2', '2R ', ' U ', "2R'")
                self.myperms2['Plus-Center-Line3Center-CBD(0)'] = (' E2', '2R ', ' U ', "2R'", ' E2', '2R ', " U'", "2R'")
                
            if self.size >= 6:
                self.myperms2['Oblique-Center-Opp4-XA-'] = ("2R2","3F2","2R2","3F2")
                self.myperms2['Oblique-Center-Opp4-XB-'] = (" U ","2R2","3F2","2R2","3F2"," U'")
                self.myperms2['Oblique-Center-Opp4-XC-'] = (" U2","2R2","3F2","2R2","3F2"," U2")
                self.myperms2['Oblique-Center-Opp4-WA-'] = ("2L2","3D2","2L'"," U ","2R'","3D2","2R "," U'","2L'")
                self.myperms2['Oblique-Center-Opp4-WB-'] = ("2R2","3U2","2R "," U ","2L ","3U2","2L'"," U'","2R ")
                self.myperms2['Oblique-Center-Opp4-WC-'] = ("2L2","3U2","2L'"," U ","2R'","3U2","2R "," U'","2L'")
                self.myperms2['Oblique-Center-Opp4-WD-'] = ("2R2","3D2","2R "," U ","2L ","3D2","2L'"," U'","2R ")
                self.myperms2['Oblique-Center-Opp4-VA-'] = ('2L2', ' U ', '2L2', '3B2', '2L2', " U'", '2L2', ' U ', '3B2', " U'")
                self.myperms2['Oblique-Center-Opp4-VB-'] = (" U'", '2L2', ' U ', '2L2', '3B2', '2L2', " U'", '2L2', ' U ', '3B2')
                self.myperms2['Oblique-Center-Opp4-VC-'] = ('2B2', '3L2', '2B2', '3L2', ' U ', '3B2', '2R2', '3B2', '2R2', " U'")
                self.myperms2['Oblique-Center-Opp4-UA-'] = ("3L'", "2D'", '3B ', '2D ', "3B'", '3L ', '3B2', '2U2', '3B ', '2U2', '3B ')
                self.myperms2['Oblique-Center-Opp4-UB-'] = ("3L'", "2U ", '3B ', "2U'", "3B'", '3L ', '3B2', '2D2', '3B ', '2D2', '3B ')
                self.myperms2['Oblique-Center-Opp4-UC-'] = (" U ","3L'", "2D'", '3B ', '2D ', "3B'", '3L ', '3B2', '2U2', '3B ', '2U2', '3B '," U'")
                self.myperms2['Oblique-Center-Opp4-UD-'] = (" U ","3L'", "2U ", '3B ', "2U'", "3B'", '3L ', '3B2', '2D2', '3B ', '2D2', '3B '," U'")
                self.myperms2['Oblique-Center-Opp4-UE-'] = (" U2","3L'", "2D'", '3B ', '2D ', "3B'", '3L ', '3B2', '2U2', '3B ', '2U2', '3B '," U2")
                self.myperms2['Oblique-Center-Opp4-UF-'] = (" U2","3L'", "2U ", '3B ', "2U'", "3B'", '3L ', '3B2', '2D2', '3B ', '2D2', '3B '," U2")
                self.myperms2['Oblique-Center-Opp4-ZA-'] = ('3L2', '2B2', '3L2', '2B2', ' U2', '3R2', '2B2', '3R2', '2B2', ' U2')
                self.myperms2['Oblique-Center-Opp4-ZB-'] = (" U ", '3L2', '2B2', '3L2', '2B2', ' U2', '3R2', '2B2', '3R2', '2B2', ' U ')
                self.myperms2['Oblique-Center-Opp4-YA-'] = (" U'", '2L2', '2F2', ' U ', '3R2', " U'", '2F2', '2L2', ' U ', '3R2')
                self.myperms2['Oblique-Center-Opp4-YB-'] = ('2L2', '2F2', ' U ', '3R2', " U'", '2F2', '2L2', ' U ', '3R2', " U'")
                self.myperms2['Oblique-Center-Opp4-YC-'] = (" U ", '2L2', '2F2', ' U ', '3R2', " U'", '2F2', '2L2', ' U ', '3R2', " U2")
                self.myperms2['Oblique-Center-Opp4-T-'] = (" D'", '2L2', ' D ', '3F2', '2L2', '3F2', '2L2', '3B2', " D'", '2L2', ' D ', '3B2')


                self.myperms2['Oblique-Center-8-'] = ("3U2","2R2","3U'","2R2","3U'","2R2","3U'","2R2","3U ")      
                
                self.myperms2['Oblique-Center-6A-'] = ("2R ","3U ","2R'","3U'")
                self.myperms2['Oblique-Center-6B-'] = ("2R ","3U'","2R'","3U ")
                self.myperms2['Oblique-Center-6C-'] = ("2R ","3U2","2R'","3U2")
                self.myperms2['Oblique-Center-6D-'] = ("2R2","3U ","2R2","3U'")
                self.myperms2['Oblique-Center-6E-'] = ("2R'", "3F'", "2U'", '3F ', '2U ', '2R ', '3L ', '2F2', '3L ', '2F2', '3L2')
                self.myperms2['Oblique-Center-6F-'] = ('3L ', "2F'", '3D ', '2F ', "3D'", '2L ', "3L'", '3B2', '2L ', '3B2', '2L2')
                self.myperms2['Oblique-Center-6G-'] = ("2R ","3U ","2R ","3U'","2R2")
                self.myperms2['Oblique-Center-6H-'] = ("2R ","3U'","2R ","3U ","2R2")
                self.myperms2['Oblique-Center-6I-'] = ("2R2","3U ","2R'","3U'","2R'")
                self.myperms2['Oblique-Center-6J-'] = ("2R2","3U'","2R'","3U ","2R'")
                self.myperms2['Oblique-Center-6K-'] = ("2R2","3U ","2R2","3U ","2R2","3U2","2R2")
                self.myperms2['Oblique-Center-6L-'] = ("2R2","3U2","2R2","3U ","2R2","3U ","2R2")
                self.myperms2['Oblique-Center-6M-'] = ("2U ","3R2","2U2","3R2","2U ")
                self.myperms2['Oblique-Center-6N-'] = ("2F ","3R ","2F2","3R'","2F ")
                self.myperms2['Oblique-Center-6O-'] = ("2F'","3R ","2F2","3R'","2F'")                

                self.myperms2['Oblique-Center-4A-'] = ("2R2","3U2","2R ","3U2","2R ")
                self.myperms2['Oblique-Center-4B-'] = ("2R ","3U2","2R ","3U2","2R2")
                self.myperms2['Oblique-Center-4C-'] = ("2U ","3F ","2R ","3F'","2R'","2U'")
                self.myperms2['Oblique-Center-4D-'] = ("2F'", '3D ', "2R'", "3D'", '2R ', '2F ')
                self.myperms2['Oblique-Center-4XA-'] = ("2L'"," U ","2R'","3D2","2R "," U'","3D2","2L ")
                self.myperms2['Oblique-Center-4XB-'] = ("2L'"," D'","2R'","3D2","2R "," D ","3D2","2L ")
                self.myperms2['Oblique-Center-4YA-'] = ("2B "," U'","2R ","3U ","2R'"," U ","3U'","2B'")
                self.myperms2['Oblique-Center-4YB-'] = ("2B "," D ","2R ","3U ","2R'"," D'","3U'","2B'")
                self.myperms2['Oblique-Center-4YC-'] = ('2L ', " U'", '2R ', '3U2', "2R'", " U ", '3U2', "2L'")
                self.myperms2['Oblique-Center-4YD-'] = ('2L ', ' D ', '2R ', '3U2', "2R'", " D'", '3U2', "2L'")
                self.myperms2['Oblique-Center-4ZA-'] = (' U2', '2R ', '3U2', '2R ', '3U2', '2R2', ' U2')
                self.myperms2['Oblique-Center-4ZB-'] = (' D2', '2R ', '3U2', '2R ', '3U2', '2R2', ' D2')
                self.myperms2['Oblique-Center-4ZC-'] = (' U2', '2R ', '3U2', "2R'", ' U2', '2L2', '3U2', '2L2')
                self.myperms2['Oblique-Center-4ZD-'] = (' D2', '2R ', '3U2', "2R'", ' D2', '2L2', '3U2', '2L2')
                self.myperms2['Oblique-Center-4WA-'] = ('2L ', '3U2', ' D ', '2R ', '3U2', "2R'", " D'", "2L'")
                self.myperms2['Oblique-Center-4WB-'] = ('2L ', '3U2', " U'", '2R ', '3U2', "2R'", " U ", "2L'")
                

                self.myperms2['Oblique-Center-OppX'] = (" U ", '2R2', " U'", '3F2', ' U ', '2R2', " U'", '3F2')
                self.myperms2['Oblique-Center-OppX(1)'] = ('3B2', ' U ', '3B2', '2R2', '3B2', '2R2', " U'", '3B2')
                self.myperms2['Oblique-Center-OppX(2)'] = (" D'", '3L2', ' D ', '2R2', " D'", '3L2', ' D ', '2R2')
                self.myperms2['Oblique-Center-OppY'] = ('2R2', " U'", '3F2', ' U ', '2R2', " U'", '3F2', ' U ')
                self.myperms2['Oblique-Center-OppY(1)'] = ('2R2', ' U ', '3F2', " U'", '2R2', ' U ', '3F2', " U'")
                self.myperms2['Oblique-Center-OppY(2)'] = ('3F2', ' D ', '2R2', '3F2', '2R2', '3F2', " D'", '3F2')
                self.myperms2['Oblique-Center-OppY(3)'] = ('3B2', " U'", '2R2', '3B2', '2R2', '3B2', ' U ', '3B2')
                self.myperms2['Oblique-Center-OppY(4)'] = ('2R2', " U'", '3L2', ' U ', '2R2', " U'", '3L2', ' U ')
                self.myperms2['Oblique-Center-OppY(5)'] = ('2R2', ' U ', '3R2', " U'", '2R2', ' U ', '3R2', " U'")
                self.myperms2['Oblique-Center-OppZ'] = (' U ', '3F2', " U'", '2R2', ' U ', '3F2', " U'", '2R2')
                self.myperms2['Oblique-Center-OppZ(1)'] = ('3B2', " U'", '3B2', '2R2', '3B2', '2R2', ' U ', '3B2')
                self.myperms2['Oblique-Center-OppZ(2)'] = (' U ', '3F2', " U'", '2F2', ' U ', '3F2', " U'", '2F2')


                self.myperms2['Oblique-Center-InOut-Diagonal(0)'] = ("3F'", '2U ', '3F ', " U2", "3F'", "2U'", '3F ', " U2")
                self.myperms2['Oblique-Center-InOut-Diagonal(1)'] = ("3F'", '2U ', '3F ', " D2", "3F'", "2U'", '3F ', " D2")
                self.myperms2['Oblique-Center-InOut-Vertical(0)'] = ('2R ', '3U2', "2R'", " U2", '2R ', '3U2', "2R'", " U2")
                self.myperms2['Oblique-Center-InOut-Vertical(1)'] = ('2R ', '3U2', "2R'", " D2", '2R ', '3U2', "2R'", " D2")
                self.myperms2['Oblique-Center-InOut-Vertical(2)'] = ("2R "," U ","3L'"," U'","2R'"," U ","3L "," U'")
                self.myperms2['Oblique-Center-InOut-Vertical(3)'] = ("2L'"," U ","3R "," U'","2L "," U ","3R'"," U'")
                self.myperms2['Oblique-Center-InOut-Vertical(4)'] = ("2R "," U ","3R "," U'","2R'"," U ","3R'"," U'")
                self.myperms2['Oblique-Center-InOut-Vertical(5)'] = ("2L'"," U ","3L'"," U'","2L "," U ","3L "," U'")                
                self.myperms2['Oblique-Center-InOut-Diagonal(2)'] = (' U ', "3L'", " U'", '2R ', ' U ', '3L ', " U'", "2R'")
                self.myperms2['Oblique-Center-InOut-Diagonal(3)'] = (' U ', "3R ", " U'", "2L'", ' U ', "3R'", " U'", "2L ")
                
                self.myperms2['Oblique-Center-InIn-Diagonal(0)'] = (' U2', '2R ', '3U2', "2R'", " U2", '2R ', '3U2', "2R'")
                self.myperms2['Oblique-Center-OutOut-Diagonal(0)'] = (" D2", '2R ', '3U2', "2R'", " D2", '2R ', '3U2', "2R'")
                self.myperms2['Oblique-Center-InIn-Vertical(0)'] = (" U2", "3F'", '2U ', '3F ', " U2", "3F'", "2U'", '3F ')
                self.myperms2['Oblique-Center-OutOut-Vertical(0)'] = (" D2", "3F'", '2U ', '3F ', " D2", "3F'", "2U'", '3F ')

                self.myperms2['Oblique-Center-InOut-Diagonal(4)'] = (' U2', "3B'", "2U'", '3B ', ' U2', "3B'", '2U ', '3B ')
                self.myperms2['Oblique-Center-InOut-Diagonal(5)'] = (' D2', "3B'", "2U'", '3B ', ' D2', "3B'", '2U ', '3B ')

                

                self.myperms2['Oblique-Center-Adjacent3Center-AAA(0)'] = (" F ","2D "," R2","2D'","3R'","2D "," R2","2D'","3R "," F'")
                self.myperms2['Oblique-Center-Adjacent3Center-CCC(0)'] = (" F ","2U'"," R2","2U ","3L ","2U'"," R2","2U ","3L'"," F'")
                self.myperms2['Oblique-Center-Adjacent3Center-BBB(0)'] = (" F'","3D'","2L'"," U2","2L ","3D ","2L'"," U2","2L "," F ")
                self.myperms2['Oblique-Center-Adjacent3Center-DDD(0)'] = (" F'","3U ","2R "," U2","2R'","3U'","2R "," U2","2R'"," F ")

                self.myperms2['Oblique-Center-Adjacent3Center-AAC(0)'] = (" F'","2D "," R2","2D'","3R'","2D "," R2","2D'","3R "," F ")
                self.myperms2['Oblique-Center-Adjacent3Center-CCA(0)'] = (" F'","2U'"," R2","2U ","3L ","2U'"," R2","2U ","3L'"," F ")
                self.myperms2['Oblique-Center-Adjacent3Center-BBD(0)'] = (" F ","3D'","2L'"," U2","2L ","3D ","2L'"," U2","2L "," F'")
                self.myperms2['Oblique-Center-Adjacent3Center-DDB(0)'] = (" F ","3U ","2R "," U2","2R'","3U'","2R "," U2","2R'"," F'")
                
                self.myperms2['Oblique-Center-Adjacent3Center-AAD(0)'] = ("2D "," R2","2D'","3R'","2D "," R2","2D'","3R ")
                self.myperms2['Oblique-Center-Adjacent3Center-CCB(0)'] = ("2U'"," R2","2U ","3L ","2U'"," R2","2U ","3L'")
                self.myperms2['Oblique-Center-Adjacent3Center-BBC(0)'] = ("3D'","2L'"," U2","2L ","3D ","2L'"," U2","2L ")
                self.myperms2['Oblique-Center-Adjacent3Center-DDA(0)'] = ("3U ","2R "," U2","2R'","3U'","2R "," U2","2R'")

                self.myperms2['Oblique-Center-Adjacent3Center-AAB(0)'] = ('3U ', "2L'", ' U2', '2L ', "3U'", "2L'", ' U2', '2L ')
                self.myperms2['Oblique-Center-Adjacent3Center-CCD(0)'] = ("3D'", '2R ', ' U2', "2R'", '3D ', '2R ', ' U2', "2R'")
                self.myperms2['Oblique-Center-Adjacent3Center-DDC(0)'] = ('2D ', ' R2', "2D'", '3L ', '2D ', ' R2', "2D'", "3L'")
                self.myperms2['Oblique-Center-Adjacent3Center-BBA(0)'] = ("2U'", ' R2', '2U ', "3R'", "2U'", ' R2', '2U ', '3R ')

                self.myperms2['Oblique-Center-Adjacent3Center-ADC(0)'] = ("2L'"," D'","3F'",' D ','2L '," D'",'3F ',' D ')
                self.myperms2['Oblique-Center-Adjacent3Center-CBA(0)'] = ("2R "," D'","3B ",' D ',"2R'"," D'","3B'",' D ')
                self.myperms2['Oblique-Center-Adjacent3Center-BAD(0)'] = ("2R "," D ","3F'"," D'","2R'"," D ","3F "," D'")
                self.myperms2['Oblique-Center-Adjacent3Center-DCB(0)'] = ("2L'"," D ","3B "," D'","2L "," D ","3B'"," D'")

                self.myperms2['Oblique-Center-Adjacent3Center-ABC(0)'] = (" U2","2L'"," D'","3F'",' D ','2L '," D'",'3F ',' D '," U2")
                self.myperms2['Oblique-Center-Adjacent3Center-CDA(0)'] = (" U2","2R "," D'","3B ",' D ',"2R'"," D'","3B'",' D '," U2")
                self.myperms2['Oblique-Center-Adjacent3Center-BCD(0)'] = (" U2","2R "," D ","3F'"," D'","2R'"," D ","3F "," D'"," U2")
                self.myperms2['Oblique-Center-Adjacent3Center-DAB(0)'] = (" U2","2L'"," D ","3B "," D'","2L "," D ","3B'"," D'"," U2")

                self.myperms2['Oblique-Center-Line3Center-AAD(0)'] = ("2R "," U ","3L "," U'","2R'"," U ","3L'"," U'")
                self.myperms2['Oblique-Center-Line3Center-CCB(0)'] = ("2L'"," U ","3R'"," U'","2L "," U ","3R "," U'")
                self.myperms2['Oblique-Center-Line3Center-ADA(0)'] = ("2R ", ' F ', '3U2', " F'", "2R'", ' F ', '3U2', " F'")
                self.myperms2['Oblique-Center-Line3Center-CBC(0)'] = ("2L'", ' F ', '3D2', " F'", '2L ', ' F ', '3D2', " F'")

                self.myperms2['Oblique-Center-Line3Center-ADD(0)'] = ("2L2"," F'","3R'"," F ","2L2"," F'","3R "," F ")
                self.myperms2['Oblique-Center-Line3Center-CBB(0)'] = ("2R2"," F'","3L "," F ","2R2"," F'","3L'"," F ")
                self.myperms2['Oblique-Center-Line3Center-AAA(0)'] = ('3U2', '2L ', '3F2', "2L'", ' F2', '2L ', '3F2', "2L'", ' F2', '3U2')
                self.myperms2['Oblique-Center-Line3Center-CCC(0)'] = ('3D2', "2R'", '3B2', '2R ', ' F2', "2R'", '3B2', '2R ', ' F2', '3D2')
                self.myperms2['Oblique-Center-Line3Center-CAA(0)'] = ('3D2', '2R ', '3B2', "2R'", ' B2', '2R ', '3B2', "2R'", ' B2', '3D2')
                self.myperms2['Oblique-Center-Line3Center-ACC(0)'] = ('3U2', "2L'", '3F2', '2L ', ' B2', "2L'", '3F2', '2L ', ' B2', '3U2')

                self.myperms2['Oblique-Center-Line3Center-ADB(0)'] = ('3D2', "2L'", ' U ', '2L ', '3D2', "2L'", " U'", '2L ')
                self.myperms2['Oblique-Center-Line3Center-CBD(0)'] = ('3U2', '2R ', ' U ', "2R'", '3U2', '2R ', " U'", "2R'")
                self.myperms2['Oblique-Center-Line3Center-ABD(0)'] = ('2L ', ' U ', "2L'", '3U2', '2L ', " U'", "2L'", '3U2')
                self.myperms2['Oblique-Center-Line3Center-CDB(0)'] = ("2R'", ' U ', '2R ', '3D2', "2R'", " U'", '2R ', '3D2')

                self.myperms2['Oblique-Center-Line3Center-AAC(0)'] = ('2L ', ' U2', "2L'", '3D2', '2L ', ' U2', "2L'", '3D2')
                self.myperms2['Oblique-Center-Line3Center-CCA(0)'] = ("2R'", ' U2', '2R ', '3U2', "2R'", ' U2', '2R ', '3U2')
                self.myperms2['Oblique-Center-Line3Center-ACA(0)'] = ('3U2', '2L ', ' U2', "2L'", '3U2', '2L ', ' U2', "2L'")
                self.myperms2['Oblique-Center-Line3Center-CAC(0)'] = ('3D2', "2R'", ' U2', '2R ', '3D2', "2R'", ' U2', '2R ')

                self.myperms2['Oblique-Center-Line3Center-ACB(0)'] = ('3F2', '2L ', ' D ', '3R ', " D'", "2L'", ' D ', "3R'", " D'", '3F2')
                self.myperms2['Oblique-Center-Line3Center-CAD(0)'] = ('3B2', "2R'", ' D ', "3L'", " D'", '2R ', ' D ', '3L ', " D'", '3B2')
                self.myperms2['Oblique-Center-Line3Center-ABC(0)'] = ('3F2', '2L ', ' F ', '3D2', " F'", "2L'", ' F ', '3D2', '3F2', " F'")
                self.myperms2['Oblique-Center-Line3Center-CDA(0)'] = ('3B2', "2R'", ' F ', '3U2', " F'", '2R ', ' F ', '3U2', '3B2', " F'")
                self.myperms2['Oblique-Center-Line3Center-ABB(0)'] = ('2F2', '2R2', " F'", "3L'", ' F ', '2R2', " F'", '3L ', '2F2', ' F ')
                self.myperms2['Oblique-Center-Line3Center-CDD(0)'] = ('2B2', '2L2', " F'", '3R ', ' F ', '2L2', " F'", "3R'", '2B2', ' F ')

                self.myperms2['Oblique-Center-Line3Center-AAB(0)'] = ('2F2', " F'", '2R2', " F'", "3L'", ' F ', '2R2', " F'", '3L ', '2F2', ' F2')
                self.myperms2['Oblique-Center-Line3Center-CCD(0)'] = ('2B2', " F'", '2L2', " F'", '3R ', ' F ', '2L2', " F'", "3R'", '2B2', ' F2')
                self.myperms2['Oblique-Center-Line3Center-ABA(0)'] = (' B2', '2F2', '3L ', ' B ', '2R2', " B'", "3L'", ' B ', '2R2', ' B ', '2F2')
                self.myperms2['Oblique-Center-Line3Center-CDC(0)'] = (' B2', '2B2', "3R'", ' B ', '2L2', " B'", '3R ', ' B ', '2L2', ' B ', '2B2')



            self.myperms2['OuterCenterBar-A'] = (' F2', '2R ', ' F2', ' D2', ' B2', '2L ', ' B2', ' D2')
            self.myperms2['OuterCenterBar-B'] = (' D2', ' B2', "2L'", ' B2', ' D2', ' F2', "2R'", ' F2')
            
            self.myperms2['OuterCenterBar-C'] = (" F'", '2R ', ' F2', ' D2', ' B2', '2L ', ' B2', ' D2', " F'")
            self.myperms2['OuterCenterBar-D'] = (' F ', '2R ', ' F2', ' D2', ' B2', '2L ', ' B2', ' D2', ' F ')

            self.myperms2['OuterCenterBar-E'] = (' U ', " F'", '2R ', ' F2', ' D2', ' B2', '2L ', ' B2', ' D2', " F'", " U'")
            self.myperms2['OuterCenterBar-F'] = (' U ', ' F ', '2R ', ' F2', ' D2', ' B2', '2L ', ' B2', ' D2', ' F ', " U'")
            self.myperms2['OuterCenterBar-G'] = (" U'", " F'", '2R ', ' F2', ' D2', ' B2', '2L ', ' B2', ' D2', " F'", ' U ')
            self.myperms2['OuterCenterBar-H'] = (" U'", ' F ', '2R ', ' F2', ' D2', ' B2', '2L ', ' B2', ' D2', ' F ', ' U ')
    
            self.myperms2['OuterCenterBar-W'] = ('2R ', ' F2', ' D2', ' B2', '2L ', '2R ', ' B2', ' D2', ' F2', '2L ')
            self.myperms2['OuterCenterBar-WW'] = (' F ', '2R ', ' F2', ' D2', ' B2', '2L ', '2R ', ' B2', ' D2', ' F2', '2L ', " F'")

            self.myperms2['OuterCenterBar-KA'] = ("2L'", ' B2', ' D2', ' F2', '2R2', ' F2', ' D2', ' B2', "2L'")
            self.myperms2['OuterCenterBar-KB'] = ("2L ", ' B2', ' D2', ' F2', '2R2', ' F2', ' D2', ' B2', "2L ")

            self.myperms2['OuterCenterBar-JA'] = ("2R "," U2"," F2"," D2","2L'"," D2"," F2"," U2","2R2")
            self.myperms2['OuterCenterBar-JB'] = ("2R2"," U2"," F2"," D2","2L "," D2"," F2"," U2","2R'")

            self.myperms2['OuterCenterBar-IA'] = (" B2","2R "," U2"," F2"," D2","2L'"," D2"," F2"," U2","2R2"," B2")
            self.myperms2['OuterCenterBar-IB'] = (" B2","2R2"," U2"," F2"," D2","2L "," D2"," F2"," U2","2R'"," B2")
            
            self.myperms2['OuterCenterBar-X'] = ("2L2"," F2"," U2"," F2","2L2"," F2"," U2"," F2")
            self.myperms2['OuterCenterBar-Y'] = (" F2"," U2"," F2","2L2"," F2"," U2"," F2","2L2")
            self.myperms2['OuterCenterBar-Z'] = (" U ","2L2"," F2"," U2"," F2","2L2"," F2"," U2"," F2"," U'")
            self.myperms2['OuterCenterBar-XX'] = ("2R2"," F2"," B2","2L2"," F2"," B2")
            self.myperms2['OuterCenterBar-ZZ'] = (" U ","2R2"," F2"," B2","2L2"," F2"," B2"," U'")

            

    def _register_myperms2_f2l_oll(self):
        """F2L/OLLやCenters条件に応じた手順群を登録する。"""
        # 命名メモ:
        # - OuterCenterBar / MidCenterBar は center の bar を動かす family。
        # - Adjacent3Center / Line3Center は 3面の center を動かす family。
        # - InOut / InIn / OutOut / Middle-* は各 center の相対位置関係を表す。
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

    
    def _init_single_move_and_rotate(self):
        self.single_and_rotate = [k for k in self.myperms.keys() if k[:10] == "SingleMove" or k[:6] == "Rotate"]
                
    def collect_single_move_and_rotate(self):
        return self.single_and_rotate

    def _init_cube_state_and_moves(self):
        """盤面初期化・move定義・piece番号表をまとめて構築する。"""
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
        self._init_piece_metadata()

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

    def _init_piece_metadata(self):
        """pieceの index 表・番号逆引き・完成色をまとめて初期化する。"""
        self._init_piece_indices()
        self._init_piece_lookup_tables()
        self._init_default_colors()

    def _init_piece_indices(self):
        """center / edge / corner の index 集合を作る。"""
        self.center_num = (self.size - 2) ** 2
        self.edge_pairs = self._build_edge_pairs()
        self.AB = AB[self.size]
        self.CL = self._build_corner_locations()
        self.center_index = self._build_center_indices()
        self.edge_index = self._build_edge_indices()
        self.corner_index = self._build_corner_indices()

    def _build_edge_pairs(self):
        """edge piece を構成する2面の基準位置を返す。"""
        return [((0,0),(2,0)),
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

    def _build_corner_locations(self):
        """corner piece を構成する3面の基準位置を返す。"""
        return [((0,0),(2,3),(4,0)),
                ((0,1),(4,3),(3,0)),
                ((0,2),(3,3),(5,0)),
                ((0,3),(5,3),(2,0)),
                ((1,0),(3,1),(4,2)),
                ((1,1),(4,1),(2,2)),
                ((1,2),(2,1),(5,2)),
                ((1,3),(5,1),(3,2))]

    def _build_center_indices(self):
        """center piece の index 一覧を返す。"""
        return [(i + self.surface_num * j,) for j in range(6) for i in range(4 * (self.size - 1),self.surface_num)]

    def _build_edge_indices(self):
        """edge piece の index 一覧を返す。"""
        return [(p[0][0] * self.surface_num + p[0][1] + 4 * ab[0],p[1][0] * self.surface_num + p[1][1] + 4 * ab[1]) for ab in self.AB for p in self.edge_pairs]

    def _build_corner_indices(self):
        """corner piece の index 一覧を返す。"""
        return [(cl[0][0] * self.surface_num + cl[0][1],cl[1][0] * self.surface_num + cl[1][1],cl[2][0] * self.surface_num + cl[2][1]) for cl in self.CL]

    def _init_piece_lookup_tables(self):
        """盤面 index から piece へ戻る逆引き表を作る。"""
        self.num_to_piece = {}
        for i in range(6 * self.surface_num):
            if i % self.surface_num < 4:
                self.num_to_piece[i] = [x for x in self.corner_index if i in x][0]
            elif i % self.surface_num < 4 * (self.size - 1):
                self.num_to_piece[i] = [x for x in self.edge_index if i in x][0]
            else:
                self.num_to_piece[i] = (i,)

    def _init_default_colors(self):
        """完成状態での各 piece の色並びを保存する。"""
        self.default_color = {}
        for x in self.center_index:
            self.default_color[x] = self.state_0[x[0]]
        for x in self.edge_index:
            self.default_color[x] = self.state_0[x[0]] + self.state_0[x[1]]
        for x in self.corner_index:
            self.default_color[x] = self.state_0[x[0]] + self.state_0[x[1]] + self.state_0[x[2]]

    def _init_color_keys_and_groups(self):
        """配色ID・入力次元・評価用グループベクトルを初期化する。"""
        self._init_piece_color_keys()
        self._apply_partial_solve_color_keys()
        self._init_piece_color_lists()
        self._init_input_vector_metadata()
        self._init_group_values()

    def _init_piece_color_keys(self):
        """edge / corner の色並びを整数IDへ変換する表を作る。"""
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

    def _apply_partial_solve_color_keys(self):
        """F2L / OLL / Edges / Cross 条件に応じて配色IDを上書きする。"""
        if self.F2L or self.Edges or self.Cross:
            self.edge_key['XX'] = 0
            self.corner_key['XXX'] = 0

        if self.OLL:
            self.edge_key['RX'] = 0
            self.edge_key['XR'] = 1
            self.corner_key['RXX'] = 0
            self.corner_key['XRX'] = 1
            self.corner_key['XXR'] = 2

    def _init_piece_color_lists(self):
        """ID順に並べた色並びリストを作る。"""
        # ID順に色並びを並べたリスト
        self.edge_colors = sorted(self.edge_key.keys(),key = lambda x :self.edge_key[x])
        self.corner_colors = sorted(self.corner_key.keys(),key = lambda x :self.corner_key[x])

    def _init_input_vector_metadata(self):
        """入力次元と完成状態特徴量を計算する。"""
        # 入力ベクトルの総次元（盤面情報の固定長表現）
        self.ips = 36*self.surface_num + 144 * self.size - 240
        
        # 完全解状態の特徴量（教師データ基準）
        self.perfect_data = self.makedata()

    def _init_group_values(self):
        """評価用グループごとのマスクベクトルと総和を作る。"""
        base_vector = self._empty_group_vector()
        self.group_val = {}
        self.total_val = {}
        group_names = self._group_name_map()

        if self.size % 2 == 1:
            self._init_group_values_for_odd_size(group_names, base_vector)
        else:
            self._init_group_values_for_even_size(group_names, base_vector)
        
        self._init_center_group_values(group_names, base_vector)
        
        self._set_group_aliases(group_names)

        # 各グループのマスク総和（スコア正規化等に利用）
        for key in group_names.values():
            self.total_val[key] = np.sum(self.group_val[key])
        for key in group_names.keys():
            self.total_val[key] = self.total_val[group_names[key]]

    def _init_group_values_for_odd_size(self, group_names, base_vector):
        """奇数サイズ用の Corner / MidEdge / Wing グループを初期化する。"""
        center_feature_start = 36 * self.center_num
        self.group_val[group_names['A']] = self._group_vector_slice(-192, None)
        self.group_val[group_names['B']] = self._group_vector_slice(center_feature_start, center_feature_start + 288)
        if self.size >= 5:
            self.group_val[group_names['C']] = self._group_vector_slice(center_feature_start + 288, center_feature_start + 864)
            if self.size == 7:
                self.group_val[group_names['c']] = self._group_vector_slice(center_feature_start + 864, -192)
            else:
                self._set_empty_group(group_names['c'], base_vector)
        else:
            self._set_empty_group(group_names['C'], base_vector)
            self._set_empty_group(group_names['c'], base_vector)

    def _init_group_values_for_even_size(self, group_names, base_vector):
        """偶数サイズ用の Corner / MidEdge / Wing グループを初期化する。"""
        center_feature_start = 36 * self.center_num
        self.group_val[group_names['A']] = self._group_vector_slice(-192, None)
        self._set_empty_group(group_names['B'], base_vector)
        if self.size >= 4:
            self.group_val[group_names['C']] = self._group_vector_slice(center_feature_start, center_feature_start + 576)
            if self.size == 6:
                self.group_val[group_names['c']] = self._group_vector_slice(center_feature_start + 576, -192)
            else:
                self._set_empty_group(group_names['c'], base_vector)
        else:
            self._set_empty_group(group_names['C'], base_vector)
            self._set_empty_group(group_names['c'], base_vector)

    def _init_center_group_values(self, group_names, base_vector):
        """X / Plus / Oblique / CoreCenter の group mask を初期化する。"""
        for key in ['D','d','E','e','F','f','G']:
            self.group_val[group_names[key]] = self._center_group_vector(key, base_vector)

    def _center_group_vector(self, key, base_vector):
        """center 系 group key に対応する mask ベクトルを返す。"""
        if self.Centers:
            return base_vector.copy()
        group_vector = base_vector.copy()
        for face_index in range(6):
            for group_index in self.group_indices[key]:
                vector_index = face_index + 6 * (face_index * self.center_num + group_index - 4 * (self.size - 1))
                group_vector[0,vector_index] = 1
        return group_vector

    def _set_empty_group(self, group_name, base_vector):
        """指定した group に空ベクトルを代入する。"""
        self.group_val[group_name] = base_vector.copy()

    def _empty_group_vector(self):
        """評価用グループの空ベクトルを返す。"""
        return np.zeros((1,self.ips),dtype = 'f')

    def _group_vector_slice(self, start, end):
        """perfect_data の指定区間だけを立てたグループベクトルを返す。"""
        group_vector = self._empty_group_vector()
        group_vector[0,start:end] = self.perfect_data[start:end]
        return group_vector

    def _group_name_map(self):
        """短い group key と意味ベース名の対応を返す。"""
        return {
            'A': 'Corner',
            'B': 'MidEdge',
            'C': 'Wing-Layer2',
            'c': 'Wing-Layer3',
            'D': 'XCenter-Layer2',
            'd': 'XCenter-Layer3',
            'E': 'PlusCenter-Layer2',
            'e': 'PlusCenter-Layer3',
            'F': 'ObliqueCenter-A',
            'f': 'ObliqueCenter-B',
            'G': 'CoreCenter',
        }

    def _set_group_aliases(self, group_names):
        """既存コード互換のため、旧 short key でも同じベクトルを引けるようにする。"""
        for short_key, long_key in group_names.items():
            self.group_val[short_key] = self.group_val[long_key]
        
        
    


    def _init_myperms_index(self):
        """(piece, color) から候補 myperm 群を引く逆引き表を構築する。"""
        self._init_empty_myperms_index()
        self._register_myperms_index_entries()
        self._init_myperms_order()

    def _init_empty_myperms_index(self):
        """未一致色ごとの空の myperm 候補リストを用意する。"""
        self.myperms_dict = {}
        self._init_empty_center_myperms_index()
        self._init_empty_edge_myperms_index()
        self._init_empty_corner_myperms_index()

    def _init_empty_center_myperms_index(self):
        """center piece 用の逆引きキーを作る。"""
        for piece in self.center_index:
            for color in ['R','O','B','G','Y','W','X']:
                if self.default_color[piece] != color:
                    self.myperms_dict[(piece,color)] = []

    def _init_empty_edge_myperms_index(self):
        """edge piece 用の逆引きキーを作る。"""
        for piece in self.edge_index:
            for color in self.edge_key:
                if self.default_color[piece] != color:
                    self.myperms_dict[(piece,color)] = []

    def _init_empty_corner_myperms_index(self):
        """corner piece 用の逆引きキーを作る。"""
        for piece in self.corner_index:
            for color in self.corner_key:
                if self.default_color[piece] != color:
                    self.myperms_dict[(piece,color)] = []

    def _register_myperms_index_entries(self):
        """各 myperm を1回ずつ適用し、変化する piece/color に登録する。"""
        for key, moves in self.myperms.items():
            if self._skip_myperms_index_key(key):
                continue
            self._register_single_myperms_index_entry(key, moves)

    def _skip_myperms_index_key(self, key):
        """逆引き登録から除外する myperm 名か判定する。"""
        return key[:3] in ["L2E","L4I","L4J"] or key[:5] in ['Super']

    def _register_single_myperms_index_entry(self, key, moves):
        """1つの myperm を適用して、変化した piece/color に key を追加する。"""
        self._apply_inverse_moves(moves)
        self._register_changed_center_entries(key)
        self._register_changed_edge_entries(key)
        self._register_changed_corner_entries(key)
        self._apply_moves(moves)

    def _apply_inverse_moves(self, moves):
        """逆順の move を適用して観測用の盤面へ移す。"""
        for move in self.invert_moves(moves):
            self.make_move(move)

    def _apply_moves(self, moves):
        """通常順の move を適用して盤面を元へ戻す。"""
        for move in moves:
            self.make_move(move)

    def _register_changed_center_entries(self, key):
        """色が変化した center piece に myperm key を登録する。"""
        for piece in self.center_index:
            color = self.state[piece[0]]
            if color != self.default_color[piece]:
                self.myperms_dict[(piece,color)].append(key)

    def _register_changed_edge_entries(self, key):
        """色が変化した edge piece に myperm key を登録する。"""
        for piece in self.edge_index:
            color = self.state[piece[0]] + self.state[piece[1]]
            if color != self.default_color[piece]:
                self.myperms_dict[(piece,color)].append(key)

    def _register_changed_corner_entries(self, key):
        """色が変化した corner piece に myperm key を登録する。"""
        for piece in self.corner_index:
            color = self.state[piece[0]] + self.state[piece[1]] + self.state[piece[2]]
            if color != self.default_color[piece]:
                self.myperms_dict[(piece,color)].append(key)

    def _init_myperms_order(self):
        """評価用の group 順序インデックスを作る。"""
        self.myperms_order = {}
        group_names = self._group_name_map()
        for key in ['A','B','C','c','D','d','E','e','F','f','G']:
            indices = self._group_order_indices(key)
            self.myperms_order[group_names[key]] = indices
            self.myperms_order[key] = indices

    def _group_order_indices(self, key):
        """1つの group key に対応する盤面 index 順序を返す。"""
        indices = []
        for face_index in [0,1,2,3,4,5]:
            indices += list(np.array(self.group_indices[key]) + self.surface_num * face_index)
        return indices
                


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
            self.state = np.array(list(S),dtype = str)
        else:
            self.state = np.array(S,dtype = str)
