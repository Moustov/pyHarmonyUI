from pyharmonytools.harmony.note import Note

from learning.learning_center_interfaces import LearningCenterInterface


class PilotableInstrument:
    def __init__(self):
        self.highest_note = Note("B9")
        self.lowest_note = Note("C0")

    def get_lowest_note(self) -> Note:
        return self.lowest_note

    def get_highest_note(self) -> Note:
        return self.highest_note

    def set_lowest_note(self, lowest_note: Note):
        self.lowest_note = lowest_note

    def set_highest_note(self, highest_note: Note):
        self.highest_note = highest_note

    def clear_notes(self, with_calibration: bool = False):
        """
        reset all notes
        :return:
        """
        pass

    def reset_display(self):
        """
        clear all note
        :return:
        """
        pass

    def show_note(self, new_note: str, color: str):
        """
        shows temporarily a note
        :param color: #RRGGBB in hexa
        :param new_note:
        :return:
        """
        pass

    def mask_note(self, new_note: str):
        """
        reset a note
        :param new_note:
        :return:
        """
        pass

    def set_current_note(self, new_note: str, heard_freq: float = 0.0, closest_pitch: float = 0.0):
        """
        display a note with its accuracy
        :param new_note:
        :param heard_freq:
        :param closest_pitch:
        :return:
        """
        pass

    def unset_current_note(self):
        """
        reset the current note
        :return:
        """
        pass

    def do_play_note(self, note, octave):
        """
        play a note
        :param note:
        :param octave:
        :return:
        """
        pass

    def do_start_hearing(self, lc: LearningCenterInterface):
        """
        triggers the mic to start hearing notes
        :return:
        """
        pass

    def do_stop_hearing(self):
        """
        mute the mic
        :return:
        """
        pass
