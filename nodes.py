from dataclasses import dataclass
from collections.abc import Iterable
from tokens import TokenKind

class Node:

    def children(self) -> Iterable["Node"]:
        '''
        outputs a tuple with all of the Children of the Node
        recognizes children based on being Node type
        '''
        node_var_values = vars(self).values()
        children_list = []
        for var in node_var_values:
            if type(var) == Node:
                children_list.append(var)

        return tuple(children_list)

class Leaf(Node):
    pass

@dataclass
class Number(Leaf):
    value: int | float 


@dataclass
class Symbol(Leaf):
    name: str

@dataclass
class Unary(Node):
    op: TokenKind
    expr: Node

@dataclass
class Binary(Node):
    left: Node
    op: TokenKind
    right: Node

