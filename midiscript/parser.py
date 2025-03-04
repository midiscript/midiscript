from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict
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
    sequences: Dict[str, Sequence] = field(default_factory=dict)
    tempo: Optional[TempoChange] = None
    time_signature: Optional[TimeSignature] = None
    main_sequence: Optional[str] = None

    def __post_init__(self):
        if self.sequences is None:
            self.sequences = {}


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.sequences: Dict[str, Sequence] = {}

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

    def parse(self) -> Program:
        program = Program()
        try:
            while not self.is_at_end():
                self.skip_newlines()  # Skip any leading newlines
                token = self.peek()
                if token:
                    print(
                        f"Processing token: {token.type} '{token.lexeme}' at line {token.line}, column {token.column}"
                    )
                if self.match(TokenType.TEMPO):
                    print("Found tempo")
                    self.parse_tempo(program)
                    print(
                        f"Set tempo to {program.tempo.value if program.tempo else None}"
                    )
                elif self.match(TokenType.TIME):
                    print("Found time signature")
                    self.parse_time_signature(program)
                elif self.match(TokenType.SEQUENCE):
                    print("Found sequence")
                    self.sequence_declaration()
                elif self.match(TokenType.PLAY):
                    print("Found play")
                    self.parse_play(program)
                elif self.match(TokenType.NEWLINE):
                    print("Skipping newline")
                    continue  # Skip newlines between statements
                else:
                    print("Unexpected token, advancing")
                    self.advance()
            program.sequences.update(self.sequences)
            return program
        except Exception as e:
            # Log the error and return empty program
            print(f"Error parsing: {str(e)}")
            return Program()

    def parse_tempo(self, program: Program) -> None:
        print("Parsing tempo")
        value = self.consume(TokenType.NUMBER, "Expected tempo value.")
        print(f"Found tempo value: {value.lexeme}")
        program.tempo = TempoChange(int(value.lexeme))
        self.skip_newlines()  # Skip newlines after tempo

    def parse_time_signature(self, program: Program) -> None:
        numerator = self.consume(TokenType.NUMBER, "Expected time signature numerator.")
        self.consume(TokenType.SLASH, "Expected '/' in time signature.")
        denominator = self.consume(
            TokenType.NUMBER, "Expected time signature denominator."
        )
        program.time_signature = TimeSignature(
            int(numerator.lexeme), int(denominator.lexeme)
        )
        self.skip_newlines()  # Skip newlines after time signature

    def parse_play(self, program: Program) -> None:
        sequence_name = self.consume(
            TokenType.IDENTIFIER, "Expected sequence name after 'play'."
        )
        program.main_sequence = sequence_name.lexeme
        self.skip_newlines()  # Skip newlines after play

    def sequence_declaration(self) -> None:
        print("Starting sequence declaration")
        name = self.consume(TokenType.IDENTIFIER, "Expected sequence name.")
        print(f"Found sequence name: {name.lexeme}")
        self.skip_newlines()  # Skip newlines before '{'
        self.consume(TokenType.LBRACE, "Expected '{' after sequence name.")
        print("Found opening brace")
        self.skip_newlines()  # Skip newlines after '{'

        events: List[Union[Note, Chord, Rest, SequenceRef]] = []

        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            self.skip_newlines()  # Skip newlines between events
            token = self.peek()
            if token:
                print(
                    f"Processing event token: {token.type} '{token.lexeme}' at line {token.line}, column {token.column}"
                )
            if self.match(TokenType.NOTE):
                print("Found note")
                events.append(self.note())
            elif self.match(TokenType.LBRACKET):
                print("Found chord start")
                events.append(self.chord())
            elif self.match(TokenType.REST):
                print("Found rest")
                events.append(self.rest())
            elif self.match(TokenType.IDENTIFIER):
                print("Found sequence reference")
                events.append(self.sequence_ref())
            elif self.match(TokenType.NEWLINE):
                print("Skipping newline")
                continue  # Skip newlines
            else:
                break  # Exit the loop when we find something unexpected

        self.skip_newlines()  # Skip newlines before '}'
        self.consume(TokenType.RBRACE, "Expected '}' after sequence events.")
        print("Found closing brace")
        sequence = Sequence(name.lexeme, events)
        self.sequences[name.lexeme] = sequence
        print(f"Added sequence {name.lexeme} with {len(events)} events")

    def note(self) -> Note:
        note_name = self.previous().lexeme  # Get the note name from the previous token
        print(f"Found note name: {note_name}")

        # Parse duration as number/slash/number
        numerator = self.consume(TokenType.NUMBER, "Expected duration numerator.")
        self.consume(TokenType.SLASH, "Expected '/' in duration.")
        denominator = self.consume(TokenType.NUMBER, "Expected duration denominator.")
        duration = f"{numerator.lexeme}/{denominator.lexeme}"
        print(f"Found duration: {duration}")

        return Note(
            name=note_name,
            duration=duration,
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

        # Parse duration as number/slash/number
        numerator = self.consume(TokenType.NUMBER, "Expected duration numerator.")
        self.consume(TokenType.SLASH, "Expected '/' in duration.")
        denominator = self.consume(TokenType.NUMBER, "Expected duration denominator.")
        duration = f"{numerator.lexeme}/{denominator.lexeme}"

        return Chord(notes, duration)

    def rest(self) -> Rest:
        # Parse duration as number/slash/number
        numerator = self.consume(TokenType.NUMBER, "Expected duration numerator.")
        self.consume(TokenType.SLASH, "Expected '/' in duration.")
        denominator = self.consume(TokenType.NUMBER, "Expected duration denominator.")
        duration = f"{numerator.lexeme}/{denominator.lexeme}"

        return Rest(duration)

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
