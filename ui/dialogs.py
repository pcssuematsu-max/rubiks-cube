"""Small dialog button widgets."""

import tkinter as Tk
from tkinter.scrolledtext import ScrolledText

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
