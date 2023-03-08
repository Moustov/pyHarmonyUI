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
from learning.instrument_listener import InstrumentListener
from learning.learning_center_interfaces import LearningCenterInterface


class LearningCenter(InstrumentListener):
    MODULES_PATH = 'learning modules/'

    def __init__(self):
        super().__init__()
        self.training_module_id = 0
        self.instrument_labelframe = None
        self.training_module_labelframe = None
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

        self.training_module_labelframe = LabelFrame(self.ui_root_tk, text='Training modules')
        self.training_module_labelframe.grid(row=0, column=0)
        self.select_module_label = Label(self.training_module_labelframe, text="Select your training module")
        self.select_module_label.grid(row=0, column=0)
        self.reload_button = Button(self.training_module_labelframe, text='Reload', command=self.do_reload_exercises)
        self.reload_button.grid(row=1, column=0)
        self.list_of_modules = Treeview(self.training_module_labelframe)
        self.list_of_modules['columns'] = ('Name', 'Description', 'Content', 'Path')
        self.list_of_modules.column("#0", width=0, stretch=NO)
        self.list_of_modules.column('Name', anchor=CENTER, width=80)
        self.list_of_modules.column('Description', anchor=CENTER, width=80)
        self.list_of_modules.column('Content', anchor=CENTER, width=80)
        self.list_of_modules.column('Path', anchor=CENTER, width=0)
        self.list_of_modules.heading("#0", text="", anchor=CENTER)
        self.list_of_modules.heading('Name', text="Name", anchor=CENTER)
        self.list_of_modules.heading('Description', text="Description", anchor=CENTER)
        self.list_of_modules.heading('Content', text="Content", anchor=CENTER)
        self.list_of_modules.heading('Path', text="Path", anchor=CENTER)
        # http://tkinter.fdex.eu/doc/event.html#events
        self.list_of_modules.bind("<ButtonRelease-1>", self._do_module_select)
        self.list_of_modules.grid(row=2, column=0)
        self.fill_list_of_modules()

        self.instrument_labelframe = LabelFrame(self.ui_root_tk, text='Select your instrument')
        self.instrument_labelframe.grid(row=1, column=0)
        self.instruments = ["Voice", "Guitar", "Piano", "Flute", "Saxophone"]
        self.instrument_combobox = Combobox(self.instrument_labelframe, values=self.instruments)
        self.instrument_combobox.bind('<<ComboboxSelected>>', self._do_select_instrument)
        self.instrument_combobox.current(0)
        self.instrument_combobox.grid(row=0, column=0)
        # learning params
        self.transposing_labelframe = LabelFrame(self.ui_root_tk, text='Transposing')
        self.transposing_labelframe.grid(row=3, column=0)
        self.transpose_scale = Scale(self.transposing_labelframe, from_=-11, to=11, tickinterval=3, length=200,
                                     orient=HORIZONTAL, command=self._do_transpose_change)
        self.transpose_scale.set(0)
        self.transpose_scale.grid(row=0, column=0)

        self.learn_with_random_transpose = Button(self.transposing_labelframe, text='Random transpose',
                                                  command=self._do_exercize_random_transpose, anchor=W,
                                                  state="disabled")
        self.learn_with_random_transpose.grid(row=0, column=1)
        # learning feedback
        self.learning_status_frame = Frame(self.ui_root_tk)
        self.learning_status_frame.grid(row=6, column=1, columnspan=2)
        self.learning_center_interface = LearningCenterInterface()
        self.learning_center_interface.display(self.learning_status_frame)
        # instrument feedback
        self.learning_scenario_frame = Frame(self.ui_root_tk)
        self.learning_scenario_frame.grid(row=0, column=1, rowspan=5)
        self.selected_instrument_training = VoiceTraining(self)
        # self.selected_instrument_training.debug = True
        self.selected_instrument_training.display(self.learning_scenario_frame)
        self.learning_center_interface.set_instrument(self.selected_instrument_training)

    def _do_exercize_random_transpose(self):
        note_min = self.selected_instrument_training.get_lowest_note()
        note_max = self.selected_instrument_training.get_highest_note()
        first_note = Note(self.selected_training_module["play_notes"].split("-")[0])
        interval_min = first_note.get_interval_in_half_tones(note_min) + 1
        interval_max = first_note.get_interval_in_half_tones(note_max) - 1
        random.seed()
        random_transpose = random.randrange(interval_min, interval_max)
        self.transpose_scale.set(random_transpose)
        self._do_transpose_change(None)
        self.selected_instrument_training.clear_notes(with_calibration=True)
        self.current_expected_note_step = 0
        self.learning_center_interface.demonstrate_step(0)

    def instrument_updated(self, lowest_note: Note, highest_note: Note):
        """
        todo : check if [lowest note, highest note] within [note_min,  note_max] instead of first_note
        :return:
        """
        module_lowest_note = Note("B9")
        module_highest_note = Note("C0")
        if self.selected_training_module and "play_notes" in self.selected_training_module.keys():
            for n in self.selected_training_module["play_notes"].split("-"):
                the_note = Note(n)
                if module_lowest_note > the_note:
                    module_lowest_note = the_note
                if module_highest_note < the_note:
                    module_highest_note = the_note

        interval_min = module_lowest_note.get_interval_in_half_tones(lowest_note)
        interval_max = module_highest_note.get_interval_in_half_tones(highest_note)
        if interval_min > 0 > interval_max:
            raise ValueError("Module out of vocal range")
        elif 0 < interval_min:
            self.transpose_scale.configure(from_=interval_min, to=interval_max,
                                           tickinterval=(interval_max - interval_min) / 11)
        elif 0 > interval_max:
            self.transpose_scale.configure(from_=interval_min, to=interval_max,
                                           tickinterval=(interval_max - interval_min) / 11)
        else:
            self.transpose_scale.configure(from_=interval_min, to=interval_max,
                                           tickinterval=(interval_max - interval_min) / 11)
        self.transpose_scale.set(0)
        self.learn_with_random_transpose.config(state="normal")

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
                # messagebox.showinfo("Transpose", str(ve))
                print("Transposing Error", str(ve))
                # break
        if no_error:
            self.transpose_scale.set(transposed_value)
            self.previous_transposition_value = transposed_value
            self.transposed_training_module["play_notes"] = "-".join(new_notes)
            self.learning_center_interface.set_training_module(self.transposed_training_module)

    def do_reload_exercises(self):
        self.fill_list_of_modules()

    def _do_module_select(self, event):
        item = self.list_of_modules.item(self.list_of_modules.selection())['values']
        if item and item[1]:
            self.transpose_scale.set(0)
            f = open(f"{item[3]}/{item[0]}.json")
            module_content = json.load(f)
            f.close()
            self.selected_training_module = module_content
            self.learning_center_interface.set_training_module(module_content)
            if self.selected_instrument_training and self.selected_training_module:
                self.learn_with_random_transpose.config(state="normal")
                self.instrument_updated(self.selected_instrument_training.get_lowest_note(),
                                        self.selected_instrument_training.get_highest_note())

    def _do_select_instrument(self, event):
        # "Voice", "Guitar", "Piano", "Flute", "Saxophone"
        # select instrument
        instr = self.instrument_combobox.get()
        self.selected_instrument_training = None
        if instr == "Voice":
            self.selected_instrument_training = VoiceTraining(self)
        elif instr == "Guitar":
            self.selected_instrument_training = GuitarTraining(self)
        else:
            messagebox.showinfo("PyHarmony", "This instrument is not yet implemented - try 'Voice' instead")
        if self.selected_instrument_training:
            self.learning_center_interface.set_instrument(self.selected_instrument_training)
            for widgets in self.learning_scenario_frame.winfo_children():
                widgets.destroy()
        if instr == "Voice":
            self.selected_instrument_training = VoiceTraining(self)
            self.selected_instrument_training.display(self.learning_scenario_frame)
            self.selected_instrument_training.set_lowest_note(Note("C3"))
            self.selected_instrument_training.set_highest_note(Note("B5"))
        elif instr == "Guitar":
            self.selected_instrument_training = GuitarTraining(self)
            self.selected_instrument_training.display(self.learning_scenario_frame)
        else:
            messagebox.showinfo("PyHarmony", "This instrument is not yet implemented - try 'Voice' instead")
        if self.selected_instrument_training:
            self.learning_center_interface.set_instrument(self.selected_instrument_training)
        if self.selected_instrument_training and self.selected_training_module:
            try:
                self.instrument_updated(self.selected_instrument_training.get_lowest_note(),
                                        self.selected_instrument_training.get_highest_note())
            except ValueError as ve:
                messagebox.showwarning(title="Transposition", message=str(ve))
        Tk.update(self.ui_root_tk)

    def fill_list_of_modules(self):
        for item in self.list_of_modules.get_children():
            self.list_of_modules.delete(item)
        self.training_module_id = 0
        self.fill_list_of_modules_folder("", LearningCenter.MODULES_PATH)
        self.list_of_modules.tag_configure("folder", background='orange')

    def fill_list_of_modules_folder(self, parent, path: str):
        modules = os.listdir(path)
        for module in modules:
            abspath = path + "/" + module
            if module.endswith("json"):
                try:
                    f = open(abspath)
                    module_content = json.load(f)
                    f.close()
                    oid = self.list_of_modules.insert(parent=parent, index='end', iid=self.training_module_id, text="",
                                                      values=(module_content["name"], module_content["description"],
                                                              module_content["play_notes"], path),
                                                      tags="module")
                    self.training_module_id += 1
                except Exception as err:
                    oid = self.list_of_modules.insert(parent=parent, index='end', iid=self.training_module_id, text="",
                                                      values=(module, "** error **", str(err)), tags="module")
                    self.training_module_id += 1
            else:
                oid = self.list_of_modules.insert(parent=parent, index='end', iid=self.training_module_id, text="",
                                                  values=(module, "", "", abspath),
                                                  tags="folder")
                self.training_module_id += 1
                self.fill_list_of_modules_folder(oid, abspath)
