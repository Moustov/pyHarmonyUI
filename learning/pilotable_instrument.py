from learning.learning_center_interfaces import LearningCenterInterface


class PilotableInstrument:
    def __init__(self):
        pass

    def clear_notes(self):
        """
        reset all notes
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
