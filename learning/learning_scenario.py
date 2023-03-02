import threading
import time
from tkinter import messagebox

from pyharmonytools.harmony.note import Note


class PilotableInstrument:
    def __init__(self):
        pass

    def _do_start_learning(self):
        self.learning_programme = LearningScenario(self)
        self.learning_thread = threading.Thread(target=self.learning_programme.start_learning, name="learning")
        self.learning_thread.start()
        self.clear_notes()

    def clear_notes(self):
        pass

    def show_note(self, new_note: str):
        pass

    def mask_note(self, new_note: str):
        pass

    def set_current_note(self, new_note: str, heard_freq: float = 0.0, closest_pitch: float = 0.0):
        pass

    def unset_current_note(self):
        pass

    def do_play_note(self, note, octave):
        pass

    def do_start_hearing(self):
        pass

    def do_stop_hearing(self):
        pass


class LearningScenario(PilotableInstrument):
    def __init__(self):
        self.pause_between_notes = 1
        self.debug = True
        self.instrument = None
        self.scenario = None
        self.notes_sequence = None
        self.current_expected_note_step = 0

    def start_learning(self, the_instrument: PilotableInstrument, scenario: dict):
        self.instrument = the_instrument
        self.instrument.debug = True
        self.scenario = scenario
        self.notes_sequence = self.scenario["play_notes"].split("-")
        self.current_expected_note_step = 0
        for note in self.notes_sequence:
            raw_note_name = note[:-1]
            raw_note_name = Note.CHROMATIC_SCALE_SHARP_BASED[Note.CHROMATIC_SCALE_FLAT_BASED.index(raw_note_name)]
            octave = int(note[-1])
            self.instrument.show_note(note)
            self.instrument.do_play_note(raw_note_name, octave)
            time.sleep(self.pause_between_notes)
            self.instrument.mask_note(note)
        self.instrument.do_start_hearing()

    def set_current_note(self, new_note: str, heard_freq: float = 0.0, closest_pitch: float = 0.0):
        if self.debug:
            print("expected:", self.notes_sequence[self.current_expected_note_step], "heard:", new_note)
        if self.notes_sequence[self.current_expected_note_step] == new_note:
            self.current_expected_note_step += 1
        if self.debug:
            print("status:", int(100 * self.current_expected_note_step / len(self.notes_sequence)), "%")
        if self.current_expected_note_step == len(self.notes_sequence):
            self.instrument.do_stop_hearing()
            messagebox.showinfo("Harmony tools",
                                f"You did it!")

    def unset_current_note(self):
        pass
