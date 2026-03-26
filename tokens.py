from enum import auto, Enum
from typing import Any
from dataclasses import dataclass


class TokenKind(Enum):
    NUMBER = auto()
    SYMBOL = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    LPAREN = auto()
    RPAREN = auto()
    CARET = auto()
    EOF = auto()

    def __str__(self) -> str:
        return self.name


@dataclass
class Token:
    """
    The class for Tokens outputted by the lexer
    Args:
        kind (TokenKind): The Token name / type
        lexeme (str): The string that was lexed and perceived to be the Token
        pos (int): The number of the char in the input, that was the first char of the Token
        value (Any): Optional, needed for tokens with multiple possible values, like numbers and variables
    """

    kind: TokenKind
    lexeme: str
    pos: int
    value: int | float | str | None = None

    def __repr__(self) -> str:
        if self.value is None:
            return f"Token({self.kind}, {self.lexeme!r}, pos={self.pos})"
        return (
            f"Token({self.kind}, {self.lexeme!r}, pos={self.pos}, value={self.value!r})"
        )
