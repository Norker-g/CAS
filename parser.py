"""
The parser takes a list of Tokens and transforms it into a AST graph.
"""

from tokens import Token, TokenKind
from ast_nodes import Node, Leaf, Binary, Number, Symbol
import logging

log = logging.getLogger(__name__)


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0
        self.bracket_level = 0

    # Helper functions
    def peek(self, offset: int = 0) -> Token:
        return self.tokens[self.i + offset]

    def at_end(self) -> bool:
        return self.peek().kind is TokenKind.EOF

    def previous(self) -> Token:
        if self.i == 0:
            raise ParserError("previous() called before consuming any token")
        return self.tokens[self.i - 1]

    def advance(self):
        if self.at_end():
            raise ParserError("advance() called at EOF")
        self.i += 1
        return self.previous()

    def check(self, kind: TokenKind) -> bool:
        if self.at_end():
            return False
        return self.peek().kind is kind

    def match(self, *kinds: TokenKind) -> bool:
        for kind in kinds:
            if self.check(kind):
                return True
        return False

    def consume(self, kind: TokenKind, message: str):
        if self.check(kind):
            return self.advance()

        tok = self.peek()
        raise ParserError(f"{message}. Got {tok.kind} at position {tok.pos}")

    # main logic
    def parse(self) -> Node:
        parsed = None
        while not self.at_end():
            parsed = self.parse_sum(parsed)
            log.debug(f"parsed = {parsed}. Currently at i = {self.i}")
        if parsed is None:
            raise ParserError(
                f"right operator in the sum at index i = {self.i} is None"
            )
        return parsed

    def parse_sum(self, left) -> Node:
        log.debug(f"Entering parse_sum(). Currently at index {self.i}. left = {left}")
        if self.match(TokenKind.PLUS, TokenKind.MINUS):
            right = None
            op = self.peek().kind
            while self.match(TokenKind.PLUS, TokenKind.MINUS):
                self.advance()
                right = self.parse_prod(right)

            if right is None:
                raise ParserError(
                    f"right operator in the sum at index i = {self.i} is None"
                )
            return Binary(left, op, right)
        else:
            return self.parse_prod(left)

    def parse_prod(self, left) -> Node:
        log.debug(f"Entering parse_prod(). Currently at index {self.i}. left = {left}")
        if self.match(TokenKind.STAR, TokenKind.SLASH):
            op = self.advance().kind
            right = self.parse_atom()
            return Binary(left, op, right)

        elif self.check(TokenKind.LPAREN):
            return self._handle_left_brackets()
        elif self.check(TokenKind.RPAREN):
            self.advance()
            self.bracket_level -= 1
            return left
        else:
            return self.parse_atom()

    def parse_atom(self) -> Node:
        if self.check(TokenKind.NUMBER):
            tok = self.advance()
            return Number(tok.value)  # pyright: ignore[reportArgumentType]
        elif self.check(TokenKind.SYMBOL):
            tok = self.advance()
            return Symbol(tok.value)  # pyright: ignore[reportArgumentType]
        elif self.check(TokenKind.LPAREN):
            self.bracket_level += 1
            pass
        elif self.check(TokenKind.RPAREN):
            self.bracket_level -= 1
            pass
        else:
            raise ParserError(
                f"parse_atom got unexpected TokenKind: {self.peek().kind}"
            )

    def _handle_left_brackets(self) -> Node:
        self.advance()
        self.bracket_level += 1
        return self.parse()
