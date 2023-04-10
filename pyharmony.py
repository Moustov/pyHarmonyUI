import tkinter
from importlib.metadata import version
from tkinter import Label, Menu, messagebox, Frame
# https://www.youtube.com/watch?v=XhCfsuMyhXo&list=PLCC34OHNcOtoC6GglhF3ncJ5rLwQrLGnV&index=6
from tkinter.filedialog import askopenfilename

from audio.capture_sound_fft import CaptureSoundFFT
from audio.capture_sound_plot import capture_and_display_sound
from file_capabilities.download_mp3_youtube import DownloadMP3Youtube
from learning.learning_center import LearningCenter
from note_recorder.note_recorder import NoteRecorder
from ultimate_guitar.search_cadence import SearchSongFromCadence
from ultimate_guitar.search_chords import SearchSongFromChords


#https://stackoverflow.com/questions/61274017/splitting-windows-using-frames-in-tkinter-and-python
#https://www.geeksforgeeks.org/create-multiple-frames-with-grid-manager-using-tkinter/
#https://www.geeksforgeeks.org/tkinter-separator-widget/

class RootWindow(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self.note_recorder = None
        self.learning_center = None
        self.search_chords = None
        self.search_cadence = None
        self.live_hearing = None
        self.menu_bar = None
        self._set_layout()
        self.record_youtube = None

    def _set_layout(self):
        self.title('Harmony tools')
        self.geometry('1400x768')
        self._add_menu()
        self._add_content()

    def _add_content(self):
        my_label = Label(self, text="Harmony tools")
        my_label.grid(row=0, column=0)

    def _add_menu(self):
        """
        https://koor.fr/Python/Tutoriel_Tkinter/tkinter_menu.wp
        https://tkdocs.com/tutorial/menus.html
        :return:
        todo short cuts : m_edit.entryconfigure('Paste', accelerator='Command+V')
        todo underline : m.add_command(label='Path Browser', underline=5)  # underline "B"
        """
        self.menu_bar = Menu(self)

        menu_file = Menu(self.menu_bar, tearoff=0)
        menu_file.add_command(label="Youtube MP3 grabbing", command=self.do_youtube_mp3_grabbing)
        menu_file.add_command(label="Sound file loading", command=self.do_something)
        menu_file.add_separator()
        menu_file.add_command(label="Exit", command=self.quit)
        self.menu_bar.add_cascade(label="File", menu=menu_file)

        menu_audio = Menu(self.menu_bar, tearoff=0)
        menu_audio.add_command(label="Live hearing", command=self.do_live_hearing)
        menu_audio.add_command(label="Live analysis", command=self.do_FFT_hearing)
        menu_audio.add_separator()
        menu_audio.add_command(label="Learning Center", command=self.do_learning_center)
        menu_audio.add_separator()
        menu_audio.add_command(label="Note recorder", command=self.do_record_notes)
        self.menu_bar.add_cascade(label="Audio", menu=menu_audio)

        menu_search = Menu(self.menu_bar, tearoff=0)
        menu_search.add_command(label="Chords Search UG", command=self.do_search_chords)
        menu_search.add_command(label="Cadence Search UG", command=self.do_search_cadence)
        self.menu_bar.add_cascade(label="Search", menu=menu_search)

        menu_score = Menu(self.menu_bar, tearoff=0)
        menu_score.add_command(label="Transpose", command=self.do_about)
        menu_score.add_command(label="Find chords from tabs", command=self.do_about)
        self.menu_bar.add_cascade(label="Score", menu=menu_score)

        menu_help = Menu(self.menu_bar, tearoff=0)
        menu_help.add_command(label="About", command=self.do_about)
        self.menu_bar.add_cascade(label="Help", menu=menu_help)
        self.config(menu=self.menu_bar)

    def do_learning_center(self):
        self.clear_root()
        self.learning_center = LearningCenter()
        frame = self.learning_center.get_ui_frame(self)
        frame.grid(row=1, column=0, columnspan=5, sticky='nsew', padx=5, pady=5)

    def do_FFT_hearing(self):
        c = CaptureSoundFFT()
        c.capture()

    def do_live_hearing(self):
        capture_and_display_sound()

    def do_youtube_mp3_grabbing(self):
        self.clear_root()
        self.record_youtube = DownloadMP3Youtube()
        frame = self.record_youtube.get_ui_frame(self)
        frame.grid(row=1, column=0, columnspan=5, sticky='nsew', padx=5, pady=5)

    def do_about(self):
        messagebox.showinfo("Harmony tools", f"(c) C. Moustier - 2023\nBased on pyHarmonyTooling v.{version('pyHarmonyTooling')} - https://github.com/Moustov/pyharmonytooling")

    def open_file(self):
        file = askopenfilename(title="Choose the file to open",
                               filetypes=[("PNG image", ".png"), ("GIF image", ".gif"), ("All files", ".*")])
        print(file)

    def do_something(self):
        messagebox.showinfo("Harmony tools", f"Not yet implemented :-P")

    def do_search_chords(self):
        self.clear_root()
        self.search_chords = SearchSongFromChords()
        frame = self.search_chords.get_ui_frame(self)
        frame.grid(row=1, column=0, columnspan=5, sticky='nsew', padx=5, pady=5)

    def do_search_cadence(self):
        self.clear_root()
        self.search_cadence = SearchSongFromCadence()
        frame = self.search_cadence.get_ui_frame(self)
        frame.grid(row=1, column=0, columnspan=5, sticky='nsew', padx=5, pady=5)

    def do_record_notes(self):
        self.clear_root()
        self.note_recorder = NoteRecorder()
        frame = self.note_recorder.get_ui_frame(self)
        frame.grid(row=1, column=0, columnspan=5, sticky='nsew', padx=5, pady=5)

    def clear_root(self):
        if self.record_youtube:
            self.record_youtube.frame.grid_remove()
        if self.learning_center:
            self.learning_center.frame.grid_remove()
        if self.search_chords:
            self.search_chords.frame.grid_remove()
        if self.search_cadence:
            self.search_cadence.frame.grid_remove()
        if self.note_recorder:
            self.note_recorder.frame.grid_remove()




if __name__ == "__main__":
    app = RootWindow()
    app.mainloop()
