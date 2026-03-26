from algebra_nodes import AlgebraNode, Num, Var, Neg, Inv, Sum, Prod, Pow


class Simplifier:
    def __init__(self, tree: AlgebraNode):
        self.tree = tree
        self.is_numerical = True
        for node in self.tree.walk():
            if isinstance(node, Var):
                self.is_numerical = False

    def eval(self, node=None) -> float:
        if node is None:
            node = self.tree

        if not self.is_numerical:
            raise Exception("cant evaluate a expr containing variables")
        match node:
            case Pow(base=b, exp=e):
                return self.eval(b) ** self.eval(e)
            case Sum(terms=t):
                ret = 0
                for term in t:
                    ret += self.eval(term)
                return ret
            case Prod(factors=f):
                ret = 1
                for factor in f:
                    ret *= self.eval(factor)
                return ret
            case Neg(expr=e):
                return -1 * self.eval(e)
            case Inv(expr=e):
                return 1 / self.eval(e)
            case Num(value=v):
                return v
        raise Exception(f"Node type {type(node)} not recognized")
