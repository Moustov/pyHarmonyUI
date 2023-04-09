import threading
import tkinter
from tkinter import Frame, NO, CENTER, Text, Label, Entry, Button, END
from tkinter.ttk import Treeview, Progressbar

from pyharmonytools.song.ultimate_guitar_search import UltimateGuitarSearch
from pyharmonytools.song.ultimate_guitar_song import UltimateGuitarSong


class SearchSongFromChords(tkinter.Tk):
    def __init__(self):
        self.list_of_songs = None
        self.song = None
        self.pattern = None
        self.pattern_label = None
        self.search_button = None
        self.progress_bar = None
        self.ug_engine = UltimateGuitarSearch()

    def get_ui_frame(self, root: tkinter.Tk) -> Frame:
        self.frame = Frame(root)
        self.pattern_label = Label(self.frame, text="Chord pattern to search")
        self.pattern_label.pack()
        self.pattern = Entry(self.frame)
        self.pattern.pack()

        self.progress_bar = Progressbar(self.frame, orient='horizontal', mode='indeterminate', length=280)
        self.progress_bar.pack()

        self.search_button = Button(self.frame,text='Search', command=self._do_search_songs)
        self.search_button.pack()
        self.list_of_songs = Treeview(self.frame)
        self.list_of_songs['columns'] = ('Author', 'Title', 'URL')
        self.list_of_songs.column("#0", width=0, stretch=NO)
        self.list_of_songs.column('Author', anchor=CENTER, width=80)
        self.list_of_songs.column('Title', anchor=CENTER, width=80)
        self.list_of_songs.column('URL', anchor=CENTER, width=80)
        self.list_of_songs.heading("#0", text="", anchor=CENTER)
        self.list_of_songs.heading('Author', text="Author", anchor=CENTER)
        self.list_of_songs.heading('Title', text="Title", anchor=CENTER)
        self.list_of_songs.heading('URL', text="URL", anchor=CENTER)
        # self.list_of_songs.bind("<Double-1>", self._on_double_click)
        # http://tkinter.fdex.eu/doc/event.html#events
        self.list_of_songs.bind("<ButtonRelease-1>", self._on_song_select)
        self.list_of_songs.pack()

        self.song = Text(self.frame)
        self.song.pack()
        return self.frame

    def _do_search_songs(self):
        download_thread = threading.Thread(target=self._download_songs, name="_download_songs")
        download_thread.start()

    def _download_songs(self):
        self.progress_bar.start()
        query = self.pattern.get()
        songs = self.ug_engine.search(query, 20)
        song = UltimateGuitarSong()
        index = 0
        for s in songs:
            song.extract_song_from_url(s)
            self.list_of_songs.insert(parent="", index='end', iid=index, text="",
                                      values=(song.artist, song.song_title, song.url))
            index += 1
        self.progress_bar.stop()
        self.list_of_songs.pack()

    def _on_song_select(self, event):
        item = self.list_of_songs.item(self.list_of_songs.selection())['values']
        print("Selected item : ", item)
        ug_song = UltimateGuitarSong()
        ug_song.extract_song_from_url(item[2])
        self.song.configure(state='normal')
        song_string = ""
        self.song.delete('1.0', END)
        for (c, l) in zip(ug_song.line_of_chords, ug_song.lyrics):
            song_string += str(c) + "\n"
            self.song.insert('end', str(c))
            self.song.insert('end', "\n")
            song_string += str(l) + "\n"
            self.song.insert('end', str(l))
            self.song.insert('end', "\n")
        print(song_string)
        self.song.configure(state='disabled')

