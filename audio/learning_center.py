import tkinter
from tkinter import Button

from audio.learning_scenario import LearningScenario, LearningEnabled
from audio.note_training import NoteTraining


class LearningCenter:
    def __init__(self):
        self.debug = True
        self.learning_scenario = None
        self.stop_button = None
        self.start_button = None
        self.ui_root_tk = None

    def display(self, ui_root_tk: tkinter.Tk):
        self.ui_root_tk = ui_root_tk
        self.start_button = Button(ui_root_tk, text='Start exercise', command=self.do_start_exercise)
        self.start_button.grid(row=0, column=0)
        self.stop_button = Button(self.ui_root_tk, text='Stop exercise', command=self.do_stop_exercise)
        self.stop_button.grid(row=0, column=0)
        self.stop_button.grid_remove()

        # select instrument
        note_training = NoteTraining()
        self.learning_scenario = LearningScenario(note_training)
        note_training.display(self.ui_root_tk)
        # select scenario
        sc = {"name": "C chord", "description": "", "play_notes": "C3-E3-G3", "check condition": 100}
        sc = {"name": "CMaj7 chord", "description": "", "play_notes": "C3-E3-G3-Bb3", "check condition": 100}
        sc = {"name": "C scale", "description": "", "play_notes": "C3-D3-E3-F3-G3-A3-B3", "check condition": 100}
        sc = {"name": "C scale2", "description": "", "play_notes": "C3-D3-E3-F3-G3-A3-B3-A4-G4-F4-E4-D4-C4", "check condition": 100}
        self.learning_scenario.set_scenario(sc)
        # select rapidity & success factors (how hard)

    def do_start_exercise(self):
        pass

    def do_stop_exercise(self):
        pass