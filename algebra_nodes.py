from collections.abc import Iterator
from dataclasses import dataclass


class AlgebraNode:
    def children(self) -> tuple["AlgebraNode", ...]:
        return tuple(
            value for value in vars(self).values() if isinstance(value, AlgebraNode)
        )

    def walk(self) -> Iterator["AlgebraNode"]:
        """Gets all nodes of the tree."""
        yield self
        for child in self.children():
            yield from child.walk()


@dataclass(repr=False)
class Num(AlgebraNode):
    """
    A numeric literal node.

    Attributes:
        value (int | float): The numeric value stored in the node.
    """

    value: int | float

    def __repr__(self) -> str:
        return str(self.value)


@dataclass(repr=False)
class Var(AlgebraNode):
    """
    A symbolic variable node.

    Attributes:
        name (str): The variable name.
    """

    name: str

    def __repr__(self) -> str:
        return self.name


@dataclass(repr=False)
class Neg(AlgebraNode):
    """
    A unary negation node.

    Attributes:
        expr (AlgebraNode): The expression being negated.
    """

    expr: AlgebraNode

    def __repr__(self) -> str:
        if isinstance(self.expr, (Num, Var)):
            return f"-{self.expr!r}"
        return f"-({self.expr!r})"


@dataclass(repr=False)
class Sum(AlgebraNode):
    """
    An n-ary addition node.

    Attributes:
        terms (tuple[AlgebraNode, ...]): The terms being added.
    """

    terms: tuple[AlgebraNode, ...]

    def __repr__(self) -> str:
        return "(" + " + ".join(repr(term) for term in self.terms) + ")"


@dataclass(repr=False)
class Prod(AlgebraNode):
    """
    An n-ary multiplication node.

    Attributes:
        factors (tuple[AlgebraNode, ...]): The factors being multiplied.
    """

    factors: tuple[AlgebraNode, ...]

    def __repr__(self) -> str:
        return "(" + " * ".join(repr(factor) for factor in self.factors) + ")"


@dataclass(repr=False)
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


@dataclass(repr=False)
class Inv(AlgebraNode):
    """
    A multiplicative inverse node.

    Attributes:
        expr (AlgebraNode): The expression being inverted.
    """

    expr: AlgebraNode

    def __repr__(self) -> str:
        return f"({self.expr!r})^(-1)"
