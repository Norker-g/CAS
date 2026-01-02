from enum import auto, Enum 
from typing import Optional, Any
from dataclasses import dataclass


class TokenKind(Enum):
    NUMBER = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    LPAREN = auto()
    RPAREN = auto()
    EOF = auto()

@dataclass
class Token:
    kind: TokenKind 
    lexeme: str
    pos: int
    value: Optional[Any] = None

t = Token(TokenKind.PLUS, lexeme = "+", pos = 2)
print(t)
