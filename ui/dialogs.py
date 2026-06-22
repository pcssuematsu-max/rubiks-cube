"""Small dialog button widgets."""

import tkinter as Tk
from tkinter.scrolledtext import ScrolledText

import numpy as np

from cube.rubiks_cube import Rubiks_3
from cto.cube import CtoCube
from fto.cube import FtoCube
from megaminx.cube import MegaminxCube
from pyraminx.cube import MasterPyraminxCube, PyraminxCube
from skewb.cube import SkewbCube
from ui.cto.state_viewer import CtoStateViewer
from ui.fto.state_viewer import FtoStateViewer
from ui.megaminx.state_viewer import MegaminxStateViewer
from ui.pyraminx.state_viewer import PyraminxStateViewer
from ui.skewb.state_viewer import SkewbStateViewer
from ui.viewers import StateViewer

class MakeMypermOkButton(Tk.Button):
    def __init__(self,master,frame,entry):
        Tk.Button.__init__(self,master,text = 'OK',command = self.make_myperm)
        self.frame = frame
        self.entry = entry
        self.master = master

    def make_myperm(self):
        text = self.entry.get()
        self.frame.myperm_manager.apply_named_myperm(text)
        self.master.destroy()


class LpShowKeyButton(Tk.Button):
    def __init__(self,master,frame,entry_key,entry_length):
        Tk.Button.__init__(self,master,text = 'Show',command = self.show_key)
        self.frame = frame
        self.entry_key = entry_key
        self.entry_length = entry_length
        self.master = master

    def show_key(self):
        text_key = self.entry_key.get().strip()
        text_length = self.entry_length.get().strip()
        if text_length == '':
            length = None
        else:
            length = int(text_length)
        self.frame.lp_show(text_key,length)
        self.master.destroy()


# Backward-compatible aliases during dialog rename migration.
make_myperm_OK = MakeMypermOkButton
lp_show_key = LpShowKeyButton


class ParamEditorDialog(Tk.Toplevel):
    """AI parameter viewer/editor dialog."""

    def __init__(self, frame):
        Tk.Toplevel.__init__(self, frame)
        self.frame = frame
        self.title('param editor')
        self.font = ('Century Gothic', 12, 'bold')
        self.ai_index_var = Tk.StringVar(value = self._default_ai_text())
        self.param_key_var = Tk.StringVar()
        self.param_index_var = Tk.StringVar(value = '')
        self.param_value_var = Tk.StringVar(value = '')
        self.summary_var = Tk.StringVar(value = '')
        self.status_var = Tk.StringVar(value = '')
        self._build_widgets()
        self._refresh_param_keys()

    def _default_ai_text(self):
        text = self.frame.param_index_var.get().strip()
        if text != '':
            return text.split(',')[0].strip()
        return str(self.frame.AI_idx)

    def _build_widgets(self):
        Tk.Label(self, text = 'AI idx', font = self.font).grid(row = 0, column = 0, sticky = 'e')
        Tk.Entry(self, textvariable = self.ai_index_var, font = self.font, width = 8).grid(row = 0, column = 1, sticky = 'ew')
        Tk.Button(self, text = 'refresh', font = self.font, command = self._refresh_param_keys).grid(row = 0, column = 2, sticky = 'ew')

        Tk.Label(self, text = 'param', font = self.font).grid(row = 1, column = 0, sticky = 'e')
        self.param_menu = Tk.OptionMenu(self, self.param_key_var, '')
        self.param_menu.configure(font = self.font)
        self.param_menu.grid(row = 1, column = 1, columnspan = 2, sticky = 'ew')

        Tk.Label(self, text = 'index', font = self.font).grid(row = 2, column = 0, sticky = 'e')
        Tk.Entry(self, textvariable = self.param_index_var, font = self.font).grid(row = 2, column = 1, sticky = 'ew')
        Tk.Button(self, text = 'load value', font = self.font, command = self._load_value).grid(row = 2, column = 2, sticky = 'ew')

        Tk.Label(self, text = 'value', font = self.font).grid(row = 3, column = 0, sticky = 'e')
        Tk.Entry(self, textvariable = self.param_value_var, font = self.font).grid(row = 3, column = 1, sticky = 'ew')
        Tk.Button(self, text = 'apply', font = self.font, command = self._apply_value).grid(row = 3, column = 2, sticky = 'ew')

        Tk.Label(self, textvariable = self.summary_var, justify = Tk.LEFT, anchor = 'w').grid(row = 4, column = 0, columnspan = 3, sticky = 'ew')

        self.preview = ScrolledText(self, width = 72, height = 12, font = ('Courier', 11))
        self.preview.grid(row = 5, column = 0, columnspan = 3, sticky = 'nsew')
        self.preview.configure(state = Tk.DISABLED)

        Tk.Label(self, textvariable = self.status_var, justify = Tk.LEFT, anchor = 'w', fg = '#7A1F1F').grid(row = 6, column = 0, columnspan = 3, sticky = 'ew')

        for column in range(3):
            self.grid_columnconfigure(column, weight = 1)
        self.grid_rowconfigure(5, weight = 1)

        self.param_key_var.trace_add('write', lambda *_: self._refresh_preview())

    def _selected_ai_index(self):
        return self.frame.param_manager.selected_index(self.ai_index_var.get(), default = self.frame.AI_idx)

    def _refresh_param_keys(self):
        ai_index = self._selected_ai_index()
        keys = self.frame.param_manager.param_keys(ai_index)
        menu = self.param_menu['menu']
        menu.delete(0, 'end')
        for key in keys:
            menu.add_command(label = key, command = lambda value = key: self.param_key_var.set(value))
        if keys:
            current = self.param_key_var.get()
            self.param_key_var.set(current if current in keys else keys[0])
        self.status_var.set('')
        self._refresh_preview()

    def _refresh_preview(self):
        key = self.param_key_var.get()
        if key == '':
            return
        ai_index = self._selected_ai_index()
        summary = self.frame.param_manager.param_summary(ai_index, key)
        self.summary_var.set(
            f"shape={summary['shape']} size={summary['size']} dtype={summary['dtype']} "
            f"min={summary['min']:.6g} max={summary['max']:.6g} "
            f"mean={summary['mean']:.6g} std={summary['std']:.6g}"
        )
        preview_text = self.frame.param_manager.param_preview(ai_index, key)
        self.preview.configure(state = Tk.NORMAL)
        self.preview.delete('1.0', Tk.END)
        self.preview.insert(Tk.END, preview_text)
        self.preview.configure(state = Tk.DISABLED)

    def _load_value(self):
        key = self.param_key_var.get()
        ai_index = self._selected_ai_index()
        try:
            value = self.frame.param_manager.param_value(ai_index, key, self.param_index_var.get())
        except ValueError as exc:
            self.status_var.set(str(exc))
            return
        self.param_value_var.set(f'{value:.8g}')
        self.status_var.set('')

    def _apply_value(self):
        key = self.param_key_var.get()
        ai_index = self._selected_ai_index()
        try:
            value = self.frame.param_manager.set_param_value(
                ai_index,
                key,
                self.param_index_var.get(),
                self.param_value_var.get(),
            )
        except ValueError as exc:
            self.status_var.set(str(exc))
            return
        self.status_var.set(f'updated {key} = {value:.8g}')
        self._refresh_preview()
        self.frame.append_log(
            f'param updated: ai={ai_index} key={key} index={self.param_index_var.get() or "()"} value={value:.8g}'
        )


class ToolsDialog(Tk.Toplevel):
    """画面外へ追い出した補助操作をまとめる小さいツールパネル。"""

    def __init__(self, frame):
        Tk.Toplevel.__init__(self, frame)
        self.frame = frame
        self.title('tools')
        self.font = ('Century Gothic', 12, 'bold')
        self._build_widgets()

    def _build_widgets(self):
        buttons = [
            ('make myperm', self.frame.make_myperm),
            ('edit params', self.frame.open_param_editor),
            ('dataset inspector', self.frame.open_dataset_inspector),
            ('attention analysis', self.frame.analyze_transformer_attention),
            ('embedding analysis', self.frame.analyze_transformer_embedding),
            ('lpk', self.frame.lpk),
            ('lp show', self.frame.lp_show_by_button),
            ('manual moves', self.frame.toggle_move_pad),
        ]
        for row_index, (text, command) in enumerate(buttons):
            Tk.Button(self, text = text, font = self.font, command = command).grid(
                row = row_index,
                column = 0,
                sticky = 'ew',
                padx = 4,
                pady = 2,
            )
        self.grid_columnconfigure(0, weight = 1)


class AnalysisScoresDialog(Tk.Toplevel):
    """Occlusion などのスコア一覧を表示するダイアログ。"""

    def __init__(self, frame):
        Tk.Toplevel.__init__(self, frame)
        self.title('analysis scores')
        self.geometry('420x320')
        self.text = ScrolledText(self, width = 60, height = 18, font = ('Menlo', 11))
        self.text.pack(fill = 'both', expand = True)
        self.text.configure(state = Tk.DISABLED)

    def set_content(self, title, rows):
        self.title(title)
        self.text.configure(state = Tk.NORMAL)
        self.text.delete('1.0', Tk.END)
        self.text.insert(Tk.END, title + '\n')
        self.text.insert(Tk.END, '-' * len(title) + '\n')
        for label, score in rows:
            self.text.insert(Tk.END, f'{label:<24} {score: .6f}\n')
        self.text.configure(state = Tk.DISABLED)

    def set_text_content(self, title, content):
        self.title(title)
        self.text.configure(state = Tk.NORMAL)
        self.text.delete('1.0', Tk.END)
        self.text.insert(Tk.END, content)
        self.text.configure(state = Tk.DISABLED)


class DatasetInspectorDialog(Tk.Toplevel):
    """Search2 / Search3 dataset summary viewer."""

    def __init__(self, frame):
        Tk.Toplevel.__init__(self, frame)
        self.frame = frame
        self.title('dataset inspector')
        self.geometry('620x520')
        self.font = ('Century Gothic', 12, 'bold')
        self.ai_index_var = Tk.StringVar(value = self._default_ai_text())
        self.dataset_kind_var = Tk.StringVar(value = 'Search2')
        self.sample_key_var = Tk.StringVar(value = '')
        self.sample_selector_var = Tk.StringVar(value = 'perfect_key')
        self._build_widgets()
        self.refresh()

    def _default_ai_text(self):
        text = self.frame.param_index_var.get().strip()
        if text != '':
            return text.split(',')[0].strip()
        return str(self.frame.AI_idx)

    def _build_widgets(self):
        Tk.Label(self, text = 'AI idx', font = self.font).pack(anchor = 'w', padx = 6, pady = (6, 2))
        entry_frame = Tk.Frame(self)
        entry_frame.pack(fill = 'x', padx = 6)
        Tk.Entry(entry_frame, textvariable = self.ai_index_var, font = self.font, width = 8).pack(side = 'left')
        Tk.Button(entry_frame, text = 'refresh', font = self.font, command = self.refresh).pack(side = 'left', padx = 4)
        self.text = ScrolledText(self, width = 84, height = 28, font = ('Menlo', 11))
        self.text.pack(fill = 'both', expand = True, padx = 6, pady = 6)
        self.text.configure(state = Tk.DISABLED)

        sample_frame = Tk.Frame(self)
        sample_frame.pack(fill = 'x', padx = 6, pady = (0, 6))
        Tk.OptionMenu(sample_frame, self.dataset_kind_var, 'Search2', 'Search3').pack(side = 'left')
        Tk.OptionMenu(sample_frame, self.sample_selector_var, 'perfect_key', 'top_group').pack(side = 'left', padx = 4)
        Tk.Entry(sample_frame, textvariable = self.sample_key_var, font = self.font).pack(side = 'left', fill = 'x', expand = True, padx = 4)
        Tk.Button(sample_frame, text = 'open sample', font = self.font, command = self.open_sample).pack(side = 'left')
        Tk.Button(sample_frame, text = 'replay sample', font = self.font, command = self.replay_sample).pack(side = 'left', padx = 4)

    def refresh(self):
        ai_index = self.frame.param_manager.selected_index(self.ai_index_var.get(), default = self.frame.AI_idx)
        content = self.frame.search_data_manager.dataset_summary_text(ai_index)
        self.text.configure(state = Tk.NORMAL)
        self.text.delete('1.0', Tk.END)
        self.text.insert(Tk.END, content)
        self.text.configure(state = Tk.DISABLED)

    def open_sample(self):
        ai_index = self.frame.param_manager.selected_index(self.ai_index_var.get(), default = self.frame.AI_idx)
        selector_value = self.sample_key_var.get().strip()
        selector_kind = self.sample_selector_var.get()
        if selector_value == '':
            return
        content = self.frame.search_data_manager.representative_sample_text(
            ai_index,
            self.dataset_kind_var.get(),
            selector_value,
            selector_kind,
        )
        self.text.configure(state = Tk.NORMAL)
        self.text.delete('1.0', Tk.END)
        if content is None:
            self.text.insert(Tk.END, f'No sample found for {selector_kind}={selector_value} in {self.dataset_kind_var.get()}.\n')
        else:
            self.text.insert(Tk.END, content)
            self.frame.append_log(
                f'dataset sample: ai={ai_index} kind={self.dataset_kind_var.get()} {selector_kind}={selector_value}'
            )
        self.text.configure(state = Tk.DISABLED)

    def replay_sample(self):
        ai_index = self.frame.param_manager.selected_index(self.ai_index_var.get(), default = self.frame.AI_idx)
        selector_value = self.sample_key_var.get().strip()
        selector_kind = self.sample_selector_var.get()
        if selector_value == '':
            return
        sample = self.frame.search_data_manager.representative_sample(
            ai_index,
            self.dataset_kind_var.get(),
            selector_value,
            selector_kind,
        )
        if sample is None:
            self.text.configure(state = Tk.NORMAL)
            self.text.delete('1.0', Tk.END)
            self.text.insert(Tk.END, f'No sample found for {selector_kind}={selector_value} in {self.dataset_kind_var.get()}.\n')
            self.text.configure(state = Tk.DISABLED)
            return
        DatasetSampleReplayDialog(self.frame, ai_index, self.dataset_kind_var.get(), sample, selector_kind, selector_value)


class DatasetSampleReplayDialog(Tk.Toplevel):
    """Replay one dataset sample step by step."""

    def __init__(self, frame, ai_index, dataset_kind, sample, selector_kind = 'perfect_key', selector_value = None):
        Tk.Toplevel.__init__(self, frame)
        self.frame = frame
        self.ai_index = ai_index
        self.dataset_kind = dataset_kind
        self.sample = sample
        self.selector_kind = selector_kind
        self.selector_value = selector_value
        self.step_index = 0
        self.font = ('Century Gothic', 12, 'bold')
        self.title(f'{dataset_kind} replay')
        self.replay_cube = self._build_replay_cube()
        self.viewer = self._build_viewer()
        self.info_var = Tk.StringVar(value = '')
        self._build_widgets()
        self._render_step()

    def _build_replay_cube(self):
        if self.frame.puzzle_type == 'megaminx':
            return MegaminxCube(
                size = self.frame.config.cube_size,
                F2L = self.frame.config.F2L,
                OLL = self.frame.config.OLL,
                Centers = self.frame.config.Centers,
                Edges = self.frame.config.Edges,
                Cross = self.frame.config.Cross,
            )
        if self.frame.puzzle_type == 'master_pyraminx':
            return MasterPyraminxCube(
                size = self.frame.config.cube_size,
                F2L = self.frame.config.F2L,
                OLL = self.frame.config.OLL,
                Centers = self.frame.config.Centers,
                Edges = self.frame.config.Edges,
                Cross = self.frame.config.Cross,
            )
        if self.frame.puzzle_type == 'pyraminx':
            return PyraminxCube(
                size = self.frame.config.cube_size,
                F2L = self.frame.config.F2L,
                OLL = self.frame.config.OLL,
                Centers = self.frame.config.Centers,
                Edges = self.frame.config.Edges,
                Cross = self.frame.config.Cross,
            )
        if self.frame.puzzle_type == 'skewb':
            return SkewbCube(
                size = self.frame.config.cube_size,
                F2L = self.frame.config.F2L,
                OLL = self.frame.config.OLL,
                Centers = self.frame.config.Centers,
                Edges = self.frame.config.Edges,
                Cross = self.frame.config.Cross,
            )
        if self.frame.puzzle_type == 'fto':
            return FtoCube(
                size = self.frame.config.cube_size,
                F2L = self.frame.config.F2L,
                OLL = self.frame.config.OLL,
                Centers = self.frame.config.Centers,
                Edges = self.frame.config.Edges,
                Cross = self.frame.config.Cross,
            )
        if self.frame.puzzle_type == 'cto':
            return CtoCube(
                size = self.frame.config.cube_size,
                F2L = self.frame.config.F2L,
                OLL = self.frame.config.OLL,
                Centers = self.frame.config.Centers,
                Edges = self.frame.config.Edges,
                Cross = self.frame.config.Cross,
            )
        return Rubiks_3(
            size = self.frame.config.cube_size,
            F2L = self.frame.config.F2L,
            OLL = self.frame.config.OLL,
            Centers = self.frame.config.Centers,
            Edges = self.frame.config.Edges,
            Cross = self.frame.config.Cross,
        )

    def _build_viewer(self):
        if self.frame.puzzle_type == 'megaminx':
            return MegaminxStateViewer(self, mini_mode = True)
        if self.frame.puzzle_type in ('pyraminx', 'master_pyraminx'):
            return PyraminxStateViewer(self, self.frame.cube_size, mini_mode = True)
        if self.frame.puzzle_type == 'skewb':
            return SkewbStateViewer(self, mini_mode = True)
        if self.frame.puzzle_type == 'fto':
            return FtoStateViewer(self, mini_mode = True)
        if self.frame.puzzle_type == 'cto':
            return CtoStateViewer(self, mini_mode = True)
        return StateViewer(self, self.frame.cube_size, mini_mode = True)

    def _build_widgets(self):
        top = Tk.Frame(self)
        top.pack(fill = 'x', padx = 6, pady = 6)
        Tk.Button(top, text = '<<', font = self.font, command = self._rewind).pack(side = 'left')
        Tk.Button(top, text = '<', font = self.font, command = self._prev_step).pack(side = 'left', padx = 4)
        Tk.Button(top, text = '>', font = self.font, command = self._next_step).pack(side = 'left')
        Tk.Button(top, text = '>>', font = self.font, command = self._last_step).pack(side = 'left', padx = 4)
        Tk.Label(top, textvariable = self.info_var, font = self.font, justify = Tk.LEFT).pack(side = 'left', padx = 12)

        self.viewer.pack(padx = 6, pady = 6)
        self.text = ScrolledText(self, width = 72, height = 12, font = ('Menlo', 11))
        self.text.pack(fill = 'both', expand = True, padx = 6, pady = 6)
        self.text.configure(state = Tk.DISABLED)

    def _rewind(self):
        self.step_index = 0
        self._render_step()

    def _prev_step(self):
        if self.step_index > 0:
            self.step_index -= 1
            self._render_step()

    def _next_step(self):
        if self.step_index < len(self.sample.moves):
            self.step_index += 1
            self._render_step()

    def _last_step(self):
        self.step_index = len(self.sample.moves)
        self._render_step()

    def _render_step(self):
        self.replay_cube.reset()
        self.replay_cube.scramble(0, self.sample.scramble)
        applied_moves = tuple(self.sample.moves[:self.step_index])
        for move in applied_moves:
            self.replay_cube.make_move(move)
        self.viewer.set_color(self.replay_cube.state)
        self._update_info(applied_moves)
        self._update_text(applied_moves)

    def _update_info(self, applied_moves):
        total_steps = len(self.sample.moves)
        next_move = ''
        if self.step_index < total_steps:
            next_move = self.frame.display_move_sequence((self.sample.moves[self.step_index],))[0]
        self.info_var.set(
            f'step {self.step_index}/{total_steps}  next={next_move}  key={getattr(self.sample, "perfect_key", None)}'
        )

    def _update_text(self, applied_moves):
        ai = self.frame.AIs[self.ai_index]
        x = self.replay_cube.makedata().reshape(-1, 1)
        policy = ai.predict(x, policy = True, value = False).reshape(-1)
        value = float(ai.predict(x, policy = False, value = True)[0][0])
        top_indices = np.argsort(policy)[-5:][::-1]
        top_moves = [
            f"{self.frame.display_move_sequence((self.frame.move_keys[index],))[0]}: {float(policy[index]):.4f}"
            for index in top_indices
        ]
        reward_line = self._step_array_line('reward', getattr(self.sample, 'rewards', None), self.step_index - 1)
        target_line = self._step_array_line('value_target', getattr(self.sample, 'value_targets', None), self.step_index - 1)
        trace_line = self._step_array_line('value_trace', getattr(self.sample, 'value_trace', None), self.step_index)
        trace_raw_line = self._step_array_line('value_trace_raw', getattr(self.sample, 'value_trace_raw', None), self.step_index)
        lines = [
            f'{self.dataset_kind} replay',
            f'selector: {self.selector_kind}={self.selector_value}',
            f'AI: {self.ai_index}',
            f'perfect_key: {getattr(self.sample, "perfect_key", None)}',
            f'top_group: {getattr(self.sample, "top_group", None)}',
            f'step: {self.step_index}/{len(self.sample.moves)}',
            f'value: {value:.6f}',
            reward_line,
            target_line,
            trace_line,
            trace_raw_line,
            f'applied moves: {self.frame.display_move_sequence(applied_moves)}',
            f'remaining moves: {self.frame.display_move_sequence(self.sample.moves[self.step_index:])}',
            'top policy:',
        ] + [f'  {line}' for line in top_moves]
        self.text.configure(state = Tk.NORMAL)
        self.text.delete('1.0', Tk.END)
        self.text.insert(Tk.END, '\n'.join(lines))
        self.text.configure(state = Tk.DISABLED)

    def _step_array_line(self, label, values, index):
        if values is None:
            return f'{label}: n/a'
        if len(values) == 0:
            return f'{label}: []'
        if index < 0 or index >= len(values):
            return f'{label}: out-of-range ({index})'
        value = values[index]
        if isinstance(value, (float, np.floating)):
            return f'{label}: step[{index}]={float(value):.6f}'
        return f'{label}: step[{index}]={value}'
