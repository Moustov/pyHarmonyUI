import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy import fftpack
from pvrecorder import PvRecorder
import threading
import tkinter
from tkinter import Label, Button
from tkinter.ttk import Progressbar

from pyharmonytools.song.ultimate_guitar_search import UltimateGuitarSearch

from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# https://python-sounddevice.readthedocs.io/en/0.4.5/examples.html#plot-microphone-signal-s-in-real-time


class AudioLiveHearing(tkinter.Tk):
    def __init__(self):
        self.frame_label = None
        self.hear_button = None
        self.progress_bar = None
        self.canvas = None
        self.fig = None
        self.ug_engine = UltimateGuitarSearch()

    def display(self, root: tkinter.Tk):
        self.frame_label = Label(root, text="Audio Live Hearing")
        self.frame_label.pack()

        self.hear_button = Button(root, text='Start Hearing', command=self._do_start_hearing)
        self.hear_button.pack()

        self.progress_bar = Progressbar(root, orient='horizontal', mode='indeterminate', length=280)
        self.progress_bar.pack()

        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)  # A tk.DrawingArea.
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        # f = 10  # Frequency, in cycles per second, or Hertz
        # f_s = 100  # Sampling rate, or number of measurements per second
        # t = np.linspace(0, 2, 2 * f_s, endpoint=False)
        # x = np.sin(f * 2 * np.pi * t)
        # # self.fig, ax = plt.subplots()
        # # ax.plot(t, x)
        # # ax.set_xlabel('Time [s]')
        # # ax.set_ylabel('Signal amplitude')
        #
        # X = fftpack.fft(x)
        # freqs = fftpack.fftfreq(len(x)) * f_s
        #
        # self.fig.clear()
        # self.fig, ax = plt.subplots()
        #
        # ax.stem(freqs, np.abs(X))
        # ax.set_xlabel('Frequency in Hertz [Hz]')
        # ax.set_ylabel('Frequency Domain (Spectrum) Magnitude')
        # ax.set_xlim(-f_s / 2, f_s / 2)
        # ax.set_ylim(-5, 110)
        # self.canvas.draw()
        #

    def _do_start_hearing(self):
    #     download_thread = threading.Thread(target=self._hear_sound, name="_hearing_sound")
    #     download_thread.start()
    #
    # def _hear_sound(self):
        self.progress_bar.start()
        # https://picovoice.ai/blog/how-to-record-audio-using-python/
        for index, device in enumerate(PvRecorder.get_audio_devices()):
            print(f"[{index}] {device}")
        # use the default microphone (-1)
        sample_duration_ms = 32
        recorder = PvRecorder(device_index=-1, buffer_size_msec=sample_duration_ms, frame_length=512)  # 32 milliseconds of 16 kHz audio
        try:
            dt = 1000.0 / sample_duration_ms
            recorder.start()
            nb_samples = 0
            while True:
                nb_samples += 1
                frame = recorder.read()
                if nb_samples % 100 == 0:
                    # https://www.oreilly.com/library/view/elegant-scipy/9781491922927/ch04.html
                    X = fftpack.fft(frame)
                    freqs = fftpack.fftfreq(len(frame)) * dt

                    self.fig.clear()
                    self.fig, ax = plt.subplots()

                    ax.stem(freqs, np.abs(X))
                    ax.set_xlabel('Frequency in Hertz [Hz]')
                    ax.set_ylabel('Frequency Domain (Spectrum) Magnitude')
                    ax.set_xlim(0, dt)
                    ax.set_ylim(0, 1000)
                    self.canvas.draw()
                    plt.show()

                # https://www.geeksforgeeks.org/how-to-extract-frequency-associated-with-fft-values-in-python/
        except KeyboardInterrupt:
            recorder.stop()
        finally:
            recorder.delete()
        self.progress_bar.stop()

