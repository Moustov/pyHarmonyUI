import time
from copy import deepcopy
from tkinter import Frame, Button, Canvas, Tk, LabelFrame
from tkinter.constants import *

import PIL.ImageTk
from PIL import Image
from pyharmonytools.harmony.note import Note


class LearningCenterInterface:
    img = Image.open("resources/checked_icon.png")

    def __init__(self):
        self.exercise_labelframe = None
        self.demonstrate_thread = None
        self.blinking_running = False
        self.preview_running = False
        self.achieved_img_id = None
        self.canvas_step_notes = None
        self.status_button = None
        self.module_path_canvas = None
        self.module_path_canvas_height = 100
        self.module_path_canvas_width = 500
        self.hear_user_button = None
        self.scenario = None
        self.stop_button = None
        self.demonstrate_button = None
        self.debug = True
        self.ui_root_tk = None
        self.pause_between_notes = 1
        self.notes_sequence = None
        self.current_expected_note_step = 0
        self.selected_instrument_training = None
        self.exercise_achieved_img = self.img.resize((20, 20), Image.LANCZOS)
        self.achieved_pyimg = None

    def display(self, parent_frame: Frame):
        self.ui_root_tk = parent_frame
        self.exercise_labelframe = LabelFrame(self.ui_root_tk, text='Your performance')
        self.exercise_labelframe.grid(row=1, column=0)
        self.demonstrate_button = Button(self.exercise_labelframe, text='Hear exercise',
                                         command=self.do_demonstrate_exercise, state=DISABLED)
        self.demonstrate_button.grid(row=0, column=0)

        self.hear_user_button = Button(self.exercise_labelframe, text='Try it...', command=self.do_hear_user, state=DISABLED)
        self.hear_user_button.grid(row=0, column=1)

        self.module_path_canvas = Canvas(self.exercise_labelframe, width=self.module_path_canvas_width,
                                         height=self.module_path_canvas_height,
                                         borderwidth=1, background='white')
        self.module_path_canvas.grid(row=1, column=0, columnspan=4)

    def set_instrument(self, instrument):
        self.selected_instrument_training = instrument
        if self.selected_instrument_training and self.scenario:
            self.hear_user_button.config(state=NORMAL)

    def set_training_module(self, module_content: dict):
        """
        registers the training module content + displays the module checkpoints
        :param module_content: ex {"name": "C chord", "description": "", "play_notes": "C3-E3-G3", "check condition": 100}
        :return:
        """
        self.scenario = deepcopy(module_content)
        if self.scenario:
            self.demonstrate_button.config(state=NORMAL)
        if self.selected_instrument_training and self.scenario:
            self.hear_user_button.config(state=NORMAL)
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
        self.module_path_canvas.create_line(0, self.module_path_canvas_height / 2 - note_width / 2 + margin_N,
                                            self.module_path_canvas_width,
                                            self.module_path_canvas_height / 2 - note_width / 2 + margin_N,
                                            fill="lightgray", width=5)
        for step in self.notes_sequence:
            nw_x = margin_W + step_index * note_interval + 3
            nw_y = self.module_path_canvas_height / 2
            se_x = nw_x + note_width
            se_y = nw_y + note_width
            step_index += 1
            oval_id = self.module_path_canvas.create_oval(nw_x, nw_y - note_width / 2, se_x, se_y - note_width / 2, fill="#DDDDDD",
                                                          outline="#AAAAAA", width=1, tags=step)
            text_id = self.module_path_canvas.create_text(nw_x + note_width / 2, nw_y - note_width / 2 + margin_N,
                                                          text=step, font=font, anchor=CENTER, fill="#222222",
                                                          tags=step)
            self.canvas_step_notes.append((oval_id, text_id))

        self.achieved_pyimg = PIL.ImageTk.PhotoImage(self.exercise_achieved_img)
        self.achieved_img_id = self.module_path_canvas.create_image(self.module_path_canvas_width - 20,
                                                                    self.module_path_canvas_height / 2
                                                                    + margin_N - note_width,
                                                                    anchor=NW, image=self.achieved_pyimg,
                                                                    state='hidden')
        Tk.update(self.ui_root_tk)

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
                self.module_path_canvas.itemconfigure(self.achieved_img_id, state='normal')
                self.do_stop_exercise()
                Tk.update(self.ui_root_tk)
        except ValueError:
            if self.debug:
                print("Not a note")

    def do_demonstrate_exercise(self):
        """
        demonstrate the sequence to practice
        :return:
        """
        if self.selected_instrument_training and self.scenario:
            self.set_training_module(self.scenario)
            # self.selected_instrument_training.debug = True
            self.selected_instrument_training.clear_notes(with_calibration=True)
            self.current_expected_note_step = 0
            for note in self.notes_sequence:
                n = Note(note)
                raw_note_name = n.get_sharp_based_note()
                octave = n.octave
                note = f"{raw_note_name}{octave}"
                self._preview_step(self.current_expected_note_step, "#26ea6e")
                time.sleep(self.pause_between_notes)
                self.selected_instrument_training.mask_note(note)
                self.current_expected_note_step += 1
        self.current_expected_note_step = 0

    def do_hear_user(self):
        if self.selected_instrument_training and self.scenario:
            # hear
            self.set_training_module(self.scenario)
            self.selected_instrument_training.clear_notes(with_calibration=True)
            self.current_expected_note_step = 0
            self.selected_instrument_training.do_start_hearing(self)

    def do_stop_exercise(self):
        self.selected_instrument_training.do_stop_hearing()

    def demonstrate_step(self, step: int):
        """
        the note will temporarily blink to acknowledge what has been heard
        :param step:
        :return:
        """
        self._preview_step(step, "#26ea6e")

    def _preview_step(self, note_index: int, color: str):
        """
        the note will temporarily blink to acknowledge what has been heard
        :param note:
        :return:
        """
        self.preview_running = True
        note = self.notes_sequence[note_index]
        raw_note_name = note[:-1]
        if 'b' in raw_note_name:
            raw_note_name = Note.CHROMATIC_SCALE_SHARP_BASED[Note.CHROMATIC_SCALE_FLAT_BASED.index(raw_note_name)]
        octave = int(note[-1])
        note = f"{raw_note_name}{octave}"
        self.selected_instrument_training.do_play_note(raw_note_name, octave)
        self.validate_current_step()
        self.selected_instrument_training.show_note(note)
        the_note = self.canvas_step_notes[note_index]
        if self.debug:
            print(note_index, raw_note_name, octave, the_note)
        Tk.update(self.ui_root_tk)
        self.module_path_canvas.itemconfigure(the_note[0], state='normal', fill="#DDDDDD")
        self.module_path_canvas.itemconfigure(the_note[1], state='normal')
        self.preview_running = False

    def validate_current_step(self):
        """
        the note will temporarily blink to acknowledge what has been heard
        :param note:
        :return:
        """
        the_note = self.canvas_step_notes[self.current_expected_note_step]
        self.module_path_canvas.itemconfigure(the_note[0], state='normal', fill="#26ea6e")
        self.module_path_canvas.itemconfigure(the_note[1], state='normal')

    def make_note_blink(self, note_index: int, new_color: str):
        self.blinking_running = True
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
        self.blinking_running = False
