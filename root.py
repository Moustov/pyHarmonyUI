import tkinter
from importlib.metadata import version
from tkinter import Label, Menu, messagebox, Frame
# https://www.youtube.com/watch?v=XhCfsuMyhXo&list=PLCC34OHNcOtoC6GglhF3ncJ5rLwQrLGnV&index=6
from tkinter.filedialog import askopenfilename

from audio.capture_sound_fft import CaptureSoundFFT
from audio.capture_sound_plot import capture_and_display_sound
from instrument.guitar_training import GuitarTraining
from learning.learning_center import LearningCenter
from file_capabilities.download_mp3_youtube import DownloadMP3Youtube
from instrument.voice_training import VoiceTraining
from ultimate_guitar.search_cadence import SearchSongFromCadence
from ultimate_guitar.search_chords import SearchSongFromChords


#https://stackoverflow.com/questions/61274017/splitting-windows-using-frames-in-tkinter-and-python
#https://www.geeksforgeeks.org/create-multiple-frames-with-grid-manager-using-tkinter/
#https://www.geeksforgeeks.org/tkinter-separator-widget/

class RootWindow(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self.search_chords = None
        self.search_cadence = None
        self.live_hearing = None
        self.menu_bar = None
        self._set_layout()

    def _set_layout(self):
        self.title('Harmony tools')
        self.geometry('1400x768')
        self._add_menu()
        self._add_content()

    def _add_content(self):
        my_label = Label(self, text="Harmony tools")
        my_label.pack()

    def _add_menu(self):
        """
        https://koor.fr/Python/Tutoriel_Tkinter/tkinter_menu.wp
        :return:
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
        lc = LearningCenter()
        f = Frame()
        f.pack()
        lc.display(f)

    def do_FFT_hearing(self):
        c = CaptureSoundFFT()
        c.capture()

    def do_live_hearing(self):
        capture_and_display_sound()

    def do_youtube_mp3_grabbing(self):
        d = DownloadMP3Youtube()
        f = Frame()
        f.pack()
        d.display(f)

    def do_about(self):
        messagebox.showinfo("Harmony tools", f"(c) C. Moustier - 2023\nBased on pyHarmonyTooling v.{version('pyHarmonyTooling')} - https://github.com/Moustov/pyharmonytooling")

    def open_file(self):
        file = askopenfilename(title="Choose the file to open",
                               filetypes=[("PNG image", ".png"), ("GIF image", ".gif"), ("All files", ".*")])
        print(file)

    def do_something(self):
        messagebox.showinfo("Harmony tools", f"Not yet implemented :-P")

    def do_search_chords(self):
        f = Frame()
        f.pack()
        if not self.search_chords:
            self.search_chords = SearchSongFromChords()
        self.search_chords.display(f)

    def do_search_cadence(self):
        f = Frame()
        f.pack()
        if not self.search_cadence:
            self.search_cadence = SearchSongFromCadence()
        self.search_cadence.display(f)


if __name__ == "__main__":
    app = RootWindow()
    app.mainloop()
