from parser_nodes import ParserNode, Binary, Unary, Number, Symbol
from algebra_nodes import AlgebraNode, Sum, Prod, Neg, Num, Var, Pow, Inv
from tokens import TokenKind
import logging

log = logging.getLogger(__name__)


class ConverterError(Exception):
    pass


class Converter:
    def __init__(self, tree: ParserNode):
        self.tree = tree

    def convert_full(self) -> AlgebraNode:
        # I can freely get the 0th of the tuple, because I know that because the parent isnt binary it wont be converted
        return self.convert(self.tree)[0]

    def convert(self, node, parent=None) -> tuple[AlgebraNode, ...]:
        # Tuples are used for Sum / Prod
        log.debug(f"converting:\n  {node} \n with parent \n {parent}")
        match node:
            case Binary():
                return self.convert_binary(node, parent)
            case Unary():
                return self.convert_unary(node)
            case Number(value=v):
                return (Num(v),)
            case Symbol(name=n):
                return (Var(n),)
        raise ConverterError("Unknown Parser Node")

    def convert_binary(self, node: Binary, parent=None) -> tuple[AlgebraNode, ...]:
        op = node.op
        left = node.left
        right = node.right
        if isinstance(parent, Binary) and op == parent.op:
            return (*self.convert(left, node), *self.convert(right, node))

        match op:
            case TokenKind.STAR:
                return (Prod((*self.convert(left, node), *self.convert(right, node))),)
            case TokenKind.SLASH:
                # I can freely get the 0th of the tuple, because I know that because the node isnt binary it wont be converted
                return (Prod((*self.convert(left, node), Inv(self.convert(right)[0]))),)
            case TokenKind.PLUS:
                return (Sum((*self.convert(left, node), *self.convert(right, node))),)
            case TokenKind.MINUS:
                # I can freely get the 0th of the tuple, because I know that because the node isnt binary it wont be converted
                return (Sum((*self.convert(left, node), Neg(self.convert(right)[0]))),)
            case TokenKind.CARET:
                return (Pow(*self.convert(left), *self.convert(right)),)
            case _:
                raise ConverterError("Unkown Binary Operator")

    def convert_unary(self, node: Unary) -> tuple[AlgebraNode, ...]:
        op = node.op
        expr = node.expr
        match op:
            case TokenKind.MINUS:
                # I can freely get the 0th of the tuple, because I know that because the parent isnt binary it wont be converted
                expr = self.convert(expr, node)[0]
                return (Neg(expr),)
            case TokenKind.PLUS:
                return self.convert(expr, node)
        raise ConverterError("Unknown Unary Operator")
