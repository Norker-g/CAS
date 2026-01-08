"""
This module converts the input string into a series of tokens, getting it ready for the parser
"""

from typing import Dict, List
from tokens import Token, TokenKind
import logging

log = logging.getLogger(__name__)


class LexerError(Exception):
    pass


CHAR_TO_TOKEN: Dict[str, TokenKind] = {
    "+": TokenKind.PLUS,
    "-": TokenKind.MINUS,
    "*": TokenKind.STAR,
    "/": TokenKind.SLASH,
    "(": TokenKind.LPAREN,
    ")": TokenKind.RPAREN,
}

IGNORED_CHARS = {
    " ",  # space
    "\t",  # horizontal tab
    "\n",  # newline
    "\r",  # carriage return
}


class Lexer:
    """
    Converts the inputted string into tokens
    Args:
        input (str): The input
        pos (int): The current position in the input
        token_start (int): The beginning of the Token currently parsed, used for debugging purposes
    """

    def __init__(self, source: str, debug: bool = False):
        """Store input text and initialize lexer state"""
        self.source = source
        self.pos = 0
        self.token_start = 0
        self.debug = debug

    def peek(self):
        if self.pos >= len(self.source):
            return "\0"
        return self.source[self.pos]

    def advance(self) -> str:
        """Returns the current character and moves one char"""
        ch = self.peek()
        if ch != "\0":
            self.pos += 1
        log.debug(f"processing character number {self.pos}: '{ch}'")
        return ch

    def tokenize(self) -> List[Token]:
        """Runs next_token until every token is processed and added to a list of tokens, which then is outputted"""
        token_list: List[Token] = []
        while True:
            tok = self.next_token()  # should always return one Token
            token_list.append(tok)
            log.debug(f"Successfully processed token number {len(token_list)}: {tok}")
            if tok.kind is TokenKind.EOF:
                break
        return token_list

    def next_token(self) -> Token:
        """Outputs one Token and changes the position to the beginning of the next Token"""

        self._skip_ignored()

        self.token_start = self.pos
        ch = self.advance()

        # Identify the next token
        if ch == "\0":
            token = Token(TokenKind.EOF, "", self.token_start)

        elif ch.isdigit():
            token = self._tokenize_number()

        elif ch.isalpha():
            token = Token(TokenKind.SYMBOL, self.peek(), self.token_start, self.peek())

        elif ch in CHAR_TO_TOKEN:
            token = Token(CHAR_TO_TOKEN[self.peek()], self.peek(), self.token_start)

        else:
            raise LexerError(
                f"The charecter {self.peek()} at the position {self.pos} could not be recognized by the lexer"
            )

        return token

    def _tokenize_number(self) -> Token:
        """Makes a Token out of a Number"""
        ch = self.peek()
        while ch.isdigit():
            ch = self.advance()
        lexeme = self._get_token_lexeme()
        return Token(TokenKind.NUMBER, lexeme, self.token_start, int(lexeme))

    def _get_token_lexeme(self):
        """returns the lexeme for the token"""
        return self.source[self.token_start : self.pos]

    def _skip_ignored(self):
        while self.peek() in IGNORED_CHARS:
            self.advance()
            log.debug(f"Current pos: {self.pos}, skipping char")
