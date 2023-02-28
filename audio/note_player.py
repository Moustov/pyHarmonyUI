# https://towardsdatascience.com/mathematics-of-music-in-python-b7d838c84f72
# see also https://github.com/MaelDrapier/musicalbeeps#from-a-python-program

import numpy as np
from pyharmonytools.harmony.note import Note


class NotePlayer:
    samplerate = 44100  # Frequecy in Hz

    def __init__(self):
        self.waves = {}
        for n in Note.CHROMATIC_SCALE_SHARP_BASED:
            self.waves[n] = {}
            for octave in range(0,10):
                self.waves[n][octave] = self.get_wave_from_note(n, octave)

    def _get_wave(self, freq, duration=0.5):
        '''
        Function takes the "frequency" and "time_duration" for a wave
        as the input and returns a "numpy array" of values at all points
        in time
        '''
        amplitude = 4096
        t = np.linspace(0, duration, int(self.samplerate * duration))
        wave = amplitude * np.sin(2 * np.pi * freq * t)
        return wave

    def get_wave_from_note(self, note: str, octave: int):
        """

        :param note: A Ab A#...
        :param octave:
        :return:
        """
        raw_note_name = note
        if "b" in note:
            raw_note_name = Note.CHROMATIC_SCALE_SHARP_BASED[Note.CHROMATIC_SCALE_FLAT_BASED.index(note)]
        freq = Note.notes[raw_note_name][octave]
        return self._get_wave(freq, 5)


