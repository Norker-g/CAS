from tokens import Token, TokenKind
import logging
from ast_nodes import Node, Unary, Leaf, Binary, Number, Symbol

log = logging.getLogger(__name__)


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset: int = 0) -> Token:
        return self.tokens[self.pos + offset]

    def at_end(self) -> bool:
        return self.peek().kind is TokenKind.EOF

    def advance(self):
        if self.at_end():
            raise ParserError("advance() called at EOF")
        log.debug(
            f"processed token {self.peek()}. Currently at position {self.pos + 1}"
        )
        tok = self.peek()
        self.pos += 1
        return tok

    def check(self, kind: TokenKind) -> bool:
        if self.at_end():
            return False
        return self.peek().kind is kind

    def match(self, *kinds: TokenKind) -> bool:
        for kind in kinds:
            if self.check(kind):
                return True
        return False

    def parse(self):
        # Parsing hierarchy: Sum -> Product -> Unary -> Atom
        tree = self.parse_sum()
        if self.pos + 1 < len(self.tokens):
            log.debug(f"Not all Tokens consumed. Currently at token {self.peek()}")
        return tree

    def parse_sum(self) -> Node:
        left = self.parse_prod()
        while (
            self.match(TokenKind.PLUS, TokenKind.MINUS)
            and not self.check(TokenKind.RPAREN)
            and not self.at_end()
        ):
            op = self.advance().kind
            right = self.parse_prod()
            left = Binary(op, left, right)

        if self.check(TokenKind.RPAREN):
            self.advance()
        return left

    def parse_prod(self) -> Node:
        left = self.parse_unary()
        while (
            self.match(
                TokenKind.STAR,
                TokenKind.SLASH,
                TokenKind.SYMBOL,
                TokenKind.NUMBER,
                TokenKind.LPAREN,
            )
            and not self.at_end()
        ):
            if self.match(TokenKind.STAR, TokenKind.SLASH):
                op = self.peek().kind
                self.advance()
            else:
                op = TokenKind.STAR
            right = self.parse_unary()
            left = Binary(op, left, right)
        return left

    def parse_unary(self) -> Node:
        if self.match(TokenKind.PLUS, TokenKind.MINUS):
            op = self.advance().kind
            expr = self.parse_atom()
            return Unary(op, expr)

        return self.parse_atom()

    def parse_atom(self) -> Node:
        tok = self.peek()
        match tok.kind:
            case TokenKind.NUMBER:
                assert isinstance(tok.value, int | float)
                self.advance()
                return Number(tok.value)
            case TokenKind.SYMBOL:
                assert isinstance(tok.value, str)
                self.advance()
                return Symbol(tok.value)
            case TokenKind.LPAREN:
                self.advance()
                return self.parse_sum()
        raise ParserError(f"Token {tok} not an atom")
