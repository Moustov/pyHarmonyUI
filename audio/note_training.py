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
from functools import partial
from math import floor
from tkinter import Button
from tkinter.ttk import Progressbar
import numpy as np
import pygame

from audio.mic_analyzer import MicAnalyzer
from audio.note_player import NotePlayer


class NoteTraining:
    def __init__(self):
        pygame.init()
        self.mic_analyzer = MicAnalyzer()
        self.mic_analyzer.add_listener(self)
        # UI data
        self.progress_bar = None
        self.search_button = None
        self.stop_button = None
        self.ui_root_tk = None
        self.notes_buttons = {}
        self.download_thread = None
        # song data
        self.song = []
        self.sig_up = 4     # 4 fourths in a bar
        self.sig_down = 4   # dealing with fourths
        self.tempo = 60     # 4th per minute
        self.chrono = None
        self.start_time = None
        self.is_listening = False
        self.current_note = None
        self.previous_note = None
        self.note_player = NotePlayer()

    def display(self, ui_root_tk: tkinter.Tk):
        self.ui_root_tk = ui_root_tk
        self.search_button = Button(ui_root_tk, text='Listen', command=self._do_start_hearing)
        self.search_button.grid(row=0, column=4, columnspan=2)
        self.stop_button = Button(self.ui_root_tk, text='Stop', command=self._do_stop_hearing)
        self.stop_button.grid(row=0, column=4, columnspan=2)
        self.stop_button.grid_remove()

        self.progress_bar = Progressbar(ui_root_tk, orient='horizontal', mode='indeterminate', length=280)
        self.progress_bar.grid(row=1, column=0, columnspan=9)
        for octave in range(0, len(self.mic_analyzer.OCTAVE_BANDS)):
            self.notes_buttons[str(octave)] = {}
            half_tone = 0
            for note in self.mic_analyzer.ALL_NOTES:
                half_tone += 1
                self.notes_buttons[str(octave)][note] = Button(ui_root_tk, text=f"{note}{octave}", bg="#AAAAAA",
                                                               width=10, command=partial(self._do_play_note, note,
                                                                                         octave))
                self.notes_buttons[str(octave)][note].grid(row=2 + half_tone, column=octave, padx=5)

    def _do_play_note(self, note, octave):
        print(note, octave)
        c2 = pygame.mixer.Sound(self.note_player.waves[note][octave].astype(np.int16))
        pygame.mixer.Sound.play(c2, loops=100, maxtime=1000, fade_ms=200)

    def _do_start_hearing(self):
        self.stop_button.grid()
        self.search_button.grid_remove()
        self.start_time = datetime.now()
        self.progress_bar.start()
        self.mic_analyzer.do_start_hearing()

    def _do_stop_hearing(self):
        self.mic_analyzer.do_stop_hearing()
        self.progress_bar.stop()
        self.stop_button.grid_remove()
        self.search_button.grid()
        self.display_song()

    def set_current_note(self, new_note: str, heard_freq: float = 0.0, closest_pitch: float = 0.0):
        """

        :param closest_pitch:
        :param heard_freq:
        :param new_note: eg "A#2" or "B3"
        :return:
        """
        # print("_set_current_note", new_note)
        if new_note == "-" or len(new_note) in [2, 3]:
            now = datetime.now()
            self.chrono = (now - self.start_time).microseconds
            self.add_note(new_note)
            self.previous_note = self.current_note
            self.unset_current_note()
            self.current_note = new_note
            if new_note == "-":
                self.unset_current_note()
            else:
                accuracy = 100 - 100*abs((closest_pitch - heard_freq) / closest_pitch)
                self._change_note_aspects(new_note, "#AA8888", accuracy)

    def unset_current_note(self):
        # print("unset", self.current_note)
        if self.current_note and len(self.current_note) in [2, 3]:
            self._change_note_aspects(self.current_note, "#AAAAAA")
            self.previous_note = self.current_note
            self.current_note = "-"

    def _change_note_aspects(self, note: str, bg: str, accuracy: float = -1):
        """

        :param accuracy: percentage of accuracy with perfect pitch
        :param note: eg "A#2" or "B3"
        :param bg:  eg "#112233"
        :return:
        """
        # print("Changed Note:", note, bg, self.current_note)
        if note and len(note) in [2, 3] and bg and len(bg) == 7:
            octave = note[-1]
            the_note = note[0:len(note) - 1]
            half_tone = self.mic_analyzer.ALL_NOTES.index(the_note) + 1
            btn_text = f"{the_note}{octave}"
            if accuracy == -1:
                self.notes_buttons[str(octave)][the_note].configure(bg=bg)
            else:
                btn_text = f"{the_note}{octave} ({round(accuracy, 2)}%)"
                print(btn_text)
                self.notes_buttons[str(octave)][the_note].configure(bg=bg, text=btn_text)

    def add_note(self, new_note):
        if self.previous_note != new_note:
            now = datetime.now()
            self.chrono = (now - self.start_time)
            self.song.append((new_note, self.chrono))
            print("add_note", self.current_note, (new_note, self.chrono))

    def display_song(self):
        for note in self.song:
            print(note[1], ":", note[0])

    def time_string(self, chrono: int):
        """

        :param chrono: number of ms
        :return: eg hh:mm:ss.µµµ
        """
        h_n = chrono // (1000 * 3600)
        h = str(floor(h_n))
        h = "0" * (2 - len(h)) + h
        m = str(chrono // (1000 * 60) % 60)
        m = "0" * (2 - len(m)) + m
        s = str(chrono // 1000 % 60)
        s = "0" * (2 - len(s)) + s
        ms = str(chrono % 1000)
        ms = "0" * (3 - len(ms)) + ms
        res = f"{h}:{m}:{s}.{ms}"
        return res

    def score_string(self, chrono: int, sig_up, sig_down, precision, tempo: int):
        """

        :param sig_up: time signature - upper figure: nb of sig_down per bar
        :param sig_down: time signature - lower figure: unit (1, 2, 4, 8, 16)
        :param tempo: 128 4th per minute
        :param precision: 1, 2, 4, 8, 16
        :param chrono: number of ms
        :return: eg (bar num, 2nd in time, 4th in 2nd, 8th in 4th, 16th in 8th)
        """
        bar_duration = tempo / 60
        bar = chrono // (bar_duration * sig_up)
        sig_up_number = chrono % bar
        sig_down_duration = bar_duration // sig_up_number
        # todo define note tempo according to the precision
        second_duration = 0
        note_duration_sig_down = 0
        return f"bar:{bar} / time:{sig_up_number}"


if __name__ == "__main__":
    nt = NoteTraining()
    root = tkinter.Tk()
    root.title('Harmony tools')
    root.geometry('800x600')
    nt.display(root)
    root.mainloop()
