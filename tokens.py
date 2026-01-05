from enum import auto, Enum 
from typing import Optional, Any
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
    EOF = auto()

@dataclass
class Token:
    '''
    The class for Tokens outputted by the lexer
    Args:
        kind (TokenKind): The Token name / type
        lexeme (str): The string that was lexed and perceived to be the Token
        pos (int): The number of the char in the input, that was the first char of the Token
        value (Any): Optional, needed for tokens with many values, like numebrs and variables
    '''
    kind: TokenKind 
    lexeme: str
    pos: int
    value: Optional[Any] = None
