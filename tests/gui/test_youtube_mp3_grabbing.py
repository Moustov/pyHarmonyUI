import os
import threading
from unittest import TestCase

import pyautogui as gui
import time

from file_capabilities.download_mp3_youtube import DownloadMP3Youtube
from pyharmony import RootWindow
from tests.gui.youtube_mp3_grabbing_frame import YoutubeMp3GrabbingFrame


class TestYoutubeMp3Grabbing(TestCase):
    app = None
    youtube_frame = None

    def setUp(self):
        listen_thread = threading.Thread(target=self._do_launch_mainloop, name="mainloop")
        listen_thread.start()
        time.sleep(3)

    def test_youtube_mp3_grabbing(self):
        # SETUP
        self.app.do_youtube_mp3_grabbing()
        self.youtube_frame = YoutubeMp3GrabbingFrame(self.app.record_youtube)
        self.youtube_frame.set_youtube_url("https://www.youtube.com/watch?v=KHcKA6zK5T8")
        self.youtube_frame.click_button_download_mp3_from_url()
        print("output file:" + self.app.record_youtube.out_file)
        # TEST
        is_file_present = os.path.isfile(self.app.record_youtube.out_file)
        assert is_file_present

    def tearDown(self):
        # test_youtube_mp3_grabbing
        try:
            os.remove(self.app.record_youtube.out_file)
        except FileNotFoundError:
            pass
        # killing root window
        self.app.quit()

    def _do_launch_mainloop(self):
        self.app = RootWindow()
        self.app.mainloop()



