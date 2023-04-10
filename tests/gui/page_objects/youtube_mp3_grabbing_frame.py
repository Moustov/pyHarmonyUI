from tkinter.constants import *

from tests.gui.page_objects.root_window_frame import RootWindowFrame


class YoutubeMp3GrabbingFrame:
    def __init__(self, root_app: RootWindowFrame):
        self.youtube_object = None
        self.root_app = root_app
        # self.objects_in_youtube_mp3_grabbing = youtube_object.frame.children.values()

    def set_youtube_url(self, text: str):
        self.youtube_object.youtube_url.delete(0, END)
        self.youtube_object.youtube_url.insert(0, text)

    def get_youtube_url(self) -> str:
        self.youtube_object.focus_force()
        return self.youtube_object.youtube_url.get()

    def click_button_download_mp3_from_url(self):
        self.youtube_object.do_download_mp3_from_url()
        self.youtube_object.download_thread.join()

    def display_frame(self):
        self.root_app.open_youtube_recorder_frame()
        self.youtube_object = self.root_app.app.record_youtube
