import tkinter
from datetime import datetime
from functools import partial
from tkinter import Button, Frame, Radiobutton, LabelFrame
from tkinter.ttk import Progressbar

from pyharmonytools.harmony.note import Note

from audio.mic_analyzer import MicAnalyzer, MicListener
from audio.note_player import NotePlayer
from learning.learning_center_interfaces import LearningCenterInterface
from learning.pilotable_instrument import PilotableInstrument


class VoiceTraining(MicListener, PilotableInstrument):
    NOTE_MUTE = "#AAAAAA"
    NOTE_HEARD = "#AA8888"
    NOTE_SHOW = "#EEEEEE"
    NOTE_DISABLED = "#222222"

    def __init__(self):
        self.calibration_labelframe = None
        self.calibration_radio = None
        self.castrato_radio = None
        self.progress_bar_labelframe = None
        self.notes_labelframe = None
        self.soprano_radio = None
        self.mezzo_soprano_radio = None
        self.contralto_radio = None
        self.tenor_radio = None
        self.baritone_radio = None
        self.bass_radio = None
        self.vocal_range = tkinter.StringVar()
        self.vocal_ranges_labelframe = None
        self.calibrating_highest_note = None
        self.calibrating_lowest_note = None
        self.nb_samples = 20
        self.calibrate_highest_button = None
        self.calibrate_button = None
        self.highest_note = None
        self.lowest_note = None
        self.debug = False
        self.learning_center = None
        #
        self.mic_analyzer = MicAnalyzer()
        self.mic_analyzer.add_listener(self)
        # UI data
        self.progress_bar = None
        self.ui_root_tk = None
        self.notes_buttons = {}
        self.learning_thread = None
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
        self.learn_button = None
        self.note_player = NotePlayer()

    def get_lowest_note(self) -> Note:
        if not self.lowest_note:
            return Note("C0")
        return self.lowest_note

    def get_highest_note(self) -> Note:
        if not self.highest_note:
            return Note("B9")
        return self.highest_note

    def display(self, ui_root_tk: Frame):
        self.ui_root_tk = ui_root_tk

        self.vocal_ranges_labelframe = LabelFrame(self.ui_root_tk, text='Vocal ranges')
        self.vocal_ranges_labelframe.grid(row=0, column=0, rowspan=2)

        self.calibration_labelframe = LabelFrame(self.vocal_ranges_labelframe, text='Calibration')
        self.calibration_labelframe.grid(row=0, column=0)
        self.calibrate_button = Button(self.calibration_labelframe, text=f"Voice\nCalibration",
                                       width=10, command=self._do_calibrate_with_voice)
        self.calibrate_button.grid(row=1, column=0)
        self.calibration_radio = Radiobutton(self.calibration_labelframe, text="Calibration",
                                             variable=self.vocal_range,
                                             value="Calibration", command=self._do_change_vocal_range)
        self.calibration_radio.grid(row=1, column=1)

        # classical voice ranges https://en.wikipedia.org/wiki/Vocal_range
        self.bass_radio = Radiobutton(self.vocal_ranges_labelframe, text="Bass (E2->E4)",
                                      variable=self.vocal_range,
                                      value="Bass", command=self._do_change_vocal_range)
        self.bass_radio.grid(row=1, column=0)
        self.baritone_radio = Radiobutton(self.vocal_ranges_labelframe, text="Baritone (G2->F4)",
                                          variable=self.vocal_range,
                                          value="Baritone", command=self._do_change_vocal_range)
        self.baritone_radio.grid(row=1, column=1)
        self.tenor_radio = Radiobutton(self.vocal_ranges_labelframe, text="Tenor (B2->A4)",
                                       variable=self.vocal_range,
                                       value="Tenor", command=self._do_change_vocal_range)
        self.tenor_radio.grid(row=1, column=2)
        self.contralto_radio = Radiobutton(self.vocal_ranges_labelframe, text="Contralto (F3->E5)",
                                           variable=self.vocal_range,
                                           value="Contralto", command=self._do_change_vocal_range)
        self.contralto_radio.grid(row=2, column=0)
        self.mezzo_soprano_radio = Radiobutton(self.vocal_ranges_labelframe, text="Mezzo-soprano (A3->A5)",
                                               variable=self.vocal_range,
                                               value="Mezzo-soprano", command=self._do_change_vocal_range)
        self.mezzo_soprano_radio.grid(row=2, column=1)
        self.soprano_radio = Radiobutton(self.vocal_ranges_labelframe, text="Soprano (C4->C6)",
                                         variable=self.vocal_range,
                                         value="Soprano", command=self._do_change_vocal_range)
        self.soprano_radio.grid(row=2, column=2)
        # https://startsingingtoday.com/castrato-singers-today/
        self.castrato_radio = Radiobutton(self.vocal_ranges_labelframe, text="Castrato (A3->D6)",
                                          variable=self.vocal_range,
                                          value="Castrato", command=self._do_change_vocal_range)
        self.castrato_radio.grid(row=3, column=0)
        self.vocal_range.set('Vocal ranges')

        self.progress_bar_labelframe = LabelFrame(self.ui_root_tk, text='Microphone')
        self.progress_bar_labelframe.grid(row=2, column=0)
        self.progress_bar = Progressbar(self.progress_bar_labelframe, orient='horizontal', mode='indeterminate',
                                        length=280)
        self.progress_bar.grid(row=1, column=0, columnspan=9)
        self.notes_labelframe = LabelFrame(self.ui_root_tk, text='Notes')
        self.notes_labelframe.grid(row=3, column=0)
        for octave in range(0, len(self.mic_analyzer.OCTAVE_BANDS)):
            self.notes_buttons[str(octave)] = {}
            half_tone = 0
            for note in Note.CHROMATIC_SCALE_SHARP_BASED:
                half_tone += 1
                self.notes_buttons[str(octave)][note] = Button(self.notes_labelframe,
                                                               text=f"{note}{octave}",
                                                               bg=VoiceTraining.NOTE_MUTE,
                                                               width=10,
                                                               command=partial(self.do_play_note, note, octave))
                self.notes_buttons[str(octave)][note].grid(row=1 + half_tone, column=octave, padx=5)

    def _do_change_vocal_range(self):
        selected_range = self.vocal_range.get()
        if selected_range == "Bass":
            self.lowest_note = Note("E2")
            self.highest_note = Note("E4")
        elif selected_range == "Baritone":
            self.lowest_note = Note("G2")
            self.highest_note = Note("F4")
        elif selected_range == "Tenor":
            self.lowest_note = Note("F3")
            self.highest_note = Note("E5")
        elif selected_range == "Contralto":
            self.lowest_note = Note("F3")
            self.highest_note = Note("E5")
        elif selected_range == "Mezzo-soprano":
            self.lowest_note = Note("A3")
            self.highest_note = Note("A5")
        elif selected_range == "Soprano":
            self.lowest_note = Note("C4")
            self.highest_note = Note("C6")
        elif selected_range == "Castrato":
            self.lowest_note = Note("A3")
            self.highest_note = Note("D6")
        else:
            self.lowest_note = Note("C0")
            self.highest_note = Note("B9")
        self.set_lowest_note(self.lowest_note)
        self.set_highest_note(self.highest_note)

    def _do_calibrate_with_voice(self):
        self.debug = True
        self.nb_samples = 20
        self.lowest_note = None
        self.highest_note = None
        self.calibrating_lowest_note = True
        self.calibrating_highest_note = True
        self.progress_bar.start()
        self.mic_analyzer.do_start_hearing()
        # self.calibrate_lowest_button.after(10, partial(self.__calibrating, get_lowest=True))

    def do_play_note(self, note, octave):
        if self.debug:
            print(note, octave)
        self.note_player.play_note(note, octave)

    def do_start_hearing(self, lc: LearningCenterInterface):
        self.learning_center = lc
        self.start_time = datetime.now()
        self.progress_bar.start()
        self.mic_analyzer.do_start_hearing()

    def do_stop_hearing(self):
        self.mic_analyzer.do_stop_hearing()
        self.progress_bar.stop()
        self.display_song()

    def show_note(self, note: str, color: str = NOTE_SHOW):
        if self.debug:
            print("show_note", note, color)
        self._change_note_aspects(note, color)

    def mask_note(self, note: str):
        if self.debug:
            print("show_note", note)
        self._change_note_aspects(note, VoiceTraining.NOTE_MUTE)

    def set_current_note(self, new_note: str, heard_freq: float = 0.0, closest_pitch: float = 0.0):
        """

        :param closest_pitch:
        :param heard_freq:
        :param new_note: eg "A#2" or "B3"
        :return:
        """
        if self.debug:
            print("_set_current_note", new_note)
        if new_note == "-" or len(new_note) in [2, 3]:
            if self.start_time:
                now = datetime.now()
                self.chrono = (now - self.start_time).microseconds
                self.add_note(new_note)
            self.previous_note = self.current_note
            self.unset_current_note()
            self.current_note = new_note
            if new_note == "-":
                self.unset_current_note()
            else:
                accuracy = 100 - 100 * abs((closest_pitch - heard_freq) / closest_pitch)
                self._change_note_aspects(new_note, VoiceTraining.NOTE_HEARD, accuracy)
                if self.debug:
                    print("_set_current_note - record", new_note)
        if self.learning_center:
            self.learning_center.check_note(new_note, heard_freq, closest_pitch)
        if self.calibrating_lowest_note:
            if self.debug:
                print("_set_current_note - calibrating_lowest_note", new_note)
            if self.current_note and 2 <= len(self.current_note) <= 3:
                if self.nb_samples > 0:
                    self.nb_samples -= 1
                else:
                    self.mic_analyzer.do_stop_hearing()
                    self.progress_bar.stop()
                    self.calibrating_lowest_note = None
                if self.lowest_note and (Note(self.current_note) < self.lowest_note):
                    self.set_lowest_note(Note(self.current_note))
                if not self.lowest_note:
                    self.set_lowest_note(Note(self.current_note))
        if self.calibrating_highest_note:
            if self.debug:
                print("_set_current_note - calibrating_highest_note", new_note)
            if self.current_note and 2 <= len(self.current_note) <= 3:
                if self.nb_samples > 0:
                    self.nb_samples -= 1
                else:
                    self.mic_analyzer.do_stop_hearing()
                    self.progress_bar.stop()
                    self.calibrating_highest_note = None
                if self.highest_note and (Note(self.current_note) > self.highest_note):
                    self.set_highest_note(Note(self.current_note))
                if not self.highest_note:
                    self.set_highest_note(Note(self.current_note))

    def set_lowest_note(self, lowest_note: Note):
        super().set_lowest_note(lowest_note)
        print("set_lowest_note", lowest_note)
        # disable lower notes
        for octave in range(0, len(self.mic_analyzer.OCTAVE_BANDS)):
            for note in Note.CHROMATIC_SCALE_SHARP_BASED:
                n = Note(f"{note}{octave}")
                if self.get_lowest_note() <= n <= self.get_highest_note():
                    self.notes_buttons[str(octave)][note].config(bg=VoiceTraining.NOTE_MUTE)
                else:
                    self.notes_buttons[str(octave)][note].config(bg=VoiceTraining.NOTE_DISABLED)

    def set_highest_note(self, highest_note: Note):
        super().set_highest_note(highest_note)
        print("set_highest_note", highest_note)
        # disable higher notes
        for octave in range(0, len(self.mic_analyzer.OCTAVE_BANDS)):
            for note in Note.CHROMATIC_SCALE_SHARP_BASED:
                n = Note(f"{note}{octave}")
                if self.get_lowest_note() <= n <= self.get_highest_note():
                    self.notes_buttons[str(octave)][note].config(bg=VoiceTraining.NOTE_MUTE)
                else:
                    self.notes_buttons[str(octave)][note].config(bg=VoiceTraining.NOTE_DISABLED)

    def unset_current_note(self):
        if self.debug:
            print("unset", self.current_note)
        if self.current_note and len(self.current_note) in [2, 3]:
            self._change_note_aspects(self.current_note, VoiceTraining.NOTE_MUTE)
            self.previous_note = self.current_note
            self.current_note = "-"

    def _change_note_aspects(self, note: str, bg: str, accuracy: float = -1):
        """

        :param accuracy: percentage of accuracy with perfect pitch
        :param note: eg "A#2" or "B3"
        :param bg:  eg "#112233"
        :return:
        """
        if self.debug:
            print("Changed Note:", note, bg, self.current_note)
        if note and len(note) in [2, 3]:  # and bg and len(bg) == 7:
            octave = note[-1]
            the_note = note[0:len(note) - 1]
            if accuracy == -1:
                btn_text = f"{the_note}{octave}"
                self.notes_buttons[str(octave)][the_note].configure(bg=bg, text=btn_text)
            else:
                btn_text = f"{the_note}{octave} ({round(accuracy, 2)}%)"
                self.notes_buttons[str(octave)][the_note].configure(bg=bg, text=btn_text)

    def add_note(self, new_note):
        if self.previous_note != new_note:
            now = datetime.now()
            self.chrono = (now - self.start_time)
            self.song.append((new_note, self.chrono))
            if self.debug:
                print("add_note", self.current_note, (new_note, self.chrono))

    def display_song(self):
        for note in self.song:
            print(note[1], ":", note[0])

    def clear_notes(self, with_calibration: bool = False):
        for octave in range(0, len(self.mic_analyzer.OCTAVE_BANDS)):
            for note in Note.CHROMATIC_SCALE_SHARP_BASED:
                if with_calibration:
                    n = Note(f"{note}{octave}")
                    if self.get_lowest_note() <= n <= self.get_highest_note():
                        self.notes_buttons[str(octave)][note].config(bg=VoiceTraining.NOTE_MUTE)
                    else:
                        self.notes_buttons[str(octave)][note].config(bg=VoiceTraining.NOTE_DISABLED)
                else:
                    self.notes_buttons[str(octave)][note].configure(bg=VoiceTraining.NOTE_MUTE, text=f"{note}{octave}")


if __name__ == "__main__":
    nt = VoiceTraining()
    root = tkinter.Tk()
    root.title('Harmony tools')
    root.geometry('800x600')
    nt.display(root)
    root.mainloop()
