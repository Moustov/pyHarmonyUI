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


class MicListener:
    def set_current_note(self, new_note: str, heard_freq: float = 0.0, closest_pitch: float = 0.0):
        pass


class MicAnalyzer:
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
        # analyzer data
        self.mic_timer = 0.005
        self.length = 0
        self.HANN_WINDOW = np.hanning(self.WINDOW_SIZE)
        self.window_samples = [0 for _ in range(self.WINDOW_SIZE)]
        self.noteBuffer = ["1", "2"]
        self.debug = True
        self.listeners = []

    def add_listener(self, l: MicListener):
        self.listeners.append(l)

    def do_start_hearing(self):
        self.is_listening = True
        self.download_thread = threading.Thread(target=self._listen, name="_listen")
        self.download_thread.start()

    def do_stop_hearing(self):
        self.is_listening = False
        self.download_thread.join()

    def _listen(self):
        self.start_time = datetime.now()
        with sd.InputStream(channels=1, callback=self.callback, blocksize=self.WINDOW_STEP,
                            samplerate=self.SAMPLE_FREQ):
            while self.is_listening:
                time.sleep(self.mic_timer)

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
                self._set_current_note(closest_note, max_freq, closest_pitch)
            else:
                self._set_current_note("-")
        else:
            self._set_current_note("-")
            print('no input')

    def _set_current_note(self, new_note: str, heard_freq: float = 0.0, closest_pitch: float = 0.0):
        """

        :param new_note: eg "A#2" or "B3"
        :return:
        """
        # print("_set_current_note", new_note)
        if new_note == "-" or len(new_note) in [2, 3]:
            if new_note == "-":
                if self.debug:
                    print(f" - Silence: {new_note}")
            else:
                if self.debug:
                    print(f" - Closest note: {new_note} {heard_freq}/{closest_pitch}")
            for l in self.listeners:
                l.set_current_note(new_note, heard_freq, closest_pitch)


if __name__ == "__main__":
    nt = MicAnalyzer()
    nt.do_start_hearing()