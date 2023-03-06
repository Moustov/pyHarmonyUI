import json
import os
import random
import tkinter
from copy import deepcopy
from tkinter import Button, Label, Frame, messagebox, Scale, Tk, LabelFrame
from tkinter.constants import *
from tkinter.ttk import Treeview, Combobox

from pyharmonytools.harmony.note import Note

from instrument.guitar_training import GuitarTraining
from instrument.voice_training import VoiceTraining
from learning.learning_center_interfaces import LearningCenterInterface


class LearningCenter:
    MODULES_PATH = 'learning modules/'

    def __init__(self):
        self.transposing_labelframe = None
        self.learn_with_random_transpose = None
        self.transposed_training_module = None
        self.previous_transposition_value = 0
        self.transpose_scale = None
        self.reload_button = None
        self.selected_instrument_training = None
        self.learning_center_interface = None
        self.learning_status_frame = None
        self.learning_scenario_frame = None
        self.instruments = None
        self.instrument_combobox = None
        self.select_instrument_label = None
        self.list_of_modules = None
        self.select_module_label = None
        self.debug = True
        self.learning_scenario = None
        self.ui_root_tk = None
        self.selected_training_module = None

    def display(self, ui_root_tk: tkinter.Tk):
        self.ui_root_tk = ui_root_tk

        self.select_module_label = Label(self.ui_root_tk, text="Select your training module")
        self.select_module_label.grid(row=0, column=0)

        self.reload_button = Button(ui_root_tk, text='Reload', command=self.do_reload_exercises)
        self.reload_button.grid(row=1, column=0)

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
        self.list_of_modules.grid(row=2, column=0)
        self.fill_list_of_modules()

        self.select_instrument_label = Label(self.ui_root_tk, text="Select your instrument")
        self.select_instrument_label.grid(row=3, column=0)

        self.instruments = ["Voice", "Guitar", "Piano", "Flute", "Saxophone"]
        self.instrument_combobox = Combobox(self.ui_root_tk, values=self.instruments)
        self.instrument_combobox.bind('<<ComboboxSelected>>', self._do_select_instrument)
        self.instrument_combobox.current(0)
        self.instrument_combobox.grid(row=4, column=0)
        # learning params
        self.transposing_labelframe = LabelFrame(self.ui_root_tk, text='Transposing')
        self.transposing_labelframe.grid(row=5, column=0)
        self.transpose_scale = Scale(self.transposing_labelframe, from_=-11, to=11, tickinterval=3, length=200,
                                     orient=HORIZONTAL,
                                     command=self._do_transpose_change)
        self.transpose_scale.set(0)
        self.transpose_scale.grid(row=0, column=0)

        self.learn_with_random_transpose = Button(self.transposing_labelframe, text='Random transpose',
                                                  command=self._do_exercize_random_transpose, anchor=W)
        self.learn_with_random_transpose.grid(row=0, column=1)
        # learning feedback
        self.learning_status_frame = Frame(self.ui_root_tk)
        self.learning_status_frame.grid(row=6, column=1, columnspan=2)
        self.learning_center_interface = LearningCenterInterface()
        self.learning_center_interface.display(self.learning_status_frame)
        # instrument feedback
        self.learning_scenario_frame = Frame(self.ui_root_tk)
        self.learning_scenario_frame.grid(row=0, column=1, rowspan=5)
        self.selected_instrument_training = VoiceTraining()
        # self.selected_instrument_training.debug = True
        self.selected_instrument_training.display(self.learning_scenario_frame)
        self.learning_center_interface.set_instrument(self.selected_instrument_training)

    def _do_exercize_random_transpose(self):
        note_min = self.selected_instrument_training.get_lowest_note()
        note_max = self.selected_instrument_training.get_highest_note()
        first_note = Note(self.selected_training_module["play_notes"].split("-")[0])
        interval_min = first_note.get_interval_in_half_tones(note_min) + 1
        interval_max = first_note.get_interval_in_half_tones(note_max) - 1
        random_transpose = random.randrange(interval_min, interval_max)
        self.transpose_scale.set(random_transpose)
        self._do_transpose_change(None)
        self.selected_instrument_training.clear_notes()
        self.current_expected_note_step = 0
        self.learning_center_interface.demonstrate_step(0)

    def _do_transpose_change(self, event):
        transposed_value = self.transpose_scale.get()
        print(transposed_value)
        notes = self.selected_training_module["play_notes"].split("-")
        self.transposed_training_module = deepcopy(self.selected_training_module)
        new_notes = []
        Note.debug = True
        no_error = True
        for n in notes:
            try:
                new_notes.append(Note(n).transpose(transposed_value))
            except ValueError as ve:
                self.transpose_scale.set(self.previous_transposition_value)
                Tk.update(self.ui_root_tk)
                no_error = False
                messagebox.showinfo("Transpose", str(ve))
                break
        if no_error:
            self.transpose_scale.set(transposed_value)
            self.previous_transposition_value = transposed_value
            self.transposed_training_module["play_notes"] = "-".join(new_notes)
            self.learning_center_interface.set_training_module(self.transposed_training_module)

    def do_reload_exercises(self):
        self.fill_list_of_modules()

    def _do_module_select(self, event):
        item = self.list_of_modules.item(self.list_of_modules.selection())['values']
        if item:
            self.transpose_scale.set(0)
            f = open(f"{LearningCenter.MODULES_PATH}{item[0]}.json")
            module_content = json.load(f)
            f.close()
            self.selected_training_module = module_content
            self.learning_center_interface.set_training_module(module_content)
        else:
            self.do_reload_exercises()

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
            self.learning_center_interface.set_instrument(self.selected_instrument_training)
            for widgets in self.learning_scenario_frame.winfo_children():
                widgets.destroy()
            self.selected_instrument_training.display(self.learning_scenario_frame)
            note_min = self.selected_instrument_training.get_lowest_note()
            note_max = self.selected_instrument_training.get_highest_note()
            first_note = Note(self.selected_training_module["play_notes"].split("-")[0])
            interval_min = first_note.get_interval_in_half_tones(note_min)
            interval_max = first_note.get_interval_in_half_tones(note_max)
            self.transpose_scale.configure(from_=interval_min, to=interval_max,
                                           tickinterval=(interval_max - interval_min) / 10)

    def fill_list_of_modules(self):
        for item in self.list_of_modules.get_children():
            self.list_of_modules.delete(item)
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
