"""Small dialog button widgets."""

import tkinter as Tk

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


