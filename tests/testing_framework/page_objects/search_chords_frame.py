from tkinter.constants import *

from tests.testing_framework.page_objects.root_window_frame import RootWindowFrame


class SearchChordsFrame:
    def __init__(self, root_app: RootWindowFrame):
        self.search_chord_object = None
        self.root_app = root_app
        # self.objects_in_youtube_mp3_grabbing = youtube_object.frame.children.values()

    def display_frame(self):
        # self.app.open_search_chords_frame()
        self.root_app.open_search_chords_frame()
        self.search_chord_object = self.root_app.app.search_chords

    def set_chords_to_search(self, chord_sequence: str):
        self.search_chord_object.pattern.delete(0, END)
        self.search_chord_object.pattern.insert(0, chord_sequence)

    def get_chords_to_search(self) -> str:
        return self.search_chord_object.pattern.get()

    def click_button_search_chords(self):
        self.search_chord_object.do_search_songs()
        self.search_chord_object.download_thread.join()

    def get_found_songs(self) -> {}:
        songs = self.search_chord_object.list_of_songs.get_children()
        res = {}
        for i in songs:
            values = self.search_chord_object.list_of_songs.item(i)['values']
            if values:
                data = self.search_chord_object.list_of_songs.item(i)['values']
                res[i] = data
        return res
