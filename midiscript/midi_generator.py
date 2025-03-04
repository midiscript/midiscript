from typing import Dict, Set
from midiutil import MIDIFile  # type: ignore
from fractions import Fraction
from .parser import (
    Program,
    Note,
    Chord,
    Rest,
    Sequence,
    SequenceRef,
    TempoChange,
    TimeSignature,
)


class MIDIGenerator:
    NOTE_MAP = {
        "C": 60,
        "C#": 61,
        "Db": 61,
        "D": 62,
        "D#": 63,
        "Eb": 63,
        "E": 64,
        "F": 65,
        "F#": 66,
        "Gb": 66,
        "G": 67,
        "G#": 68,
        "Ab": 68,
        "A": 69,
        "A#": 70,
        "Bb": 70,
        "B": 71,
    }

    def __init__(self):
        self.midi = MIDIFile(1)  # One track
        self.time = 0.0  # Current time in beats
        self.current_tempo = 120
        self.ppq = 480  # Pulses per quarter note
        self.current_velocity = 100
        self.sequences: Dict[str, Sequence] = {}
        self.sequence_stack: Set[str] = set()

    def set_tempo(self, tempo: int):
        self.current_tempo = tempo
        self.midi.addTempo(0, self.time, tempo)

    def set_time_signature(self, numerator: int, denominator: int):
        self.midi.addTimeSignature(0, self.time, numerator, denominator, 24, 8)

    def note_to_midi_number(self, note_name: str) -> int:
        # Split note into name and octave (e.g., 'C4' -> 'C', 4)
        if len(note_name) == 2:
            name, octave = note_name[0], int(note_name[1])
        else:
            name, octave = note_name[:2], int(note_name[2])

        # Get base MIDI number for note name
        base = self.NOTE_MAP[name]

        # Adjust for octave (middle C is C4)
        return base + (octave - 4) * 12

    def duration_to_beats(self, duration: str) -> float:
        # Convert duration string (e.g., '1/4') to float
        if "/" in duration:
            num, denom = map(int, duration.split("/"))
            return float(Fraction(num, denom))
        return float(duration)

    def add_note(self, note: Note):
        midi_number = self.note_to_midi_number(note.name)
        duration = self.duration_to_beats(note.duration)
        velocity = note.velocity or self.current_velocity

        self.midi.addNote(
            0,  # track
            0,  # channel
            midi_number,
            self.time,
            duration,
            velocity
        )
        self.time += duration

    def add_chord(self, chord: Chord):
        duration = self.duration_to_beats(chord.duration)
        velocity = chord.velocity or self.current_velocity

        for note_name in chord.notes:
            midi_number = self.note_to_midi_number(note_name)
            self.midi.addNote(0, 0, midi_number, self.time, duration, velocity)

        self.time += duration

    def add_rest(self, rest: Rest):
        duration = self.duration_to_beats(rest.duration)
        self.time += duration

    def generate_sequence(self, sequence: Sequence):
        if sequence.name in self.sequence_stack:
            raise ValueError(
                f"Circular reference detected in sequence '{sequence.name}'"
            )

        self.sequence_stack.add(sequence.name)

        try:
            for event in sequence.events:
                if isinstance(event, Note):
                    self.add_note(event)
                elif isinstance(event, Chord):
                    self.add_chord(event)
                elif isinstance(event, Rest):
                    self.add_rest(event)
                elif isinstance(event, SequenceRef):
                    referenced_seq = self.sequences.get(event.name)
                    if referenced_seq:
                        self.generate_sequence(referenced_seq)
                    else:
                        raise ValueError(
                            f"Referenced sequence '{event.name}' not found"
                        )
        finally:
            self.sequence_stack.remove(sequence.name)

    def generate(self, program: Program) -> bytes:
        # Reset state
        self.time = 0.0
        self.midi = MIDIFile(1)
        self.sequences = {seq.name: seq for seq in program.sequences}
        self.sequence_stack = set()

        # Set initial tempo and time signature
        if program.tempo:
            self.set_tempo(program.tempo.value)
        else:
            self.set_tempo(120)  # Default tempo

        if program.time_signature:
            self.set_time_signature(
                program.time_signature.numerator,
                program.time_signature.denominator
            )
        else:
            self.set_time_signature(4, 4)  # Default 4/4 time

        # Find main sequence
        if program.main_sequence:
            main_seq = self.sequences.get(program.main_sequence)
            if main_seq:
                self.generate_sequence(main_seq)
            else:
                raise ValueError(
                    f"Sequence '{program.main_sequence}' not found"
                )
        elif program.sequences:
            # If no main sequence specified, use the first one
            self.generate_sequence(program.sequences[0])

        # Convert to bytes
        with open("temp.mid", "wb") as f:
            self.midi.writeFile(f)
        with open("temp.mid", "rb") as f:
            return f.read()
