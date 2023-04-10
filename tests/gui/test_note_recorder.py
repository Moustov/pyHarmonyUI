from unittest import TestCase

from tests.testing_framework.page_objects.note_recorder_frame import NoteRecorderFrame
from tests.testing_framework.page_objects.root_window_frame import RootWindowFrame
from tests.testing_framework.page_objects.search_cadence_frame import SearchCadenceFrame


class TestNoteRecorder(TestCase):
    note_recorder_frame = None
    root_window_frame = None

    def setUp(self):
        self.root_window_frame = RootWindowFrame()
        self.root_window_frame.open()
        self.root_window_frame.open_note_recorder_frame()

    def test_note_recorder_bars(self):
        # SETUP
        self.note_recorder_frame = NoteRecorderFrame(self.root_window_frame)
        self.note_recorder_frame.display_frame()
        self.note_recorder_frame.start_listening_bars(bpm=120, signature=(4, 4), bars=12)   # 1.5 sec
        # TEST
        song_heard = self.note_recorder_frame.get_song()
        print("Songs found:", song_heard)
        assert song_heard

    def tearDown(self):
        # killing root window
        self.root_window_frame.quit()




