# https://towardsdatascience.com/mathematics-of-music-in-python-b7d838c84f72
# see also https://github.com/MaelDrapier/musicalbeeps#from-a-python-program

import time

import numpy as np
import pygame
from pyharmonytools.harmony.note import Note


class NotePlayer:
    debug = False
    samplerate = 44100  # Frequency in Hz
    waves = {}
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
                    NotePlayer.waves[note][octave]["signal"] = self.generate_wave_from_note(note, octave)
                    sound_id = pygame.mixer.Sound(self.waves[note][octave]["signal"])
                    NotePlayer.waves[note][octave]["pygame_sound_id"] = sound_id

    def _get_wave(self, freq: float, duration: float = 0.5) -> []:
        '''
        Function takes the "frequency" and "time_duration" for a wave
        as the input and returns a "numpy array" of values at all points
        in time
        '''
        # factor to adjust frequency / todo: address this magic number to make things clearer
        MAGIC_NUMBER = 4.3536363636363636363636363636364
        amplitude = 4096
        t = np.linspace(0, duration, int(NotePlayer.samplerate * duration))
        wave = amplitude * np.sin(2 * np.pi * freq * t / MAGIC_NUMBER)
        return wave.astype(np.int16)

    def generate_wave_from_note(self, note: str, octave: int) -> []:
        """

        :param note: A Ab A#...
        :param octave:
        :return:
        """
        raw_note_name = note
        if "b" in note:
            raw_note_name = Note.CHROMATIC_SCALE_SHARP_BASED[Note.CHROMATIC_SCALE_FLAT_BASED.index(note)]
        freq = Note.notes[raw_note_name][octave]
        if self.debug:
            print(f"Generating wav from {note}{octave} - {freq}Hz")
        return self._get_wave(freq, 5)

    def play_note(self, note: str, octave: int):
        """
        plays a sound generated from the note name & octave
        :param note:
        :param octave:
        :return:
        """
        if NotePlayer.debug:
            print("play_note:", note, octave)
        pygame.mixer.Sound.play(NotePlayer.waves[note][octave]["pygame_sound_id"], maxtime=1000, fade_ms=400)

    def test_sound(self):
        for f in range(50, 20000, 100):
            sound = self._get_wave(f, 1)
            sound_id = pygame.mixer.Sound(sound)
            print(f, "Hz")
            pygame.mixer.Sound.play(sound_id, maxtime=1000, fade_ms=400)
            time.sleep(1)


if __name__ == "__main__":
    npl = NotePlayer()
    npl.test_sound()
