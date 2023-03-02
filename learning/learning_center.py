import json
import os
import tkinter
from tkinter import Button, Label, Frame, messagebox
from tkinter.constants import *
from tkinter.ttk import Treeview, Combobox

from instrument.guitar_training import GuitarTraining
from learning.learning_scenario import LearningScenario
from instrument.voice_training import VoiceTraining


class LearningCenter:
    MODULES_PATH = 'learning modules/'

    def __init__(self):
        self.learning_scenario_frame = None
        self.instruments = None
        self.instrument_combobox = None
        self.select_instrument_label = None
        self.list_of_modules = None
        self.select_module_label = None
        self.debug = True
        self.learning_scenario = None
        self.stop_button = None
        self.start_button = None
        self.ui_root_tk = None
        self.scenario = None
        self.selected_instrument_training = None

    def display(self, ui_root_tk: tkinter.Tk):
        self.ui_root_tk = ui_root_tk

        self.select_module_label = Label(self.ui_root_tk, text="Select your training module")
        self.select_module_label.grid(row=0, column=0)

        self.list_of_modules = Treeview(self.ui_root_tk)
        self.list_of_modules['columns'] = ('Name', 'Description', 'Content')
        self.list_of_modules.column("#0", width=0, stretch=NO)
        self.list_of_modules.column('Name', anchor=CENTER, width=80)
        self.list_of_modules.column('Description', anchor=CENTER, width=80)
        self.list_of_modules.column('Content', anchor=CENTER, width=80)
        self.list_of_modules.heading("#0", text="", anchor=CENTER)
        self.list_of_modules.heading('Name', text="Name", anchor=CENTER)
        self.list_of_modules.heading('Description', text="Description", anchor=CENTER)
        self.list_of_modules.heading('Content', text="Content", anchor=CENTER)
        # http://tkinter.fdex.eu/doc/event.html#events
        self.list_of_modules.bind("<ButtonRelease-1>", self._do_module_select)
        self.list_of_modules.grid(row=1, column=0)
        self.fill_list_of_modules()

        self.select_instrument_label = Label(self.ui_root_tk, text="Select your instrument")
        self.select_instrument_label.grid(row=2, column=0)

        self.instruments = ["Voice", "Guitar", "Piano", "Flute", "Saxophone"]
        self.instrument_combobox = Combobox(self.ui_root_tk, values=self.instruments)
        self.instrument_combobox.bind('<<ComboboxSelected>>', self._do_select_instrument)
        self.instrument_combobox.current(0)
        self.instrument_combobox.grid(row=3, column=0)

        self.start_button = Button(ui_root_tk, text='Start exercise', command=self.do_start_exercise)
        self.start_button.grid(row=4, column=0)
        self.stop_button = Button(self.ui_root_tk, text='Stop exercise', command=self.do_stop_exercise)
        self.stop_button.grid(row=4, column=0)
        self.stop_button.grid_remove()

        self.learning_scenario_frame = Frame(self.ui_root_tk)
        self.learning_scenario_frame.grid(row=0, column=1, rowspan=5)
        self.selected_instrument_training = VoiceTraining()
        self.selected_instrument_training.display(self.learning_scenario_frame)
        # select rapidity & success factors (how hard)

    def do_start_exercise(self):
        if self.selected_instrument_training and self.scenario:
            self.learning_scenario = LearningScenario()
            self.learning_scenario.start_learning(self.selected_instrument_training, self.scenario)

    def do_stop_exercise(self):
        pass

    def _do_module_select(self, event):
        item = self.list_of_modules.item(self.list_of_modules.selection())['values']
        print("Selected item : ", item)
        f = open(f"{LearningCenter.MODULES_PATH}{item[0]}.json")
        module_content = json.load(f)
        f.close()
        self.scenario = module_content

    def _do_select_instrument(self, event):
        # "Voice", "Guitar", "Piano", "Flute", "Saxophone"
        # select instrument
        instr = self.instrument_combobox.get()
        self.selected_instrument_training = None
        if instr == "Voice":
            self.selected_instrument_training = VoiceTraining()
        elif instr == "Guitar":
            self.selected_instrument_training = GuitarTraining()
        else:
            messagebox.showinfo("PyHarmony", "This instrument is not yet implemented - try 'Voice' instead")
        if self.selected_instrument_training:
            for widgets in self.learning_scenario_frame.winfo_children():
                widgets.destroy()
            self.selected_instrument_training.display(self.learning_scenario_frame)

    def fill_list_of_modules(self):
        modules = os.listdir(LearningCenter.MODULES_PATH)
        index = 0
        for module in modules:
            try:
                f = open(LearningCenter.MODULES_PATH + module)
                module_content = json.load(f)
                f.close()
                self.list_of_modules.insert(parent="", index='end', iid=index, text="",
                                            values=(module_content["name"], module_content["description"],
                                                    module_content["play_notes"]))
            except Exception as err:
                self.list_of_modules.insert(parent="", index='end', iid=index, text="",
                                            values=("** Error **", module,
                                                    str(err)))
            index += 1
