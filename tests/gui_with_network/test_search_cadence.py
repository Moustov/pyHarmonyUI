from unittest import TestCase

from tests.testing_framework.page_objects.root_window_frame import RootWindowFrame
from tests.testing_framework.page_objects.search_cadence_frame import SearchCadenceFrame


class TestSearchCadence(TestCase):
    search_cadence_frame = None
    root_window_frame = None

    def setUp(self):
        self.root_window_frame = RootWindowFrame()
        self.root_window_frame.open()
        self.root_window_frame.open_search_cadence_frame()

    def test_search_songs_from_cadence(self):
        # SETUP
        self.search_cadence_frame = SearchCadenceFrame(self.root_window_frame)
        self.search_cadence_frame.display_frame()
        self.search_cadence_frame.set_cadence_to_search("I-IV-V")
        self.search_cadence_frame.click_button_search_cadence()
        # TEST
        found_songs = self.search_cadence_frame.get_found_songs()
        print("Songs found:", found_songs)
        assert found_songs

    def tearDown(self):
        # killing root window
        self.root_window_frame.quit()




