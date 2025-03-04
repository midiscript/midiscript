from dataclasses import dataclass
from typing import List, Optional, Union
from .lexer import Token, TokenType


@dataclass
class Note:
    name: str  # e.g., 'C4', 'D#3'
    duration: str  # e.g., '1/4', '1/8'
    velocity: Optional[int] = None


@dataclass
class Chord:
    notes: List[str]  # List of note names
    duration: str
    velocity: Optional[int] = None


@dataclass
class Rest:
    duration: str


@dataclass
class SequenceRef:
    name: str


@dataclass
class Sequence:
    name: str
    events: List[Union[Note, Chord, Rest, SequenceRef]]


@dataclass
class TempoChange:
    value: int


@dataclass
class TimeSignature:
    numerator: int
    denominator: int


@dataclass
class Program:
    tempo: Optional[TempoChange] = None
    time_signature: Optional[TimeSignature] = None
    sequences: List[Sequence] = None
    main_sequence: Optional[str] = None


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.current_token = tokens[0] if tokens else None

    def error(self, message: str = "Invalid syntax"):
        token = self.current_token
        raise Exception(
            f"{message} at line {token.line}, column {token.column}"
        )

    def advance(self):
        self.current += 1
        if self.current < len(self.tokens):
            self.current_token = self.tokens[self.current]
        else:
            self.current_token = None

    def peek(self) -> Optional[Token]:
        if self.current + 1 < len(self.tokens):
            return self.tokens[self.current + 1]
        return None

    def skip_newlines(self):
        while (self.current_token and 
               self.current_token.type == TokenType.NEWLINE):
            self.advance()

    def match(self, type_: TokenType) -> bool:
        if self.current_token and self.current_token.type == type_:
            self.advance()
            return True
        return False

    def expect(self, type_: TokenType) -> Token:
        self.skip_newlines()
        if self.current_token and self.current_token.type == type_:
            token = self.current_token
            self.advance()
            return token
        self.error(f"Expected {type_}, got {self.current_token.type}")

    def parse_note(self) -> Note:
        note_token = self.expect(TokenType.NOTE)
        duration_token = self.expect(TokenType.DURATION)
        return Note(note_token.value, duration_token.value)

    def parse_chord(self) -> Chord:
        self.expect(TokenType.LBRACKET)
        notes = []
        
        while self.current_token and self.current_token.type == TokenType.NOTE:
            notes.append(self.current_token.value)
            self.advance()
            self.skip_newlines()
            
        self.expect(TokenType.RBRACKET)
        duration_token = self.expect(TokenType.DURATION)
        return Chord(notes, duration_token.value)

    def parse_rest(self) -> Rest:
        self.expect(TokenType.REST)
        duration_token = self.expect(TokenType.DURATION)
        return Rest(duration_token.value)

    def parse_sequence_ref(self) -> SequenceRef:
        token = self.expect(TokenType.IDENTIFIER)
        return SequenceRef(token.value)

    def parse_sequence(self) -> Sequence:
        self.expect(TokenType.SEQUENCE)
        name_token = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.LBRACE)
        
        events = []
        while (self.current_token and 
               self.current_token.type in 
               (TokenType.NOTE, TokenType.LBRACKET, TokenType.REST, 
                TokenType.IDENTIFIER, TokenType.NEWLINE)):
            
            if self.current_token.type == TokenType.NEWLINE:
                self.advance()
                continue
                
            if self.current_token.type == TokenType.NOTE:
                events.append(self.parse_note())
            elif self.current_token.type == TokenType.LBRACKET:
                events.append(self.parse_chord())
            elif self.current_token.type == TokenType.REST:
                events.append(self.parse_rest())
            elif self.current_token.type == TokenType.IDENTIFIER:
                events.append(self.parse_sequence_ref())
                
        self.expect(TokenType.RBRACE)
        return Sequence(name_token.value, events)

    def parse_tempo(self) -> TempoChange:
        self.expect(TokenType.TEMPO)
        value_token = self.expect(TokenType.NUMBER)
        return TempoChange(int(value_token.value))

    def parse_time_signature(self) -> TimeSignature:
        self.expect(TokenType.TIME)
        numerator_token = self.expect(TokenType.NUMBER)
        self.expect(TokenType.SLASH)
        denominator_token = self.expect(TokenType.NUMBER)
        return TimeSignature(
            int(numerator_token.value),
            int(denominator_token.value)
        )

    def parse(self) -> Program:
        program = Program(sequences=[])
        
        while self.current_token and self.current_token.type != TokenType.EOF:
            if self.current_token.type == TokenType.NEWLINE:
                self.advance()
                continue
                
            if self.current_token.type == TokenType.TEMPO:
                program.tempo = self.parse_tempo()
            elif self.current_token.type == TokenType.TIME:
                program.time_signature = self.parse_time_signature()
            elif self.current_token.type == TokenType.SEQUENCE:
                program.sequences.append(self.parse_sequence())
            elif self.current_token.type == TokenType.PLAY:
                self.advance()
                sequence_token = self.expect(TokenType.IDENTIFIER)
                program.main_sequence = sequence_token.value
            else:
                self.error()
                
        return program 