import threading
import time

from pyharmony import RootWindow


class RootWindowFrame:
    def __init__(self):
        self.app = None

    def open(self):
        """
        open the root windows in a thread for the mainloop()
        :return:
        """
        listen_thread = threading.Thread(target=self._do_launch_mainloop, name="mainloop")
        listen_thread.start()
        time.sleep(2)

    def _do_launch_mainloop(self):
        """
        mainloop()
        :return:
        """
        self.app = RootWindow()
        self.app.mainloop()

    def get_out_file(self) -> str:
        """
        provides the path of the recorded youtube file
        :return:
        """
        return self.app.record_youtube.out_file

    def quit(self):
        """
        quit the root window & mainloop
        :return:
        """
        self.app.quit()

    def open_youtube_recorder_frame(self):
        """
        open the youtube recorder frame
        :return:
        """
        self.app.do_youtube_mp3_grabbing()

    def open_search_chords_frame(self):
        self.app.do_search_chords()

