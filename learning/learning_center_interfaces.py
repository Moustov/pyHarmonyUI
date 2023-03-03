import threading
import time
from copy import deepcopy
from functools import partial
from tkinter import Frame, messagebox, Button, Canvas
from tkinter.constants import *
from pyharmonytools.harmony.note import Note


class LearningCenterInterface:
    def __init__(self):
        self.canvas_step_notes = None
        self.status_button = None
        self.module_path_canvas = None
        self.module_path_canvas_height = 100
        self.module_path_canvas_width = 500
        self.pause_button = None
        self.scenario = None
        self.stop_button = None
        self.start_button = None
        self.debug = True
        self.ui_root_tk = None
        self.pause_between_notes = 1
        self.notes_sequence = None
        self.current_expected_note_step = 0
        self.selected_instrument_training = None

    def display(self, ui_root_tk: Frame):
        self.ui_root_tk = ui_root_tk

        self.start_button = Button(ui_root_tk, text='Start exercise', command=self.do_start_exercise, state=DISABLED)
        self.start_button.grid(row=0, column=0)

        self.pause_button = Button(self.ui_root_tk, text='Pause exercise', command=self.do_stop_exercise)
        self.pause_button.grid(row=0, column=1)
        self.pause_button.grid_remove()

        self.stop_button = Button(self.ui_root_tk, text='Stop exercise', command=self.do_stop_exercise)
        self.stop_button.grid(row=0, column=0)
        self.stop_button.grid_remove()

        self.status_button = Button(self.ui_root_tk, text='--', state=DISABLED)
        self.status_button.grid(row=0, column=2)

        self.module_path_canvas = Canvas(ui_root_tk, width=self.module_path_canvas_width,
                                         height=self.module_path_canvas_height,
                                         borderwidth=1, background='white')
        self.module_path_canvas.grid(row=1, column=0, columnspan=4)

    def set_instrument(self, instrument):
        self.selected_instrument_training = instrument
        if self.selected_instrument_training and self.scenario:
            self.start_button.config(state=NORMAL)

    def set_training_module(self, module_content: dict):
        """
        registers the training module content + displays the module checkpoints
        :param module_content: ex {"name": "C chord", "description": "", "play_notes": "C3-E3-G3", "check condition": 100}
        :return:
        """
        self.scenario = deepcopy(module_content)
        if self.selected_instrument_training and self.scenario:
            self.start_button.config(state=NORMAL)
        self.notes_sequence = self.scenario["play_notes"].split("-")
        self.module_path_canvas.delete("all")
        note_width = 20
        margin_W = 20
        margin_E = 20
        margin_N = 10
        note_interval = (self.module_path_canvas_width - margin_W - margin_E) / (len(self.notes_sequence) + 1)
        font = ('Helvetica', 10)
        step_index = 1
        self.canvas_step_notes = []
        self.module_path_canvas.create_line(0, self.module_path_canvas_height / 2 + note_width / 2,
                                       self.module_path_canvas_width,
                                       self.module_path_canvas_height / 2 + note_width / 2,
                                       fill="lightgray", width=5)
        for step in self.notes_sequence:
            nw_x = margin_W + step_index * note_interval + 3
            nw_y = self.module_path_canvas_height / 2
            se_x = nw_x + note_width
            se_y = nw_y + note_width
            step_index += 1
            oval_id = self.module_path_canvas.create_oval(nw_x, nw_y, se_x, se_y, fill="#DDDDDD",
                                                          outline="#AAAAAA", width=1, tags=step)
            text_id = self.module_path_canvas.create_text(nw_x + note_width / 2, nw_y + note_width / 2, text=step,
                                                          font=font, anchor=CENTER, fill="#222222", tags=step)
            self.canvas_step_notes.append((oval_id, text_id))

    def check_note(self, note: str, heard_freq: float = 0.0, closest_pitch: float = 0.0):
        if self.debug:
            print("expected:", self.notes_sequence[self.current_expected_note_step], "heard:", note)
        try:
            heard_raw_heard_note = note[:-1]
            heard_octave = int(note[-1])
            expected_raw_note = self.notes_sequence[self.current_expected_note_step][:-1]
            expected_octave = int(self.notes_sequence[self.current_expected_note_step][-1])
            if Note(heard_raw_heard_note) == Note(expected_raw_note) and heard_octave == expected_octave:
                self.validate_current_step()
                self.current_expected_note_step += 1
            if self.debug:
                print("status:", int(100 * self.current_expected_note_step / len(self.notes_sequence)), "%")
            if self.current_expected_note_step == len(self.notes_sequence):
                self.selected_instrument_training.do_stop_hearing()
                messagebox.showinfo("Harmony tools",
                                    f"You did it!")
        except ValueError:
            if self.debug:
                print("Not a note")

    def do_start_exercise(self):
        if self.selected_instrument_training and self.scenario:
            # self.learning_scenario = LearningScenario()
            # self.learning_scenario.start_learning(self.selected_instrument_training, self.scenario)

            self.selected_instrument_training.debug = True
            self.current_expected_note_step = 0
            for note in self.notes_sequence:
                raw_note_name = note[:-1]
                raw_note_name = Note.CHROMATIC_SCALE_SHARP_BASED[Note.CHROMATIC_SCALE_FLAT_BASED.index(raw_note_name)]
                octave = int(note[-1])
                note = f"{raw_note_name}{octave}"
                self.selected_instrument_training.show_note(note)
                self.selected_instrument_training.do_play_note(raw_note_name, octave)
                time.sleep(self.pause_between_notes)
                self.selected_instrument_training.mask_note(note)
            self.selected_instrument_training.do_start_hearing(self)

    def do_stop_exercise(self):
        pass

    def validate_current_step(self):
        """
        the note will temporarily blink to acknowledge what has been heard
        :param note:
        :return:
        """
        validate_thread = threading.Thread(target=partial(self.make_note_blink,
                                                          self.current_expected_note_step,
                                                          "#26ea6e"),
                                           name="validate")
        validate_thread.start()

    def make_note_blink(self, note_index: int, new_color: str):
        if self.debug:
            print("make_note_blink", note_index, new_color)
        the_note = self.canvas_step_notes[note_index]
        for i in range(0, 5):
            self.module_path_canvas.itemconfigure(the_note[0], state='normal', fill=new_color)
            self.module_path_canvas.itemconfigure(the_note[1], state='normal')
            time.sleep(0.1)
            self.module_path_canvas.itemconfigure(the_note[0], state='hidden')
            self.module_path_canvas.itemconfigure(the_note[1], state='hidden')
            time.sleep(0.1)
        self.module_path_canvas.itemconfigure(the_note[0], state='normal', fill=new_color)
        self.module_path_canvas.itemconfigure(the_note[1], state='normal')
