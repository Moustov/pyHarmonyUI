from unittest import TestCase

from audio.voice_training import VoiceTraining


class TestNoteTraining(TestCase):
    def test_time_string(self):
        nt = VoiceTraining()
        res = nt.time_string(1)
        self.assertTrue(res == "00:00:00.001")
        res = nt.time_string(10)
        self.assertTrue(res == "00:00:00.010")
        res = nt.time_string(1000)
        self.assertTrue(res == "00:00:01.000")
        res = nt.time_string(60*1000)
        self.assertTrue(res == "00:01:00.000")
        res = nt.time_string(5*60*1000)
        self.assertTrue(res == "00:05:00.000")
        res = nt.time_string(60*60*1000)
        self.assertTrue(res == "01:00:00.000")
        res = nt.time_string(60*60*1000 + 2000)
        self.assertTrue(res == "01:00:02.000")
