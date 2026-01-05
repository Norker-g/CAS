"""
This module converts the input string into a series of tokens, getting it ready for the parser
"""

from sys import _debugmallocstats
from typing import Dict, List, Optional
from tokens import Token, TokenKind
import logging
log = logging.getLogger(__name__)

class LexerError(Exception):
    pass

CHAR_TO_TOKEN: Dict[str, TokenKind] = {
    '+': TokenKind.PLUS,
    '-': TokenKind.MINUS,
    '*': TokenKind.STAR,
    '/': TokenKind.SLASH,
    '(': TokenKind.LPAREN,
    ')': TokenKind.RPAREN,
}

IGNORED_CHARS = {
    ' ',    # space
    '\t',   # horizontal tab
    '\n',   # newline
    '\r',   # carriage return
}

class Lexer:
    """
    Converts the inputted string into tokens
    Args:
        input (str): The input
        pos (int): The current position in the input
        token_start (int): The beginning of the Token currently parsed, used for debugging purposes
    """


    def __init__(self, source: str,debug: bool = False):
        """
        Store input text and initialize lexer state
        """
        self.source = source
        self.pos = 0
        self.token_start = 0
        self.debug = debug


    @property
    def current_char(self):
        if self.pos < len(self.source):
            return self.source[self.pos]
        else:
            return ""


    def tokenize(self) -> List[Token]:
        '''Runs tokenize_unit until every token is processed and added to a list of tokens, which then is outputted'''
        token_list : List[Token] = []
        while True:
            tok = self.tokenize_unit()      # should always return one Token
            token_list.append(tok)
            if tok.kind is TokenKind.EOF:
                break
        return token_list

    def tokenize_unit(self) -> Token:
        """
        Outputs one Token and changes the position to the beginning of the next Token 
        """
        # Advance pos and token_start to the beginning of the Next Token
        while self.current_char in IGNORED_CHARS:
            self.pos += 1
            if self.debug:
                print(f"Current pos: {self.pos}, skipping char")
        
        log.debug(f"Processing character {self.current_char} at position {self.pos}")
        self.token_start = self.pos
        
        # Identify the next token 
        if self.pos == len(self.source):
            token =  Token(TokenKind.EOF, "", self.token_start)
 
        elif self.current_char.isdigit():
            token =  self._tokenize_number()

        elif self.current_char.isalpha():
            token =  Token(TokenKind.SYMBOL, self.current_char, self.token_start, self.current_char)
            self.pos += 1
         
        elif self.current_char in CHAR_TO_TOKEN:
            token = Token(CHAR_TO_TOKEN[self.current_char], self.current_char, self.token_start)
            self.pos += 1

        else:
            raise LexerError(f"The charecter {self.current_char} at the position {self.pos} could not be recognized by the lexer")

        return token


    def _tokenize_number(self) -> Token:
        '''Makes a Token out of a Number'''
        while (not self.pos == len(self.source)) and self.current_char.isdigit():
            self.pos +=1
        return Token(TokenKind.NUMBER, self._get_token_lexeme() ,self.token_start, int(self._get_token_lexeme()))


    def _get_token_lexeme(self):
        '''returns the lexeme for the token'''
        return self.source[self.token_start:self.pos]


