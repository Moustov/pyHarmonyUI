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
import copy
import os
import threading
import time
import tkinter
from datetime import datetime
from math import floor
from tkinter import Label, Entry, Button
from tkinter.ttk import Progressbar

import numpy as np
import scipy.fftpack
import sounddevice as sd


class NoteTraining:
    # General settings that can be changed by the user
    SAMPLE_FREQ = 48000  # sample frequency in Hz
    WINDOW_SIZE = 48000  # window size of the DFT in samples
    WINDOW_STEP = 12000  # step size of window
    NUM_HPS = 5  # max number of harmonic product spectrums
    POWER_THRESH = 1e-6  # tuning is activated if the signal power exceeds this threshold
    CONCERT_PITCH = 440  # defining a1
    WHITE_NOISE_THRESH = 0.2  # everything under WHITE_NOISE_THRESH*avg_energy_per_freq is cut off

    WINDOW_T_LEN = WINDOW_SIZE / SAMPLE_FREQ  # length of the window in seconds
    SAMPLE_T_LENGTH = 1 / SAMPLE_FREQ  # length between two samples in seconds
    DELTA_FREQ = SAMPLE_FREQ / WINDOW_SIZE  # frequency step width of the interpolated DFT
    OCTAVE_BANDS = [50, 100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600]
    ALL_NOTES = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]

    def __init__(self):
        # UI data
        self.progress_bar = None
        self.search_button = None
        self.stop_button = None
        self.ui_root_tk = None
        self.notes_buttons = {}
        self.download_thread = None
        # analyzer data
        self.length = 0
        self.HANN_WINDOW = np.hanning(self.WINDOW_SIZE)
        self.window_samples = [0 for _ in range(self.WINDOW_SIZE)]
        self.noteBuffer = ["1", "2"]
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

    def display(self, ui_root_tk: tkinter.Tk):
        self.ui_root_tk = ui_root_tk
        self.search_button = Button(ui_root_tk, text='Listen', command=self._do_start_hearing)
        self.search_button.grid(row=0, column=4, columnspan=2)
        self.stop_button = Button(self.ui_root_tk, text='Stop', command=self._do_stop_hearing)
        self.stop_button.grid(row=0, column=4, columnspan=2)
        self.stop_button.grid_remove()

        self.progress_bar = Progressbar(ui_root_tk, orient='horizontal', mode='indeterminate', length=280)
        self.progress_bar.grid(row=1, column=0, columnspan=9)
        for octave in range(0, len(self.OCTAVE_BANDS)):
            self.notes_buttons[str(octave)] = {}
            half_tone = 0
            for note in self.ALL_NOTES:
                half_tone += 1
                self.notes_buttons[str(octave)][note] = Button(ui_root_tk, text=f"{note}{octave}", bg="#AAAAAA",
                                                               width=5, command=self._do_nothing)
                self.notes_buttons[str(octave)][note].grid(row=2 + half_tone, column=octave, padx=5)

    def _do_nothing(self):
        pass

    def _do_start_hearing(self):
        self.stop_button.grid()
        self.search_button.grid_remove()
        self.is_listening = True
        self.download_thread = threading.Thread(target=self._listen, name="_listen")
        self.download_thread.start()

    def _do_stop_hearing(self):
        self.is_listening = False
        self.download_thread.join()
        self.progress_bar.stop()
        self.stop_button.grid_remove()
        self.search_button.grid()
        self.display_song()

    def _listen(self):
        self.start_time = datetime.now()
        self.progress_bar.start()
        with sd.InputStream(channels=1, callback=self.callback, blocksize=self.WINDOW_STEP,
                            samplerate=self.SAMPLE_FREQ):
            while self.is_listening:
                time.sleep(0.05)

    def find_closest_note(self, pitch):
        """
      This function finds the closest note for a given pitch
      Parameters:
        pitch (float): pitch given in hertz
      Returns:
        closest_note (str): e.g. a, g#, ..
        closest_pitch (float): pitch of the closest note in hertz
      """
        i = int(np.round(np.log2(pitch / self.CONCERT_PITCH) * 12))
        closest_note = self.ALL_NOTES[i % 12] + str(4 + (i + 9) // 12)
        closest_pitch = self.CONCERT_PITCH * 2 ** (i / 12)
        return closest_note, closest_pitch

    def callback(self, indata, frames, time, status):
        """
      Callback function of the InputStream method.
      That's where the magic happens ;)
      """
        if status:
            # print("SS", status)
            return
        if any(indata):
            self.window_samples = np.concatenate((self.window_samples, indata[:, 0]))  # append new samples
            self.window_samples = self.window_samples[len(indata[:, 0]):]  # remove old samples

            # skip if signal power is too low
            signal_power = (np.linalg.norm(self.window_samples, ord=2) ** 2) / len(self.window_samples)
            if signal_power < self.POWER_THRESH:
                os.system('cls' if os.name == 'nt' else 'clear')
                # print("Closest note: ...")
                return

            # avoid spectral leakage by multiplying the signal with a hann window
            hann_samples = self.window_samples * self.HANN_WINDOW
            magnitude_spec = abs(scipy.fftpack.fft(hann_samples)[:len(hann_samples) // 2])

            # supress mains hum, set everything below 62Hz to zero
            for i in range(int(62 / self.DELTA_FREQ)):
                magnitude_spec[i] = 0

            # calculate average energy per frequency for the octave bands
            # and suppress everything below it
            for j in range(len(self.OCTAVE_BANDS) - 1):
                ind_start = int(self.OCTAVE_BANDS[j] / self.DELTA_FREQ)
                ind_end = int(self.OCTAVE_BANDS[j + 1] / self.DELTA_FREQ)
                ind_end = ind_end if len(magnitude_spec) > ind_end else len(magnitude_spec)
                avg_energy_per_freq = (np.linalg.norm(magnitude_spec[ind_start:ind_end], ord=2) ** 2) / (
                        ind_end - ind_start)
                avg_energy_per_freq = avg_energy_per_freq ** 0.5
                for i in range(ind_start, ind_end):
                    magnitude_spec[i] = magnitude_spec[i] if magnitude_spec[
                                                                 i] > self.WHITE_NOISE_THRESH * avg_energy_per_freq else 0

            # interpolate spectrum
            mag_spec_ipol = np.interp(np.arange(0, len(magnitude_spec), 1 / self.NUM_HPS),
                                      np.arange(0, len(magnitude_spec)),
                                      magnitude_spec)
            mag_spec_ipol = mag_spec_ipol / np.linalg.norm(mag_spec_ipol, ord=2)  # normalize it

            hps_spec = copy.deepcopy(mag_spec_ipol)

            # calculate the HPS
            for i in range(self.NUM_HPS):
                tmp_hps_spec = np.multiply(hps_spec[:int(np.ceil(len(mag_spec_ipol) / (i + 1)))],
                                           mag_spec_ipol[::(i + 1)])
                if not any(tmp_hps_spec):
                    break
                hps_spec = tmp_hps_spec

            max_ind = np.argmax(hps_spec)
            max_freq = max_ind * (self.SAMPLE_FREQ / self.WINDOW_SIZE) / self.NUM_HPS

            closest_note, closest_pitch = self.find_closest_note(max_freq)
            max_freq = round(max_freq, 1)
            closest_pitch = round(closest_pitch, 1)

            self.noteBuffer.insert(0, closest_note)  # note that this is a ringbuffer
            self.noteBuffer.pop()

            # os.system('cls' if os.name == 'nt' else 'clear')
            if self.noteBuffer.count(self.noteBuffer[0]) == len(self.noteBuffer):
                # print(f" - Closest note: {closest_note} {max_freq}/{closest_pitch}")
                self._unset_current_note()
                self._set_current_note(closest_note)
            else:
                self._unset_current_note()
                self._set_current_note("-")
        else:
            self._set_current_note("-")
            print('no input')

    def _set_current_note(self, new_note: str):
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
            half_tone = self.ALL_NOTES.index(the_note) + 1
            self.notes_buttons[str(octave)][the_note] = Button(self.ui_root_tk, text=f"{the_note}{octave}", bg=bg,
                                                               width=5, command=self._do_nothing)
            self.notes_buttons[str(octave)][the_note].grid(row=2 + half_tone, column=octave, padx=5)

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
