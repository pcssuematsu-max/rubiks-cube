"""Main Tkinter application frame."""

import pickle
from functools import reduce

import numpy as np
import tkinter as Tk

from ai.rubiks_ai import Rubiks_3_AI
from megaminx.cube import MegaminxCube
from cube.rubiks_cube import Rubiks_3
from managers.debug_analysis import DebugAnalysisManager
from managers.last_perms_reporter import LastPermsReporter
from managers.learn_manager import LearnManager
from managers.myperm_manager import MyPermManager
from managers.param_manager import ParamManager
from managers.search_data import SearchDataManager
from managers.solve_session import SolveSessionManager, SolveSessionState
from model.search_result import data
from ui.control_panel import ControlPanel
from ui.dialogs import LpShowKeyButton, ParamEditorDialog
from ui.frame_config import FrameConfig
from ui.megaminx.state_viewer import MegaminxStateViewer
from ui.viewers import (
    LogViewer,
    MoveButton,
    MoveViewer,
    ProbViewer,
    StateViewer,
    SuccessViewer,
)

np.set_printoptions(suppress=True)


def build_default_bootstrap_datas(cube_size):
    """既定の追加学習データ用手順列を返す。"""
    cube = Rubiks_3(size = cube_size)
    bootstrap_datas = []

    if cube_size >= 4:
        bootstrap_datas += [("2L'","2R'",'2D2','2R ',' U ',"2R'",'2D2','2R '," U'"),
                            ("2B ","2R ","2U ","2R'"," U'","2R ","2U'","2R'"," U "),
                            ("2U ","2D ","2R2","2U ","2D'","2R2"),
                            ("2R ","2F2","2R ","2F2","2U2","2R ","2U2"),
                            ] * 20

    if cube_size in [5,7]:
        bootstrap_datas += [("2L'","2R'",' E2','2R ',' U ',"2R'",' E2','2R '," U'"),
                            ("2B ","2R "," E'","2R'"," U'","2R "," E ","2R'"," U "),
                            ("2U ","2D "," M2","2U ","2D'"," M2"),
                            ("2R "," S2","2R "," S2"," E2","2R "," E2"),
                            ] * 20

    if cube_size >= 6:
        bootstrap_datas += [("2L'","2R'",'3D2','2R ',' U ',"2R'",'3D2','2R '," U'"),
                            ("2B ","2R ","3U ","2R'"," U'","2R ","3U'","2R'"," U "),
                            ("2U ","2D ","3R2","2U ","2D'","3R2"),
                            ("2R ","3F2","2R ","3F2","3U2","2R ","3U2"),
                            ] * 20


    if cube_size >= 6:
        bootstrap_datas = bootstrap_datas + [cube.flip_inside_moves(x) for x in bootstrap_datas]

    return (
        bootstrap_datas
        + [cube.transform(x,48) for x in bootstrap_datas]
        + [cube.transform(x,24) for x in bootstrap_datas]
        + [cube.transform(x,72) for x in bootstrap_datas]
    )


class Frame(Tk.Frame):
    def __init__(self, config = None):
        if config is None:
            config = FrameConfig()

        self.config = config
        self.puzzle_type = config.puzzle_type
        self.cube_size = config.cube_size
        Tk.Frame.__init__(self,None)
        self.master.title('Megaminx' if self.puzzle_type == 'megaminx' else 'Rubiks')
        self.cube = self._create_cube(config)

        # Register built-in scramble candidates and initialize stage-level state.
        self._register_initial_scrambles(
            config.initial_scramble_groups,
            F2L = config.F2L,
            OLL = config.OLL,
            Centers = config.Centers,
            Edges = config.Edges,
            Cross = config.Cross,
        )
        self.transform_random = config.transform_random
        self.search3_progress = self._build_search3_progress_flags(config.search3_progress)
        self._init_stage_settings()

        # Build AI instances and apply experiment-specific runtime settings.
        self.AIs = self._create_ai_collection(config.ai_search_modes)
        self._init_ai_state(config.cube_size, config.priority_list)
        self._link_ai_data()
        self._apply_ai_runtime_settings(
            lrs = config.lrs,
            wdlrs = config.wdlrs,
            skip_search = config.skip_search,
            weight_decay = config.weight_decay,
            adam = config.adam,
            lr_vs = config.lr_vs,
            lr_hs = config.lr_hs,
            out_cs = config.out_cs,
            search3_cs = config.search3_cs,
            pv_ratios = config.pv_ratios,
            transform_idx = config.transform_idx,
            flip_inside_idx = config.flip_inside_idx,
        )

        # Prepare myperm lookup tables and bootstrap training data.
        self._init_myperms_metadata()
        if self.puzzle_type == 'cube':
            self._append_bootstrap_datas(config.bootstrap_datas)

        self.grad_index = 0
        self.grad_mode = "IG"
        self.grad_layer = "WO_V"

        # Construct managers first, then create the visible UI widgets.
        self._init_managers()
        control_font = self._build_control_panel()
        self._build_move_pad(control_font)
        self._build_viewers(config.cube_size)

        # Finalize solve/runtime state after all dependencies are in place.
        self._init_runtime_state()
        
        
    def _register_initial_scrambles(self, initial_scramble_groups = None, F2L = False, OLL = False, Centers = False, Edges = False, Cross = False):
        """初期 scramble 候補を stage ごとの registry に登録する。"""
        if initial_scramble_groups is None:
            initial_scramble_groups = self._build_default_scramble_groups(F2L = F2L, OLL = OLL, Centers = Centers, Edges = Edges, Cross = Cross)

        for _ in range(8):
            self.cube.create_new_set()

        for stage_index, scramble_group in enumerate(initial_scramble_groups):
            for moves in scramble_group:
                normalized_moves = self._normalize_move_sequence(moves)
                self.cube.my_scrambles2[stage_index][normalized_moves[-1]].add(normalized_moves)

    def _build_default_scramble_groups(self, F2L = False, OLL = False, Centers = False, Edges = False, Cross = False):
        """cube size と mode に応じた既定の初期 scramble 候補群を作る。"""
        S0 = []
        S1 = []
        S2 = []
        S3 = []
        S4 = []
        S5 = []
        S6 = []
        S7 = []

        return (S0, S1, S2, S3, S4, S5, S6, S7)

    def _create_cube(self, config):
        """puzzle type に応じた cube 実装を生成する。"""
        if self.puzzle_type == 'megaminx':
            return MegaminxCube(
                size = config.cube_size,
                F2L = config.F2L,
                OLL = config.OLL,
                Centers = config.Centers,
                Edges = config.Edges,
                Cross = config.Cross,
            )

        return Rubiks_3(
            size = config.cube_size,
            F2L = config.F2L,
            OLL = config.OLL,
            Centers = config.Centers,
            Edges = config.Edges,
            Cross = config.Cross,
        )

    def _init_stage_settings(self):
        """stage 進行と scramble mode の初期値を設定する。"""
        self.scramble_mode = ['myperms']

        self.stage = 0
        self.stage_num = len(self.scramble_mode)
        self.N = 0
        self.AI_idx = 0
        self.value_target_gamma = 0.5 ** (1/20)
        self.perf_num = np.zeros(self.stage_num,dtype = 'i')

    @staticmethod
    def default_ai_search_modes():
        """既定の AI mode 構成を返す。"""
        return ['search2'] * 10 + ['search3'] * 10

    def _create_ai_collection(self, ai_search_modes = None):
        """指定 mode 列に従って AI 配列を生成する。"""
        if ai_search_modes is None:
            ai_search_modes = self.default_ai_search_modes()

        mid_size = [512] * 8
        return [
            Rubiks_3_AI(mid_size,cube_size = self.cube_size,Activation = 'ReLU',cube = self.cube,search_mode = search_mode)
            for search_mode in ai_search_modes
        ]

    def _init_ai_state(self, cube_size, priority_list):
        """AI 配列数に依存する基本状態と myval AI を初期化する。"""
        self.AInum = len(self.AIs)
        self.level = 1 * np.ones((self.AInum,self.stage_num),dtype = 'i')
        self.success = np.zeros((self.AInum,),dtype = 'i')
        self.move_keys = self.cube.move_keys
        self.my_scramble = []
        self.AI_idx = 0
        self._init_myval_ai(cube_size)

        if priority_list is not None:
            self.priority_list = self._resolve_priority_list(priority_list)
        else:
            self.priority_list = self._default_priority_list()

    def _init_myval_ai(self, cube_size):
        """myval 用の補助 AI を既定パラメータで初期化する。"""
        self.myval_AI = Rubiks_3_AI([2],cube_size = cube_size,cube = self.cube,Batch_Normalize = True)
        self.myval_AI.params['BNg1'][:] = 1
        self.myval_AI.params['BNb1'][:] = 0
        self.myval_AI.params['BNgV'][:] = 1
        self.myval_AI.params['BNbV'][:] = 0
        self.myval_AI.params['W1'][:] = 0
        self.myval_AI.params['B1'][:] = 0
        self.myval_AI.params['WO_V'][:] = 1
        self._sync_value_target_gamma()
        self.myval_AI.params['W1'][0] = self.cube.makedata()
        self.myval_AI.params['W1'][0,-192:] *= 1
        self.myval_AI.params['WM_V'] *= 0
        for i in range(self.myval_AI.params['WM_V'].shape[0]):
            self.myval_AI.params['WM_V'][i,i] = 1
        self.myval_AI.mark_params_dirty()

    def _build_search3_progress_flags(self, search3_progress):
        """AI ごとの Search3 progress 表示フラグ列を返す。"""
        if search3_progress is None:
            return [True] * len(self.AIs)
        return list(search3_progress)

    def _default_priority_list(self):
        """puzzle type ごとの既定 priority list を返す。"""
        if self.puzzle_type == 'megaminx':
            return [['Corner', 'MidEdge']] * self.AInum

        return [[
            'CoreCenter', 'ObliqueCenter-A', 'PlusCenter-Layer2',
            'XCenter-Layer2', 'ObliqueCenter-B', 'PlusCenter-Layer3',
            'XCenter-Layer3', 'Wing-Layer2', 'Wing-Layer3',
            'Corner', 'MidEdge',
        ]] * self.AInum

    def _resolve_priority_list(self, priority_list):
        """Filter configured priority groups to those supported by the current puzzle."""
        available_groups = set(getattr(self.cube, 'group_val', {}).keys())
        if not available_groups:
            return self._default_priority_list()

        resolved = []
        for group_row in priority_list:
            filtered_row = [group for group in group_row if group in available_groups]
            if not filtered_row:
                filtered_row = self._default_priority_list()[0].copy()
            resolved.append(filtered_row)
        return resolved

    def _link_ai_data(self):
        """全 AI と myval AI を cube / datas に接続する。"""
        for i in range(self.AInum):
            if i > 0:
                self.AIs[i].datas = self.AIs[0].datas
            self.AIs[i].cube = self.cube

        self.myval_AI.cube = self.cube
        self.myval_AI.datas = self.AIs[0].datas

    def _apply_ai_runtime_settings(self,
                                   lrs = None,
                                   wdlrs = None,
                                   skip_search = None,
                                   weight_decay = None,
                                   adam = None,
                                   lr_vs = None,
                                   lr_hs = None,
                                   out_cs = None,
                                   search3_cs = None,
                                   pv_ratios = None,
                                   transform_idx = None,
                                   flip_inside_idx = None):
        """AI ごとの学習・探索設定と transform 設定を適用する。"""
        for i in range(self.AInum):
            if lrs is not None:
                self.AIs[i].lr = lrs[i]
            if wdlrs is not None:
                self.AIs[i].wdlr = wdlrs[i]
            if skip_search is not None:
                self.AIs[i].skip_search = skip_search[i]
            if weight_decay is not None:
                self.AIs[i].weight_decay = weight_decay[i]
            if adam is not None:
                self.AIs[i].adam = adam[i]

            if lr_vs is not None:
                self.AIs[i].lr_v = lr_vs[i]
            else:
                self.AIs[i].lr_v = 0.99

            if lr_hs is not None:
                self.AIs[i].lr_h = lr_hs[i]
            else:
                self.AIs[i].lr_h = 0.99

            if out_cs is not None:
                self.AIs[i].out_C = out_cs[i]
            else:
                self.AIs[i].out_C = 1.0

            if search3_cs is not None:
                self.AIs[i].search3_C = search3_cs[i]
            else:
                self.AIs[i].search3_C = 0.05

            if pv_ratios is not None:
                self.AIs[i].PV_ratio = pv_ratios[i]
            else:
                self.AIs[i].PV_ratio = 1.0

        if transform_idx is not None:
            self.transform_idx = transform_idx
        else:
            self.transform_idx = [0] * self.AInum

        if flip_inside_idx is not None:
            self.flip_inside_idx = flip_inside_idx
        else:
            self.flip_inside_idx = [False] * self.AInum

    def _init_myperms_metadata(self):
        """myperms の参照用メタデータと逆引き辞書を構築する。"""
        self.myval_AI.myperms = self.cube.myperms
        self.myperms_keys = sorted(list(self.cube.myperms.keys()))
        self.myperms_vals = set(self.cube.myperms.values())
        self.myperms_len = len(self.cube.myperms)
        self.myperms_col = self._build_myperms_col()

    def _build_myperms_col(self):
        """適用後 state から myperm 名を引く逆引き辞書を作る。"""
        myperms_col = {}
        for key in self.cube.myperms.keys():
            for m in self.cube.invert_moves(self.cube.myperms[key]):
                self.cube.make_move(m)

            state_key = reduce(lambda x,y: x+y,self.cube.state)
            if state_key not in myperms_col:
                myperms_col[state_key] = key

            for m in self.cube.myperms[key]:
                self.cube.make_move(m)

        return myperms_col

    def _append_bootstrap_datas(self, bootstrap_datas = None):
        """追加の初期学習データを登録し、全 AI の index を張り直す。"""
        if bootstrap_datas is None:
            bootstrap_datas = build_default_bootstrap_datas(self.cube_size)

        for moves in bootstrap_datas:
            d = data(moves,self.cube.invert_moves(moves),None)
            d.succeeded = True
            self.AIs[0].datas.append(d)

        for i in range(self.AInum):
            self.AIs[i].indices = list(range(len(self.AIs[0].datas)))

    def _init_managers(self):
        """manager 群と solve state を生成する。"""
        self.param_manager = ParamManager(self)
        self.learn_manager = LearnManager(self)
        self.last_perms_reporter = LastPermsReporter(self)
        self.debug_analysis_manager = DebugAnalysisManager(self)
        self.solve_session_manager = SolveSessionManager(self)
        self.search_data_manager = SearchDataManager(self)
        self.myperm_manager = MyPermManager(self)
        self.solve_state = SolveSessionState()

    def _build_control_panel(self):
        """上部 control panel を生成して alias を束縛する。"""
        self.control_panel = ControlPanel(self,self)
        self.control_buttons = self.control_panel
        self.control_panel.grid(row = 0,column = 0,columnspan = 4,sticky = 'ew')
        self._bind_control_panel_aliases()
        return self.control_panel.font

    def _build_move_pad(self, font):
        """手動 move 用の別ウィンドウを生成する。"""
        self.move_window = Tk.Toplevel(self)
        self.move_window.title('Manual Moves')
        self.move_window.protocol('WM_DELETE_WINDOW',self.hide_move_pad)
        self.move_window.withdraw()
        self.move_buttons = Tk.Frame(self.move_window,relief = Tk.RIDGE,bd = 4)
        self.move_buttons.pack(fill = 'both',expand = True)
        self.close_move_pad_button = Tk.Button(
            self.move_buttons,
            text = 'Close',
            font = font,
            padx = 1,
            pady = 1,
            command = self.hide_move_pad,
        )
        self.close_move_pad_button.grid(row = 0,column = 0,columnspan = len(self.move_keys) // 9 + 1,sticky = 'ew')

        self.movebuttons = {}
        for i, move_key in enumerate(self.move_keys):
            self.movebuttons[move_key] = MoveButton(self.move_buttons,move_key,self.cube,font,self)
            self.movebuttons[move_key].grid(row = i % 9 + 1,column = i // 9)

    def _build_viewers(self, cube_size):
        """state/move/prob/success viewer を生成して配置する。"""
        if self.puzzle_type == 'megaminx':
            viewer_class = MegaminxStateViewer
            self.SV = viewer_class(self)
            self.grad_viewer_positive = viewer_class(self, mini_mode = True)
            self.grad_viewer_negative = viewer_class(self, mini_mode = True)
        else:
            viewer_class = StateViewer
            self.SV = viewer_class(self,cube_size)
            self.grad_viewer_positive = viewer_class(self,cube_size,mini_mode = True)
            self.grad_viewer_negative = viewer_class(self,cube_size,mini_mode = True)

        self.SV.grid(row = 1,column = 0,columnspan = 2)
        self.grad_viewer_positive.grid(row = 2,column = 0)
        self.grad_viewer_negative.grid(row = 2,column = 1)
        self.MV = MoveViewer(self)
        self.MV.grid(row = 1,column = 2,columnspan = 2)

        self.PV = ProbViewer(self,self._display_move_keys(self.move_keys))
        self.PV.grid(row = 2,column = 2,sticky = 'nw')
        self.success_viewer = SuccessViewer(self,self.AInum)
        self.success_viewer.grid(row = 2,column = 3,sticky = 'nsew')
        self.success_viewer.put_summary(self.success,self.N,self.AI_idx)
        self.log_viewer = LogViewer(self)
        self.log_viewer.grid(row = 3,column = 2,columnspan = 2,sticky = 'nsew')

    def _init_runtime_state(self):
        """UI 起動直後の runtime 状態を初期化する。"""
        self.stop = False
        self.last_perms = {}
        self.last_perms_changed_number = {}
        self.solve_state.reset_session()
        self.data_len = len(self.AIs[0].datas)

    def _display_move_keys(self, move_keys):
        """Return move labels in puzzle-specific display notation when available."""
        if hasattr(self.cube, 'format_moves'):
            return tuple(self.cube.format_moves(move_keys))
        return tuple(move_keys)

    def display_move_rows(self, move_rows):
        """Return move rows in puzzle-specific display notation when available."""
        if not hasattr(self.cube, 'format_moves'):
            return move_rows
        return [tuple(self.cube.format_moves(moves)) for moves in move_rows]

    def display_move_sequence(self, moves):
        """Return one move sequence in puzzle-specific display notation when available."""
        if hasattr(self.cube, 'format_moves'):
            return tuple(self.cube.format_moves(moves))
        return tuple(moves)

    def _normalize_move_sequence(self, moves):
        """Normalize a move sequence for puzzle-specific internal storage when supported."""
        if hasattr(self.cube, 'normalize_move_key'):
            return tuple(self.cube.normalize_move_key(move) for move in moves)
        return tuple(moves)

    def append_log(self, message):
        """GUI 上のログビューアへ 1 行追記する。"""
        if isinstance(message, (tuple, list)) and hasattr(self.cube, 'format_moves'):
            message = self.cube.format_moves(message)
        self.log_viewer.append_line(message)
        self.update()

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
            'edit_params_button',
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
        E_key = Tk.Entry(master = Frame,width = 20)
        E_key.grid(row = 0,column = 0)
        E_length = Tk.Entry(master = Frame,width = 20)
        E_length.grid(row = 1,column = 0)
        B = LpShowKeyButton(Frame,self,E_key,E_length)
        B.grid(row = 2,column = 0)

    def open_param_editor(self):
        ParamEditorDialog(self)


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
