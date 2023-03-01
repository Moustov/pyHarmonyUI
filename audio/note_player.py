# https://towardsdatascience.com/mathematics-of-music-in-python-b7d838c84f72
# see also https://github.com/MaelDrapier/musicalbeeps#from-a-python-program

import numpy as np
import pygame
from pyharmonytools.harmony.note import Note


class NotePlayer:
    samplerate = 44100  # Frequency in Hz
    waves = {}
    debug = False
    is_pygame_initialized = False

    def __init__(self):
        if not NotePlayer.is_pygame_initialized:
            pygame.init()
            NotePlayer.is_pygame_initialized = True

        if not NotePlayer.waves:
            for note in Note.CHROMATIC_SCALE_SHARP_BASED:
                NotePlayer.waves[note] = {}
                for octave in range(0, 10):
                    NotePlayer.waves[note][octave] = {}
                    NotePlayer.waves[note][octave]["signal"] = self.get_wave_from_note(note, octave)
                    sound_id = pygame.mixer.Sound(self.waves[note][octave]["signal"])
                    NotePlayer.waves[note][octave]["pygame_sound_id"] = sound_id
            print(self.waves)

    def _get_wave(self, freq, duration=0.5):
        '''
        Function takes the "frequency" and "time_duration" for a wave
        as the input and returns a "numpy array" of values at all points
        in time
        '''
        # factor to adjust frequency / todo: address this magic number to make things clearer
        MAGIC_NUMBER = 4.3536363636363636363636363636364
        amplitude = 4096
        t = np.linspace(0, duration, int(self.samplerate * duration))
        wave = amplitude * np.sin(2 * np.pi * freq * t / MAGIC_NUMBER)
        return wave.astype(np.int16)

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

    def play_note(self, note: str, octave: int):
        if NotePlayer.debug:
            print("play_note:", note, octave)
        pygame.mixer.Sound.play(NotePlayer.waves[note][octave]["pygame_sound_id"], maxtime=1000, fade_ms=400)
