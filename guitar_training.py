#!/usr/bin/env python3
"""Plot the live microphone signal(s) with matplotlib.

Matplotlib and NumPy have to be installed.
https://matplotlib.org/stable/api/animation_api.html

    '''
    Guitar tuner script based on the Harmonic Product Spectrum (HPS)
    MIT License
    Copyright (c) 2021 chciken
    See also https://www.chciken.com/digital/signal/processing/2020/05/13/guitar-tuner.html
    '''
"""
import tkinter
from datetime import datetime
from tkinter import Button, Canvas, CENTER
from tkinter.ttk import Progressbar

from pyharmonytools.guitar.guitar_neck.neck import Neck

from mic_analyzer import MicAnalyzer


class GuitarTraining:
    # https://en.wikipedia.org/wiki/Chromesthesia
    # Scriabin's sound-to-color circle of fifths
    note_colors = {
        "C": "#FF0000", "G": "#FF8000", "D": "#FFFF00", "A": "#2FCD30",
        "E": "#C4F2FF", "B": "#8FCAFF", "F": "#AD0031",
        "Gb": "#808CFD", "Db": "#9100FF", "Ab": "#BC76FC", "Eb": "#B8448C", "Bb": "#AB677D",
        "F#": "#808CFD", "C#": "#9100FF", "G#": "#BC76FC", "D#": "#B8448C", "A#": "#AB677D"
    }

    def __init__(self):
        # guitar
        self.guitar_neck = Neck()
        self.MAX_FRET = self.guitar_neck.FRET_QUANTITY_CLASSIC
        self.MAX_STRING = len(self.guitar_neck.TUNING)
        # mic
        self.mic_analyzer = MicAnalyzer()
        self.mic_analyzer.add_listener(self)
        # UI data
        self.progress_bar = None
        self.start_button = None
        self.stop_button = None
        self.ui_root_tk = None
        self.fretboard = None
        self.download_thread = None
        # song data
        self.song = []
        self.sig_up = 4  # 4 fourths in a bar
        self.sig_down = 4  # dealing with fourths
        self.tempo = 60  # 4th per minute
        self.chrono = None
        self.start_time = None
        self.is_listening = False
        self.current_note = None
        self.previous_note = None
        self.fretboard_width = 500
        self.fretboard_height = 200
        self.string_interval_size = 0
        self.margin_N = 10
        self.margin_S = 10
        self.margin_E = 10
        self.margin_W = 20

    def display(self, ui_root_tk: tkinter.Tk):
        self.ui_root_tk = ui_root_tk
        self.start_button = Button(ui_root_tk, text='Listen', command=self._do_start_hearing)
        self.start_button.grid(row=0, column=0)
        self.stop_button = Button(self.ui_root_tk, text='Stop', command=self._do_stop_hearing)
        self.stop_button.grid(row=0, column=0)
        self.stop_button.grid_remove()

        self.progress_bar = Progressbar(ui_root_tk, orient='horizontal', mode='indeterminate', length=280)
        self.progress_bar.grid(row=1, column=0)
        self.fretboard = Canvas(ui_root_tk, width=self.fretboard_width, height=self.fretboard_height,
                                borderwidth=1, background='gray')
        self.fretboard.grid(row=2, column=0)
        self.draw_fretboard()
        # self.draw_finger_on_neck("D", the_string='E', the_fret=5)
        # self.draw_finger_on_neck("D", the_string='A', the_fret=6)
        # self.draw_finger_on_neck("D", the_string='D', the_fret=7)
        # self.draw_finger_on_neck("D", the_string='G', the_fret=8)
        # self.draw_finger_on_neck("D", the_string='B', the_fret=9)
        # self.draw_finger_on_neck("D", the_string='e', the_fret=10)
        # self.draw_note("A")
        # self.draw_note("B")
        # self.draw_note("C")
        # self.draw_note("D")
        # self.draw_note("E")
        # self.draw_note("F")
        # self.draw_note("G")
        # self.draw_note("A#")
        # self.draw_note("Ab")
        # self.draw_note("Bb")
        # self.draw_note("C#")
        # self.draw_note("Db")
        # self.draw_note("D#")
        # self.draw_note("Eb")
        # self.draw_note("F#")
        # self.draw_note("Gb")
        # self.draw_note("G#")

    def _do_nothing(self):
        pass

    def _do_start_hearing(self):
        self.stop_button.grid()
        self.start_button.grid_remove()
        self.start_time = datetime.now()
        self.progress_bar.start()
        self.mic_analyzer.do_start_hearing()

    def _do_stop_hearing(self):
        self.mic_analyzer.do_stop_hearing()
        self.progress_bar.stop()
        self.stop_button.grid_remove()
        self.start_button.grid()
        self.display_song()

    def set_current_note(self, new_note: str, heard_freq: float = 0.0, closest_pitch: float = 0.0):
        """

        :param new_note: eg "A#2" or "B3"
        :return:
        """
        # print("_set_current_note", new_note)
        if new_note == "-" or len(new_note) in [2, 3]:
            now = datetime.now()
            self.chrono = (now - self.start_time).microseconds
            self.add_note(new_note)
            self.previous_note = self.current_note
            self.current_note = new_note
            if new_note == "-":
                self._unset_current_note()
            else:
                self._change_note_bg(new_note, "#AA8888")

    def _unset_current_note(self):
        # print("unset", self.current_note)
        if self.current_note and len(self.current_note) in [2, 3]:
            self._change_note_bg(self.current_note, "#AAAAAA")
            self.previous_note = self.current_note
            self.current_note = "-"

    def _change_note_bg(self, note: str, bg: str):
        """

        :param note: eg "A#2" or "B3"
        :param bg:  eg "#112233"
        :return:
        """
        # print("Changed Note:", note, bg, self.current_note)
        if note and len(note) in [2, 3] and bg and len(bg) == 7:
            octave = note[-1]
            the_note = note[0:len(note) - 1]
            half_tone = self.mic_analyzer.ALL_NOTES.index(the_note) + 1
            self.draw_note(the_note)

    def add_note(self, new_note):
        if self.previous_note != new_note:
            now = datetime.now()
            self.chrono = (now - self.start_time)
            self.song.append((new_note, self.chrono))
            print("add_note", self.current_note, (new_note, self.chrono))

    def display_song(self):
        for note in self.song:
            print(note[1], ":", note[0])

    def draw_note(self, note: str):
        print("draw note", note)
        pos = self.guitar_neck.find_positions_from_note(note)
        for p in pos:
            self.draw_finger_on_neck(note, p[0], p[1])

    def draw_finger_on_neck(self, note: str, the_string: str, the_fret: int):
        """

        :param note:
        :param the_string: E A D G B e
        :param the_fret:
        :return:
        """
        print(note, the_string, the_fret)
        font = ('Helvetica', 10)
        width = 20
        nw_x = self.margin_W + the_fret * self.fretboard_width / self.MAX_FRET + 3
        nw_y = self.string_interval_size * (self.MAX_STRING - self.guitar_neck.TUNING.index(the_string) - 1)
        se_x = nw_x + width
        se_y = nw_y + width
        note_color = self.note_colors[note]
        self.fretboard.create_oval(nw_x, nw_y, se_x, se_y, fill=note_color, outline="#DDD", width=1)
        self.fretboard.create_text(nw_x + width/2, nw_y + width/2, text=note, font=font, anchor=CENTER, fill="#222222")

    def draw_fretboard(self):
        self.fretboard.delete("all")
        height = self.fretboard_height
        width = self.fretboard_width
        print("canvas", height, width)
        self.string_interval_size = (height + self.margin_N) / self.MAX_STRING
        for string in range(0, self.MAX_STRING):
            self.fretboard.create_line(self.margin_W, self.margin_N + string * self.string_interval_size,
                                       width, self.margin_N + string * self.string_interval_size,
                                       fill="yellow", width=2)
            for fret in range(0, self.MAX_FRET):
                self.fretboard.create_line(self.margin_W + fret * width / self.MAX_FRET, self.margin_N,
                                           self.margin_W + fret * width / self.MAX_FRET,
                                           self.margin_N + (self.MAX_STRING - 1) * self.string_interval_size,
                                           fill="lightgray", width=1)
        # nut
        self.fretboard.create_line(self.margin_W, self.margin_N,
                                   self.margin_W, self.margin_N + (self.MAX_STRING - 1) * self.string_interval_size,
                                   fill="lightgray", width=5)
        string_id = 5
        font = ('Helvetica', 12)
        for s in self.guitar_neck.TUNING:
            self.fretboard.create_text(10, self.margin_N + self.string_interval_size * string_id, text=s,
                                       font=font, anchor=CENTER, fill="#000000")
            string_id -= 1


if __name__ == "__main__":
    nt = GuitarTraining()
    root = tkinter.Tk()
    root.title('Harmony tools')
    root.geometry('800x600')
    nt.display(root)
    root.mainloop()
