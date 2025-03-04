import pytest
from midiscript.lexer import Lexer, TokenType
from midiscript.parser import Parser, Note
from midiscript.midi_generator import MIDIGenerator


def test_time_signature_lexer():
    lexer = Lexer("4/4")
    tokens = lexer.tokenize()
    assert len(tokens) == 4
    assert tokens[0].type == TokenType.NUMBER
    assert tokens[1].type == TokenType.SLASH
    assert tokens[2].type == TokenType.NUMBER
    assert tokens[3].type == TokenType.EOF


def test_lexer():
    lexer = Lexer("sequence main { C4 1/4 }")
    tokens = lexer.tokenize()
    assert len(tokens) == 9
    assert tokens[0].type == TokenType.SEQUENCE
    assert tokens[1].type == TokenType.IDENTIFIER
    assert tokens[2].type == TokenType.LBRACE
    assert tokens[3].type == TokenType.NOTE
    assert tokens[4].type == TokenType.NUMBER
    assert tokens[5].type == TokenType.SLASH
    assert tokens[6].type == TokenType.NUMBER
    assert tokens[7].type == TokenType.RBRACE
    assert tokens[8].type == TokenType.EOF


def test_parser():
    lexer = Lexer("sequence main { C4 1/4 }")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    program = parser.parse()
    assert len(program.sequences) == 1
    main_sequence = program.sequences["main"]
    first_event = main_sequence.events[0]
    assert isinstance(first_event, Note)
    assert first_event.name == "C4"
    assert first_event.duration == "1/4"


def test_midi_generator():
    lexer = Lexer("sequence main { C4 1/4 }")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    program = parser.parse()
    generator = MIDIGenerator()
    midi_data = generator.generate(program)
    assert len(midi_data) > 0


if __name__ == "__main__":
    pytest.main([__file__])
