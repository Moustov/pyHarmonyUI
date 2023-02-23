#!/usr/bin/env python3
"""Plot the live microphone signal(s) with matplotlib.

Matplotlib and NumPy have to be installed.
https://matplotlib.org/stable/api/animation_api.html

See also https://www.chciken.com/digital/signal/processing/2020/05/13/guitar-tuner.html
"""
import argparse
import queue
import sys
import time

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

        frequencies for calibration
        Tests with internal microphone
            100Hz       https://www.youtube.com/watch?v=Cdi0jQtMqV8     KO 130.81Hz found (noisy)
        C3  130.81Hz    https://www.youtube.com/watch?v=f6GsdpWEHPk     ~OK noisy
        C#3 138.59Hz    https://www.youtube.com/watch?v=AjTCPI6-60M     KO 164.81Hz found (noisy)
        D3  146.83Hz    https://www.youtube.com/watch?v=r9Otq6yaxVY     KO 164.81Hz found (noisy)
        D#3 155.56Hz    https://www.youtube.com/watch?v=-MxqFlfCK6U     KO 164.81Hz found (noisy)
        E3  164.81Hz    https://www.youtube.com/watch?v=KzWdpvrdI38     ~OK noisy
        F3  174.61Hz    https://www.youtube.com/watch?v=Qw7xEGAjurg     KO 164-207Hz found (noisy)
        F#3 185Hz       https://www.youtube.com/watch?v=MzGav1jUrMI     KO 207.65Hz found
        G3  196Hz       https://www.youtube.com/watch?v=C7vHtc1UCeE     KO 207.65Hz found
        G#3 207.65Hz    https://www.youtube.com/watch?v=napNiGlpRf0     ~OK noisy
        A3  220Hz       https://www.youtube.com/watch?v=0XvVS-aoNmc     KO 246.94Hz found
        A#3 233.08Hz    https://www.youtube.com/watch?v=q_7I6OqMoNc     KO 246.94Hz found
        B3  246.94Hz    https://www.youtube.com/watch?v=a3SITuEhL9g     ~OK noisy
        C4  261.63Hz    https://www.youtube.com/watch?v=CKi78RF7vck     KO 277.18Hz found
        A4  440Hz       https://www.youtube.com/watch?v=0LxtrLizkrU     OK
        A#4 466.16Hz    https://www.youtube.com/watch?v=WG6Kx1-_qGU     OK
        B4  493.88Hz    https://www.youtube.com/watch?v=YnVJ5PptX-o     KO 523.25Hz found
        C4  523.25Hz    https://www.youtube.com/watch?v=Nutnvo5JmoQ     ~OK noisy
        C#5 554.37Hz    https://www.youtube.com/watch?v=Iqfejgwfx4w     OK
        D5  587.33Hz    https://www.youtube.com/watch?v=-0Pb3mu9e2c     OK
        D#5 622.25Hz    https://www.youtube.com/watch?v=0z-Ej6KNYFY     OK
        E5  659.26Hz    https://www.youtube.com/watch?v=wLdu48B9LqQ     OK
        F5  698.46Hz    https://www.youtube.com/watch?v=tXOS4lqS3yw     OK
        F#5 739.99Hz    https://www.youtube.com/watch?v=Xf_ex3jEeW8     OK
        G5  783.99Hz    https://www.youtube.com/watch?v=yqw7aKG6eIc     OK
        G#5 830.61Hz    https://www.youtube.com/watch?v=jI7ZludT5I8     OK
            1500Hz      https://www.youtube.com/watch?v=1iE_Kf3i6Ok     KO 1567.98Hz found (noisy)
            2500Hz      https://www.youtube.com/watch?v=zrYLB0K5sgo     KO 2489.02Hz found
            5000Hz      https://www.youtube.com/watch?v=cx1VQISKvhc     KO 4978.03Hz found (noisy)
            10000Hz     https://www.youtube.com/watch?v=y412fwrht3E     KO 9956.06Hz found (noisy)

        todo see a more accurate tuner here https://www.chciken.com/digital/signal/processing/2020/05/13/guitar-tuner.html
        this proves the internal mic is good enough => there is *maybe* a problem infered by
        - the Tukey windowing which is too wide ? (N = kTB)
        - the sampling rate (eventually infered by the display) ?
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
                    note = Note.find_closest_note(f)
                    plt.text(f, a + 5, f"{note[0]}")
                    plt.text(f, a - 5, f"{round(note[1],2)}")
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
            self.length = int(self.args.window * self.args.samplerate // (1000 * self.args.downsample))
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
