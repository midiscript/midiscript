import pytest
from midiscript.lexer import Lexer, TokenType
from midiscript.parser import Parser, Note, Chord, Rest, Program
from midiscript.midi_generator import MIDIGenerator


def test_time_signature_lexer():
    source = "time 4/4"
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    # Filter out newlines and EOF
    token_types = [
        t.type for t in tokens if t.type not in (TokenType.NEWLINE, TokenType.EOF)
    ]
    token_values = [
        t.value for t in tokens if t.type not in (TokenType.NEWLINE, TokenType.EOF)
    ]

    assert token_types == [
        TokenType.TIME,
        TokenType.NUMBER,
        TokenType.SLASH,
        TokenType.NUMBER,
    ]
    assert token_values == ["time", "4", "/", "4"]


def test_lexer():
    source = """
    tempo 120
    time 4/4
    
    sequence main {
        C4 1/4
        [C4 E4 G4] 1/2
        R 1/4
    }
    
    play main
    """

    lexer = Lexer(source)
    tokens = lexer.tokenize()

    # Check if basic tokens are recognized
    token_types = [t.type for t in tokens if t.type != TokenType.NEWLINE]
    expected_types = [
        TokenType.TEMPO,
        TokenType.NUMBER,
        TokenType.TIME,
        TokenType.NUMBER,
        TokenType.SLASH,
        TokenType.NUMBER,
        TokenType.SEQUENCE,
        TokenType.IDENTIFIER,
        TokenType.LBRACE,
        TokenType.NOTE,
        TokenType.DURATION,
        TokenType.LBRACKET,
        TokenType.NOTE,
        TokenType.NOTE,
        TokenType.NOTE,
        TokenType.RBRACKET,
        TokenType.DURATION,
        TokenType.REST,
        TokenType.DURATION,
        TokenType.RBRACE,
        TokenType.PLAY,
        TokenType.IDENTIFIER,
        TokenType.EOF,
    ]

    assert token_types == expected_types


def test_parser():
    source = """
    tempo 120
    time 4/4
    
    sequence main {
        C4 1/4
        [C4 E4 G4] 1/2
        R 1/4
    }
    
    play main
    """

    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    program = parser.parse()

    assert program.tempo.value == 120
    assert program.time_signature.numerator == 4
    assert program.time_signature.denominator == 4
    assert len(program.sequences) == 1
    assert program.main_sequence == "main"

    main_sequence = program.sequences[0]
    assert len(main_sequence.events) == 3

    assert isinstance(main_sequence.events[0], Note)
    assert main_sequence.events[0].name == "C4"
    assert main_sequence.events[0].duration == "1/4"

    assert isinstance(main_sequence.events[1], Chord)
    assert main_sequence.events[1].notes == ["C4", "E4", "G4"]
    assert main_sequence.events[1].duration == "1/2"

    assert isinstance(main_sequence.events[2], Rest)
    assert main_sequence.events[2].duration == "1/4"


def test_midi_generator():
    source = """
    tempo 120
    time 4/4
    
    sequence main {
        C4 1/4
        [C4 E4 G4] 1/2
        R 1/4
    }
    
    play main
    """

    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    program = parser.parse()

    generator = MIDIGenerator()
    midi_data = generator.generate(program)

    # Check if MIDI data was generated
    assert isinstance(midi_data, bytes)
    assert len(midi_data) > 0


if __name__ == "__main__":
    pytest.main([__file__])
