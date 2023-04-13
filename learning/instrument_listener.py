from pyharmonytools.harmony.note import Note


class InstrumentListener:
    def __init__(self):
        pass

    def instrument_updated(self, lowest_note: Note, highest_note: Note):
        pass

    def played_note(self, note: Note):
        pass
