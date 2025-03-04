from dataclasses import dataclass, field
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
    sequences: List[Sequence] = field(default_factory=list)
    main_sequence: Optional[str] = None

    def __post_init__(self):
        if self.sequences is None:
            self.sequences = []


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.sequences: List[Sequence] = []

    def error(self, message: str = "Invalid syntax") -> None:
        token = self.peek()
        if token is None:
            raise Exception(f"{message} at end of input")
        raise Exception(f"{message} at line {token.line}, column {token.column}")

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def peek(self) -> Optional[Token]:
        if self.current >= len(self.tokens):
            return None
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def is_at_end(self) -> bool:
        token = self.peek()
        if token is None:
            return True
        return token.type == TokenType.EOF

    def match(self, *types: TokenType) -> bool:
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def check(self, type: TokenType) -> bool:
        token = self.peek()
        if token is None:
            return False
        return token.type == type

    def skip_newlines(self) -> None:
        token = self.peek()
        while token is not None and token.type == TokenType.NEWLINE:
            self.advance()
            token = self.peek()

    def parse(self) -> List[Sequence]:
        try:
            while not self.is_at_end():
                if self.match(TokenType.SEQUENCE):
                    self.sequence_declaration()
                else:
                    self.advance()
            return self.sequences
        except Exception as e:
            # Log the error and return empty list
            print(f"Error parsing: {str(e)}")
            return []

    def sequence_declaration(self) -> None:
        name = self.consume(TokenType.IDENTIFIER, "Expected sequence name.")
        self.consume(TokenType.LBRACE, "Expected '{' after sequence name.")

        events: List[Union[Note, Chord, Rest, SequenceRef]] = []

        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            if self.match(TokenType.NOTE):
                events.append(self.note())
            elif self.match(TokenType.LBRACKET):
                events.append(self.chord())
            elif self.match(TokenType.REST):
                events.append(self.rest())
            elif self.match(TokenType.IDENTIFIER):
                events.append(self.sequence_ref())
            else:
                token = self.peek()
                if token is not None:
                    raise SyntaxError(
                        "Unexpected token at line "
                        f"{token.line}, column {token.column}"
                    )
                else:
                    raise SyntaxError("Unexpected end of input")

        self.consume(TokenType.RBRACE, "Expected '}' after sequence events.")
        self.sequences.append(Sequence(name.lexeme, events))

    def note(self) -> Note:
        duration = self.consume(TokenType.DURATION, "Expected duration after note.")
        return Note(
            self.previous().lexeme,
            duration.lexeme,
        )

    def chord(self) -> Chord:
        notes: List[str] = []
        while not self.check(TokenType.RBRACKET) and not self.is_at_end():
            if self.match(TokenType.NOTE):
                notes.append(self.previous().lexeme)
            else:
                token = self.peek()
                if token is not None:
                    raise SyntaxError(
                        f"Expected note in chord at line {token.line}, "
                        f"column {token.column}"
                    )
                else:
                    raise SyntaxError("Unexpected end of input in chord")

        self.consume(TokenType.RBRACKET, "Expected ']' after chord notes.")
        duration = self.consume(TokenType.DURATION, "Expected duration after chord.")
        return Chord(notes, duration.lexeme)

    def rest(self) -> Rest:
        duration = self.consume(TokenType.DURATION, "Expected duration after rest.")
        return Rest(duration.lexeme)

    def sequence_ref(self) -> SequenceRef:
        return SequenceRef(self.previous().lexeme)

    def consume(self, type: TokenType, message: str) -> Token:
        if self.check(type):
            return self.advance()

        token = self.peek()
        if token is not None:
            raise SyntaxError(f"{message} at line {token.line}, column {token.column}")
        else:
            raise SyntaxError(f"{message} at end of input")
