import os
from unittest import TestCase

from tests.gui.page_objects.root_window_frame import RootWindowFrame
from tests.gui.page_objects.youtube_mp3_grabbing_frame import YoutubeMp3GrabbingFrame


class TestYoutubeMp3Grabbing(TestCase):
    youtube_frame = None
    root_window_frame = None

    def setUp(self):
        self.root_window_frame = RootWindowFrame()
        self.root_window_frame.open()
        self.root_window_frame.open_youtube_recorder_frame()

    def test_youtube_mp3_grabbing(self):
        # SETUP
        self.youtube_frame = YoutubeMp3GrabbingFrame(self.root_window_frame)
        self.youtube_frame.display_frame()
        self.youtube_frame.set_youtube_url("https://www.youtube.com/watch?v=KHcKA6zK5T8")
        self.youtube_frame.click_button_download_mp3_from_url()
        print("output file:" + self.root_window_frame.get_out_file())
        # TEST
        assert os.path.isfile(self.root_window_frame.get_out_file())

    def tearDown(self):
        # test_youtube_mp3_grabbing
        try:
            os.remove(self.root_window_frame.get_out_file())
        except FileNotFoundError:
            pass
        except Exception as ex:
            print("Issue found in tearDown - " + str(ex))
        # killing root window
        self.root_window_frame.quit()




