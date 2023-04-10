import time
from tkinter.constants import *

from tests.testing_framework.page_objects.root_window_frame import RootWindowFrame


class NoteRecorderFrame:
    def __init__(self, root_app: RootWindowFrame):
        self.note_recorder_object = None
        self.root_app = root_app
        # self.objects_in_youtube_mp3_grabbing = youtube_object.frame.children.values()

    def display_frame(self):
        # self.app.open_search_chords_frame()
        self.root_app.open_note_recorder_frame()
        self.note_recorder_object = self.root_app.app.note_recorder

    def start_listening_bars(self, bpm: float, signature: tuple, bars: int):
        # todo metronome
        self.note_recorder_object.do_start_recording()
        # todo sleep
        # todo define duration
        duration = self.convert_beat_to_seconds(bpm=bpm, signature=signature, bars=bars)
        print("listenning duration:", duration)
        time.sleep(duration)
        self.note_recorder_object.do_stop_recording()

    def start_listening_undefined(self):
        self.note_recorder_object.do_start_recording()

    def stop_listening(self):
        self.note_recorder_object.do_stop_recording()

    def get_song(self) -> {}:
        return self.note_recorder_object.selected_instrument.song

    @staticmethod
    def convert_beat_to_seconds(bpm: float, signature: tuple, bars: int):
        return 60 / float(bpm) * bars / signature[0]
