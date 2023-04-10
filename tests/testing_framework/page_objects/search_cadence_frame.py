from tkinter.constants import *

from tests.testing_framework.page_objects.root_window_frame import RootWindowFrame


class SearchCadenceFrame:
    def __init__(self, root_app: RootWindowFrame):
        self.search_cadence_object = None
        self.root_app = root_app
        # self.objects_in_youtube_mp3_grabbing = youtube_object.frame.children.values()

    def display_frame(self):
        # self.app.open_search_chords_frame()
        self.root_app.open_search_cadence_frame()
        self.search_cadence_object = self.root_app.app.search_cadence

    def set_cadence_to_search(self, cadence: str):
        self.search_cadence_object.pattern.delete(0, END)
        self.search_cadence_object.pattern.insert(0, cadence)

    def get_chords_to_search(self) -> str:
        return self.search_cadence_object.pattern.get()

    def click_button_search_cadence(self):
        self.search_cadence_object.do_search_songs()
        self.search_cadence_object.download_thread.join()

    def get_found_songs(self) -> {}:
        songs = self.search_cadence_object.list_of_songs.get_children()
        res = {}
        for i in songs:
            values = self.search_cadence_object.list_of_songs.item(i)['values']
            if values:
                data = self.search_cadence_object.list_of_songs.item(i)['values']
                res[i] = data
        return res
