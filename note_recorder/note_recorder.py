import tkinter
from tkinter import Frame, LabelFrame, messagebox, Tk, Button
from tkinter.constants import *
from tkinter.ttk import Combobox

from moustovtkwidgets_lib.mtk_edit_table import mtkEditTable, mtkEditTableListener

from instrument.guitar_training import GuitarTraining
from instrument.voice_training import VoiceTraining
from learning.instrument_listener import InstrumentListener


class NoteRecorder(InstrumentListener, mtkEditTableListener):
    def __init__(self):
        self.instrument_frame = None
        self.notes_treeview = None
        self.notes_labelframe = None
        self.selected_instrument = None
        self.frame = None
        self.stop_button = None
        self.record_button = None
        self.recorder_labelframe = None
        self.instrument_combobox = None
        self.instruments = None
        self.instrument_labelframe = None
        self.frame = None
        self.ui_root_tk = None

    def get_ui_frame(self, root: tkinter.Tk) -> Frame:
        self.frame = Frame(root)
        self.ui_root_tk = root
        # todo refactor this part to make it DRY
        self.instrument_labelframe = LabelFrame(self.frame, text='Select your instrument')
        self.instrument_labelframe.grid(row=0, column=0)
        self.instruments = ["Voice", "Guitar", "Piano", "Flute", "Saxophone"]
        self.instrument_combobox = Combobox(self.instrument_labelframe, values=self.instruments)
        self.instrument_combobox.bind('<<ComboboxSelected>>', self._do_select_instrument)
        self.instrument_combobox.current(0)
        self.instrument_combobox.grid(row=0, column=1)

        # instrument feedback
        self.selected_instrument = VoiceTraining(self)
        self.instrument_frame = self.selected_instrument.get_ui_frame(self.frame)
        self.instrument_frame.grid(row=1, column=0, columnspan=5, sticky='nsew', padx=5, pady=5)

        self.recorder_labelframe = LabelFrame(self.frame, text='Recorder')
        self.recorder_labelframe.grid(row=0, column=1)
        self.record_button = Button(self.recorder_labelframe, text='Start', command=self.do_start_recording)
        self.record_button.grid(row=1, column=0)
        self.stop_button = Button(self.recorder_labelframe, text='Stop', command=self.do_stop_recording)
        self.stop_button.grid(row=1, column=1)
        # todo [BPM (30-250) / shield signature / number of bars] vs [chrono]

        # todo display score
        self.notes_labelframe = LabelFrame(self.frame, text='Played Notes')
        self.notes_labelframe.grid(row=2, column=1)
        col_ids = ('chrono', 'Note', 'Duration')
        col_titles = ('chrono', 'Note', 'Duration')
        self.notes_treeview = mtkEditTable(self.notes_labelframe, columns=col_ids, column_titles=col_titles)
        self.notes_treeview.add_listener(self)
        self.notes_treeview.debug = True
        self.notes_treeview.column('chrono', anchor=CENTER, width=60, stretch=NO)
        self.notes_treeview.column('Note', anchor=W, width=200, minwidth=100)
        self.notes_treeview.column('Duration', anchor=CENTER, width=0, stretch=YES)
        self.notes_treeview.grid(row=0, column=0, columnspan=2, ipadx=200, padx=5, pady=5)
        self.notes_treeview.column("#0", width=70, stretch=NO)

        return self.frame

    def do_start_recording(self):
        self.selected_instrument.do_start_hearing(None)

    def do_stop_recording(self):
        self.selected_instrument.do_stop_hearing()

    def _do_select_instrument(self, event):
        """
        todo refactor code to avoid duplication in [learning_center.py](learning_center.py)
        :param event:
        :return:
        """
        # "Voice", "Guitar", "Piano", "Flute", "Saxophone"
        # select instrument
        instr = self.instrument_combobox.get()
        self.selected_instrument = None
        if instr == "Voice":
            self.selected_instrument = VoiceTraining(self)
        elif instr == "Guitar":
            self.selected_instrument = GuitarTraining(self)
        else:
            messagebox.showinfo("PyHarmony", "This instrument is not yet implemented - try 'Voice' instead")
        if instr == "Voice":
            self.selected_instrument = VoiceTraining(self)
            for widget in self.instrument_frame.winfo_children():
                widget.destroy()
            self.instrument_frame = self.selected_instrument.get_ui_frame(self.frame)
            self.instrument_frame.grid(row=1, column=0, columnspan=5, sticky='nsew', padx=5, pady=5)
        elif instr == "Guitar":
            self.selected_instrument = GuitarTraining(self)
            for widget in self.instrument_frame.winfo_children():
                widget.destroy()
            self.instrument_frame = self.selected_instrument.get_ui_frame(self.frame)
            self.instrument_frame.grid(row=1, column=0, columnspan=5, sticky='nsew', padx=5, pady=5)
        else:
            messagebox.showinfo("PyHarmony", "This instrument is not yet implemented - try 'Voice' instead")
        Tk.update(self.ui_root_tk)