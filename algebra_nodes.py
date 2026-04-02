from __future__ import annotations
from collections.abc import Iterator
from dataclasses import dataclass
from logging_setup import logging

log = logging.getLogger(__name__)


class AlgebraNode:
    def children(self) -> list[AlgebraNode]:
        ret = []
        for value in vars(self).values():
            if isinstance(value, AlgebraNode):
                ret.append(value)
            if isinstance(value, tuple):
                ret.extend(value)
        return ret

    def walk(self) -> Iterator["AlgebraNode"]:
        """Gets all nodes of the tree."""
        # log.debug(f"walking {self}")
        yield self
        for child in self.children():
            yield from child.walk()


@dataclass(frozen=True)
class Num(AlgebraNode):
    """
    A numeric literal node.

    Attributes:
        value (int | float): The numeric value stored in the node.
    """

    value: int | float

    def __repr__(self) -> str:
        return str(self.value)


@dataclass(repr=False, frozen=True)
class Var(AlgebraNode):
    """
    A symbolic variable node.

    Attributes:
        name (str): The variable name.
    """

    name: str

    def __repr__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Neg(AlgebraNode):
    """
    A unary negation node.

    Attributes:
        expr (AlgebraNode): The expression being negated.
    """

    expr: AlgebraNode

    def __repr__(self) -> str:
        if isinstance(self.expr, (Num, Var)):
            return f"-({self.expr!r})"
        return f"-({self.expr!r})"


@dataclass(frozen=True)
class Sum(AlgebraNode):
    """
    An n-ary addition node.

    Attributes:
        terms (tuple[AlgebraNode, ...]): The terms being added.
    """

    terms: tuple[AlgebraNode, ...]

    def __repr__(self) -> str:
        return "(" + " + ".join(repr(term) for term in self.terms) + ")"


@dataclass(frozen=True)
class Prod(AlgebraNode):
    """
    An n-ary multiplication node.

    Attributes:
        factors (tuple[AlgebraNode, ...]): The factors being multiplied.
    """

    factors: tuple[AlgebraNode, ...]

    def __repr__(self) -> str:
        out = str(self.factors[0])
        for factor1, factor2 in zip(self.factors, self.factors[1:]):
            if isinstance(factor1, Num) and isinstance(factor2, Num):
                out += " * "
            out += str(factor2)

        return out


@dataclass(frozen=True)
class Pow(AlgebraNode):
    """
    An exponentiation node.

    Attributes:
        base (AlgebraNode): The base expression.
        exp (AlgebraNode): The exponent expression.
    """

    base: AlgebraNode
    exp: AlgebraNode

    def __repr__(self) -> str:
        return f"({self.base!r}^{self.exp!r})"


@dataclass(frozen=True)
class Inv(AlgebraNode):
    """
    A multiplicative inverse node.

    Attributes:
        expr (AlgebraNode): The expression being inverted.
    """

    expr: AlgebraNode

    def __repr__(self) -> str:
        return f"({self.expr!r})⁻¹"
