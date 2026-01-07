'''
The parser takes a list of Tokens and transforms it into a AST graph.
'''
from tokens import Token, TokenKind
from ast_nodes import *
import logging
log = logging.getLogger(__name__)

class ParserError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0
        self.bracket_level = 0 

    @property
    def tok(self):
        return self.tokens[self.i]

    def parse(self) -> Node:
        parsed = None
        while self.tok.kind != TokenKind.EOF:
            parsed = self._parse_sum(parsed)
            log.debug(f"parsed = {parsed}. Currently at i = {self.i}")
        if parsed is None: raise ParserError(f"right operator in the sum at index i = {self.i} is None")
        return  parsed

    def _parse_sum(self, left) -> Node:
        log.debug(f"Entering _parse_sum(). Currently at index {self.i}. left = {left}")
        if self.tok.kind == TokenKind.EOF: return left

        elif self.tok.kind in (TokenKind.PLUS, TokenKind.MINUS):
            right = None
            op = self.tok.kind
            self.i += 1
            while not self.tok.kind in (TokenKind.PLUS, TokenKind.MINUS, TokenKind.EOF):
                right = self._parse_sum(right) 
            if right is None: raise ParserError(f"right operator in the sum at index i = {self.i} is None")
            return Binary(left, op, right)

        elif self.tok.kind == TokenKind.LPAREN:
            return self._handle_left_brackets()
        elif self.tok.kind == TokenKind.RPAREN and self.bracket_level > 0:
            self.i += 1
            self.bracket_level -= 1
            return left
        else: return self._parse_prod(left)

    def _parse_prod(self, left) -> Node:
        log.debug(f"Entering _parse_prod(). Currently at index {self.i}. left = {left}")
        if self.tok.kind == TokenKind.EOF: return left
            
        elif self.tok.kind in (TokenKind.STAR, TokenKind.SLASH):
            op = self.tok.kind
            self.i += 1
            right = self._parse_prod(None) 
            return Binary(left, op, right)
        
            
        elif self.tok.kind == TokenKind.LPAREN:
            return self._handle_left_brackets()
        elif self.tok.kind == TokenKind.RPAREN and self.bracket_level > 0:
            self.i += 1
            self.bracket_level -= 1
            return left
        else: return self._parse_leaf()

    def _parse_leaf(self) -> Node:
        if self.tok.kind == TokenKind.NUMBER: out =  self._parse_num()
        elif self.tok.kind == TokenKind.SYMBOL: out =  self._parse_symbol()
        else: raise ParserError(f'Expected NUMBER or SYMBOL, instead got {self.tok.kind} "{self.tok.lexeme}" at {self.i}')
        self.i+=1
        return out

    def _parse_num(self) -> Node:
        return Number(self.tok.value)

    def _parse_symbol(self) -> Node:
        return Symbol(self.tok.value)

    def _handle_left_brackets(self)-> Node:
        self.i += 1
        self.bracket_level += 1
        return self.parse()
    
