'''
The parser takes a list of Tokens and transforms it into a AST graph.
'''
from tokens import Token, TokenKind
from nodes import *
import logging
log = logging.getLogger(__name__)

class ParserError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0

    @property
    def tok(self):
        return self.tokens[self.i]

    def parse(self) -> Node:
        parsed = None
        while self.tok.kind != TokenKind.EOF:
            parsed = self._parse_sum(parsed)
            log.debug(f"top level parsed is {parsed}. Currently at index {self.i}")
        if parsed is None: raise ParserError(f"right operator in the sum at index i = {self.i} is None")
        return  parsed
            
    def _parse_sum(self, left) -> Node:
        log.debug(f"Entering _parse_sum(). Currently at index {self.i}")
        if self.tok.kind == TokenKind.EOF: return left

        elif self.tok.kind in (TokenKind.PLUS, TokenKind.MINUS):
            right = None
            op = self.tok.kind
            self.i += 1
            while not self.tok.kind in (TokenKind.PLUS, TokenKind.MINUS, TokenKind.EOF):
                right = self._parse_prod(right) 
            if right is None: raise ParserError(f"right operator in the sum at index i = {self.i} is None")
            return Binary(left, op, right)

        else: return self._parse_prod(left)

    def _parse_prod(self, left) -> Node:
        log.debug(f"Entering _parse_prod(). Currently at index {self.i}")
        if self.tok.kind == TokenKind.EOF: return left

        elif self.tok.kind in (TokenKind.STAR, TokenKind.SLASH):

            op = self.tok.kind
            self.i += 1
            right = self._parse_leaf() 
            return Binary(left, op, right)

        else: return self._parse_leaf()

    def _parse_leaf(self) -> Node:
        if self.tok.kind == TokenKind.NUMBER: out =  self._parse_num()
        elif self.tok.kind == TokenKind.SYMBOL: out =  self._parse_symbol()
        self.i+=1
        return out

    def _parse_num(self) -> Node:
        return Number(self.tok.value)

    def _parse_symbol(self) -> Node:
        return Symbol(self.tok.value)


