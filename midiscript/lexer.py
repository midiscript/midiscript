from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    NOTE = auto()          # C4, D#3, etc.
    DURATION = auto()      # 1/4, 1/8, etc.
    TEMPO = auto()         # tempo keyword
    TIME = auto()          # time keyword
    NUMBER = auto()        # Any number
    SLASH = auto()         # /
    SEQUENCE = auto()      # sequence keyword
    IDENTIFIER = auto()    # sequence names, etc.
    LBRACE = auto()        # {
    RBRACE = auto()        # }
    LBRACKET = auto()      # [
    RBRACKET = auto()      # ]
    CHANNEL = auto()       # channel keyword
    VELOCITY = auto()      # velocity keyword
    PLAY = auto()          # play keyword
    REST = auto()          # R (rest)
    NEWLINE = auto()       # \n
    EOF = auto()          # End of file


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.text[0] if text else None
        self.last_token_type = None

    def error(self):
        raise Exception(
            f'Invalid character {self.current_char} at line {self.line}, '
            f'column {self.column}'
        )

    def advance(self):
        self.pos += 1
        if self.current_char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.current_char = (
            self.text[self.pos] if self.pos < len(self.text) else None
        )

    def skip_whitespace(self):
        while (self.current_char and self.current_char.isspace() and 
               self.current_char != '\n'):
            self.advance()

    def skip_comment(self):
        while self.current_char and self.current_char != '\n':
            self.advance()

    def number(self) -> Token:
        result = ''
        start_column = self.column
        
        # Read the first number
        while self.current_char and self.current_char.isdigit():
            result += self.current_char
            self.advance()
            
        # Check for duration or time signature
        if self.current_char == '/':
            # If we're after a 'time' keyword, treat as separate tokens
            if self.last_token_type == TokenType.TIME:
                return Token(TokenType.NUMBER, result, self.line, start_column)
            
            # Otherwise, it's a duration
            result += self.current_char
            self.advance()
            
            # Read the second number
            while self.current_char and self.current_char.isdigit():
                result += self.current_char
                self.advance()
                
            return Token(TokenType.DURATION, result, self.line, start_column)
            
        return Token(TokenType.NUMBER, result, self.line, start_column)

    def identifier(self) -> Token:
        result = ''
        start_column = self.column
        
        while (self.current_char and 
               (self.current_char.isalnum() or 
                self.current_char in '#b_')):
            result += self.current_char
            self.advance()

        # Check for keywords
        keywords = {
            'tempo': TokenType.TEMPO,
            'time': TokenType.TIME,
            'sequence': TokenType.SEQUENCE,
            'channel': TokenType.CHANNEL,
            'velocity': TokenType.VELOCITY,
            'play': TokenType.PLAY,
            'R': TokenType.REST
        }

        # Check if it's a note (e.g., C4, D#3, Bb4)
        if (len(result) >= 2 and result[0].upper() in 'ABCDEFG' and 
            result[-1].isdigit()):
            token = Token(TokenType.NOTE, result, self.line, start_column)
        else:
            token = Token(
                keywords.get(result, TokenType.IDENTIFIER),
                result,
                self.line,
                start_column
            )
        
        self.last_token_type = token.type
        return token

    def get_next_token(self) -> Token:
        while self.current_char:
            if self.current_char.isspace() and self.current_char != '\n':
                self.skip_whitespace()
                continue

            if self.current_char == '\n':
                self.advance()
                token = Token(TokenType.NEWLINE, '\n', self.line - 1, 
                            self.column)
                self.last_token_type = token.type
                return token

            if (self.current_char == '/' and self.pos + 1 < len(self.text) 
                and self.text[self.pos + 1] == '/'):
                self.skip_comment()
                continue

            if self.current_char.isdigit():
                token = self.number()
                self.last_token_type = token.type
                return token

            if (self.current_char.isalpha() or 
                self.current_char in '#b_'):
                return self.identifier()

            if self.current_char == '{':
                self.advance()
                token = Token(TokenType.LBRACE, '{', self.line, 
                            self.column - 1)
                self.last_token_type = token.type
                return token

            if self.current_char == '}':
                self.advance()
                token = Token(TokenType.RBRACE, '}', self.line, 
                            self.column - 1)
                self.last_token_type = token.type
                return token

            if self.current_char == '[':
                self.advance()
                token = Token(TokenType.LBRACKET, '[', self.line, 
                            self.column - 1)
                self.last_token_type = token.type
                return token

            if self.current_char == ']':
                self.advance()
                token = Token(TokenType.RBRACKET, ']', self.line, 
                            self.column - 1)
                self.last_token_type = token.type
                return token

            if self.current_char == '/':
                self.advance()
                token = Token(TokenType.SLASH, '/', self.line, 
                            self.column - 1)
                self.last_token_type = token.type
                return token

            self.error()

        token = Token(TokenType.EOF, '', self.line, self.column)
        self.last_token_type = token.type
        return token

    def tokenize(self) -> List[Token]:
        tokens = []
        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens 