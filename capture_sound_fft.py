#!/usr/bin/env python3
"""Plot the live microphone signal(s) with matplotlib.

Matplotlib and NumPy have to be installed.
https://matplotlib.org/stable/api/animation_api.html
"""
import argparse
import queue
import sys

from matplotlib import lines
from pyharmonytools.harmony.note import Note
from scipy import signal
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import sounddevice as sd
import numpy as np


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


class CaptureSoundFFT:
    MAX_AMPLITUDE = 400
    MIN_FREQ = 20
    SOUND_LEVEL_MIN = 10
    CALIBRATION_FREQ = 12.97535212
    NB_PEAKS = 6

    def __init__(self):
        self.parser = None
        self.args = None
        self.plotdata = None
        self.mapping = None
        self.sound_queue = None
        self.fig = None
        self.ax = None
        self.lines = None
        self.length = 0
        self._initialize()

    def _initialize(self):
        self.parser = argparse.ArgumentParser(add_help=False)
        self.parser.add_argument(
            '-l', '--list-devices', action='store_true',
            help='show list of audio devices and exit')
        self.args, remaining = self.parser.parse_known_args()
        if self.args.list_devices:
            print(sd.query_devices())
            self.parser.exit(0)
        self.parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            parents=[self.parser])
        self.parser.add_argument(
            'channels', type=int, default=[1], nargs='*', metavar='CHANNEL',
            help='input channels to plot (default: the first)')
        self.parser.add_argument(
            '-d', '--device', type=int_or_str,
            help='input device (numeric ID or substring)')
        self.parser.add_argument(
            '-w', '--window', type=float, default=200, metavar='DURATION',
            help='visible time slot (default: %(default)s ms)')
        self.parser.add_argument(
            '-i', '--interval', type=float, default=30,
            help='minimum time between plot updates (default: %(default)s ms)')
        self.parser.add_argument(
            '-b', '--blocksize', type=int, help='block size (in samples)')
        self.parser.add_argument(
            '-r', '--samplerate', type=float, help='sampling rate of audio device')
        self.parser.add_argument(
            '-n', '--downsample', type=int, default=1, metavar='N',
            help='display every Nth sample (default: %(default)s)')
        self.args = self.parser.parse_args(remaining)
        if any(c < 1 for c in self.args.channels):
            self.parser.error('argument CHANNEL: must be >= 1')
        self.mapping = [c - 1 for c in self.args.channels]  # Channel numbers start with 1
        self.sound_queue = queue.Queue()

    def audio_callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        # Fancy indexing with mapping creates a (necessary!) copy:
        self.sound_queue.put(indata[::self.args.downsample, self.mapping])

    def update_plotting_canvas(self, frame):
        """This is called by matplotlib for each plot update.

        Typically, audio callbacks happen more frequently than plot updates,
        therefore the queue tends to contain multiple blocks of audio data.

        """

        while True:
            try:
                recording = self.sound_queue.get_nowait()
            except queue.Empty:
                break
            N = recording.shape[0]
            L = N / self.args.samplerate
            # generate the Tukey window, widely open, alpha=0.01
            # https://www.mathworks.com/help/signal/ref/tukeywin.html
            tukey_window = signal.windows.tukey(N, 0.01, True)
            ysc = recording[:, 0] * tukey_window  # applying the Tukey window
            yk = np.fft.rfft(ysc)  # real to complex DFT
            k = np.arange(yk.shape[0])
            A = np.abs(yk).max
            freqs = k / L + CaptureSoundFFT.CALIBRATION_FREQ

            self.ax.clear()
            self.ax.set_ylim(-5, CaptureSoundFFT.MAX_AMPLITUDE)
            plt.xscale('log')
            plt.grid()

            np_abs = np.abs(yk)
            self.ax.plot(freqs, np_abs)
            lowest = np.sort(np_abs)
            peaks = lowest[-CaptureSoundFFT.NB_PEAKS:]
            for (f, a) in zip(freqs, np_abs):
                if f > CaptureSoundFFT.MIN_FREQ and a > CaptureSoundFFT.SOUND_LEVEL_MIN and a in peaks:
                    try:
                        note = Note.get_note_name(f, precision=0.01)
                        plt.text(f, a + 5, f"{note[0]}{note[1]}")
                    except ValueError:
                        try:
                            note = Note.get_note_name(f, precision=0.5)
                            plt.text(f, a + 5, f"~{note[0]}{note[1]}")
                        except ValueError as ve:
                            print(f"{f} Hz - {a} {str(ve)}")
        a_freq = 55/2.0
        for octave in range(1, 9):
            plt.axvline(x=a_freq * 2**octave, color='red', label=f"A{octave}", linestyle=":", lw=0.5)
        return []

    def init_plotting_canvas(self):
        self.ax.set_xlabel('Frequency in Hertz [Hz]')
        f = np.arange(CaptureSoundFFT.MAX_AMPLITUDE, 20000)
        self.ax.set_ylabel('Frequency Domain (Spectrum) Magnitude')
        self.ax.set_xlim(0.0, self.args.samplerate / 2.0)
        self.ax.set_ylim(-5, CaptureSoundFFT.MAX_AMPLITUDE)
        self.fig.tight_layout(pad=0)

    def capture(self):
        try:
            if self.args.samplerate is None:
                device_info = sd.query_devices(self.args.device, 'input')
                self.args.samplerate = device_info['default_samplerate']
            self.length = int(self.args.window * self.args.samplerate / (1000 * self.args.downsample))
            self.plotdata = np.zeros((self.length, len(self.args.channels)))
            self.fig, self.ax = plt.subplots()
            self.lines = self.ax.plot(self.plotdata)
            self.init_plotting_canvas()
            stream = sd.InputStream(
                device=self.args.device, channels=max(self.args.channels),
                samplerate=self.args.samplerate, callback=self.audio_callback, dtype='float32')
            ani = FuncAnimation(self.fig, self.update_plotting_canvas,
                                interval=self.args.interval, blit=True, repeat=False)
            with stream:
                plt.show()
        except Exception as e:
            self.parser.exit(type(e).__name__ + ': ' + str(e))


if __name__ == "__main__":
    c = CaptureSoundFFT()
    c.capture()
