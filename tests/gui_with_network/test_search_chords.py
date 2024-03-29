from unittest import TestCase

from tests.testing_framework.page_objects.root_window_frame import RootWindowFrame
from tests.testing_framework.page_objects.search_chords_frame import SearchChordsFrame


class TestSearchChords(TestCase):
    search_chords_frame = None
    root_window_frame = None

    def setUp(self):
        self.root_window_frame = RootWindowFrame()
        self.root_window_frame.open()
        self.root_window_frame.open_search_chords_frame()

    def test_search_song_from_chords(self):
        # SETUP
        self.search_chords_frame = SearchChordsFrame(self.root_window_frame)
        self.search_chords_frame.display_frame()
        self.search_chords_frame.set_chords_to_search("C E F")
        self.search_chords_frame.click_button_search_chords()
        # TEST
        found_songs = self.search_chords_frame.get_found_songs()
        print("Songs found:", found_songs)
        assert found_songs

    def tearDown(self):
        # killing root window
        self.root_window_frame.quit()




