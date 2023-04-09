from tkinter.constants import *

from file_capabilities.download_mp3_youtube import DownloadMP3Youtube


class YoutubeMp3GrabbingFrame:
    def __init__(self, youtube_object: DownloadMP3Youtube):
        self.youtube_object = youtube_object
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
