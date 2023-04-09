import threading
from unittest import TestCase

import pyautogui as gui
import time

from pyharmony import RootWindow


class TestRootWindow(TestCase):
    app = None

    def _testfirefox(self):
        screenWidth, screenHeight = gui.size()
        gui.moveTo(0, screenHeight)
        gui.click()
        gui.typewrite('Firefox', interval=0.25)
        gui.press('enter')
        time.sleep(2)
        gui.keyDown('alt')
        gui.press(' ')
        gui.press('x')
        gui.keyUp('alt')
        gui.click(250, 22)
        gui.click(371, 51)
        gui.typewrite('https://medium.com/financeexplained')
        gui.press('enter')

    def test_youtube_mp3_grabbing(self):
        listen_thread = threading.Thread(target=self._do_launch_mainloop, name="mainloop")
        listen_thread.start()
        time.sleep(3)
        x = self.app.menu_bar.entrycget(1, "label")
        print(x)
        # print(self.app.menu_bar.entrycget(0, 'label'))
        # print(self.app.menu_bar.entryconfigure(0))
        self.app.do_youtube_mp3_grabbing()
        objects_in_youtube_mp3_grabbing = self.app.children.values()
        assert False

    def _do_launch_mainloop(self):
        self.app = RootWindow()
        self.app.mainloop()



