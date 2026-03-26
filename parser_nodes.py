from dataclasses import dataclass
from tokens import TokenKind
from collections.abc import Iterator


class ParserNode:
    def children(self) -> Iterator["ParserNode"]:
        return (value for value in vars(self).values() if isinstance(value, ParserNode))

    def label(self) -> str:
        parts = []
        for name, value in vars(self).items():
            if isinstance(value, ParserNode):
                continue
            if isinstance(value, TokenKind):
                parts.append(f"{name}={value.name}")
            else:
                parts.append(f"{name}={value!r}")
        return f"{self.__class__.__name__}({', '.join(parts)})"

    def pretty(self, prefix: str = "", is_last: bool = True) -> str:
        branch = "└── " if is_last else "├── "
        out = prefix + branch + self.label()

        kids = list(self.children())
        if kids:
            child_prefix = prefix + ("    " if is_last else "│   ")
            lines = [
                child.pretty(child_prefix, i == len(kids) - 1)
                for i, child in enumerate(kids)
            ]
            out += "\n" + "\n".join(lines)

        return out

    def __repr__(self) -> str:
        return self.pretty(prefix="", is_last=True)


@dataclass(repr=False)
class Number(ParserNode):
    value: int | float


@dataclass(repr=False)
class Symbol(ParserNode):
    name: str


@dataclass(repr=False)
class Unary(ParserNode):
    op: TokenKind
    expr: ParserNode


@dataclass(repr=False)
class Binary(ParserNode):
    op: TokenKind
    left: ParserNode
    right: ParserNode
