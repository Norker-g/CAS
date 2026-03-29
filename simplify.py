from algebra_nodes import AlgebraNode, Num, Var, Neg, Inv, Sum, Prod, Pow
import logging
from collections.abc import Iterable
import math

log = logging.getLogger(__name__)


class SimplifierError(Exception):
    pass


class Simplifier:
    def __init__(self, tree: AlgebraNode):
        self.tree = tree

    def _is_numerical(self, tree: AlgebraNode):
        is_numerical = True
        for node in tree.walk():
            if isinstance(node, Var):
                is_numerical = False
        return is_numerical

    def simplify(self, node: AlgebraNode) -> AlgebraNode:
        log.debug(f"simplifying {type(node)}({vars(node)})")

        if self._is_numerical(node):
            return Num(self.eval(node))

        match node:
            case Sum():
                return self._simplify_sum(node)
            case Prod():
                return self._simplify_prod(node)
            case Pow(base, exp):
                simplified_pow = Pow(self.simplify(base), self.simplify(exp))
                if simplified_pow.base == Num(1) or simplified_pow.exp == Num(0):
                    return Num(1)
                if simplified_pow.base == Num(0):
                    return Num(0)
                if simplified_pow.exp == Num(1):
                    return simplified_pow.base
                if isinstance(simplified_pow.base, Pow):
                    return Pow(
                        simplified_pow.base.base,
                        Prod((simplified_pow.exp, simplified_pow.base.exp)),
                    )
                return simplified_pow
            case Neg(expr):
                if isinstance(expr, Neg):
                    return self.simplify(expr.expr)
                return node
            case Inv(expr):
                if isinstance(expr, Inv):
                    return self.simplify(expr.expr)
                return Pow(self.simplify(expr), Num(-1))
            case Num():
                return node
            case Var():
                return node

        raise SimplifierError(f"Node type {type(node)} not recognized")

    def _get_vars(self, node: Prod) -> tuple[AlgebraNode, ...]:
        vars = []
        for factor in node.factors:
            if not self._is_numerical(factor):
                vars.append(factor)
        return tuple(vars)

    def _get_coefficients(self, node: Prod) -> tuple[Num, ...]:
        coeffs = []
        for factor in node.factors:
            if self._is_numerical(factor):
                coeffs.append(factor)
        return tuple(coeffs)

    def _simplify_terms(self, terms: Iterable) -> tuple:
        log.debug("started simplifying terms")
        reformed_terms = []  # contains terms after each of them has been simplified enough
        simplified = False
        for term in terms:
            reformed_terms.append(self.simplify(term))
        while not simplified:
            simplified = True
            for term in reformed_terms:
                log.debug(term)
                match term:
                    case Neg():
                        term = self.simplify(term)
                        simplified = False
                    case Inv():
                        term = self.simplify(term)
                        simplified = False
        log.debug("ended simplifying terms")
        return tuple(reformed_terms)

    def _simplify_factors(self, factors: Iterable):
        log.debug("started simplifying factors")
        reformed_factors = []  # contains factors after each of them has been simplified enough
        simplified = False
        for factor in factors:
            reformed_factors.append(self.simplify(factor))
        i = 0
        while not simplified:
            log.debug(f"iteration {i}, simplifying factors {reformed_factors}")
            i += 1
            # cycle over nested factors
            simplified = True
            reformed_factors_buf = []
            for factor in reformed_factors:
                match factor:
                    case Neg(expr):
                        reformed_factors_buf.append(expr)
                        reformed_factors_buf.append(Num(-1))
                        simplified = False
                    case Prod(factors):
                        reformed_factors_buf.extend(factors)
                        simplified = False
                    case _:
                        reformed_factors_buf.append(factor)
            reformed_factors = reformed_factors_buf
        log.debug("ended simplifying factors")
        return tuple(reformed_factors)

    def _simplify_sum(self, node: Sum) -> AlgebraNode:
        reformed_terms = self._simplify_terms(
            node.terms
        )  # contains factors after each of them has been simplified enough
        # Now every numerical term is simplified
        numerical_term = 0
        term_coeff_dict = {}  # contains (tuple for the product of terms):coefficient
        for term in reformed_terms:
            match term:
                case Num(val):
                    numerical_term += val
                case Var():
                    term_coeff_dict[(term,)] = term_coeff_dict.get((term,), 0) + 1
                case Pow():
                    term_coeff_dict[(term,)] = term_coeff_dict.get((term,), 0) + 1
                case Prod():
                    vars = self._get_vars(term)
                    coefficients = self._get_coefficients(term)
                    coefficient = 1
                    for num in coefficients:
                        val = num.value
                        coefficient *= val
                    term_coeff_dict[vars] = term_coeff_dict.get(vars, 0) + coefficient
                case _:
                    # log.error(f"Unexpected Behaviour: {type(node)} inside a Prod")
                    raise SimplifierError(
                        f"Unexpected Behaviour: {type(node)} inside a Sum"
                    )

        non_numerical_tuple = tuple(
            Prod((coefficient, *term)) if coefficient != 1 else Prod(term)
            for term, coefficient in term_coeff_dict.items()
        )
        if numerical_term == 0:
            out_terms = non_numerical_tuple
        else:
            out_terms = (Num(numerical_term), *non_numerical_tuple)

        if len(out_terms) == 1:
            (out_term,) = out_terms
            return out_term

        return Sum(out_terms)

    def _simplify_prod(self, node: Prod) -> AlgebraNode:
        reformed_factors = self._simplify_factors(node.factors)
        # neg_count = 0
        number_factor = 1
        vars_factor_dict = {}  # contains the var names and then their exponents as sums, evaluated at the end

        for factor in reformed_factors:
            # if isinstance(factor, Neg):
            #     neg_count += 1
            #     factor = factor.expr
            match factor:
                case Num(value):
                    number_factor *= value
                case Var(name):
                    vars_factor_dict[name] = (
                        *vars_factor_dict.get(name, ()),
                        Num(1),
                    )
                case Pow(base, exp):
                    if isinstance(base, Num):
                        number_factor *= base.value
                    elif isinstance(base, Var):
                        name = base.name
                        vars_factor_dict[name] = (*vars_factor_dict.get(name, ()), exp)
                case Sum():
                    raise NotImplementedError
                case Prod():
                    log.error(
                        "Unexpected Behaviour: Prod inside a Prod, Should have been flattened"
                    )
                    raise SimplifierError(
                        f"Unexpected Behaviour: {type(node)} inside a Prod"
                    )

                case _:
                    # log.error(f"Unexpected Behaviour: {type(node)} inside a Prod")
                    raise SimplifierError(
                        f"Unexpected Behaviour: {type(node)} inside a Prod"
                    )

        for key, exp in vars_factor_dict.items():
            vars_factor_dict[key] = self.simplify(Sum(exp))
        vars_factor_dict = dict(sorted(vars_factor_dict.items()))
        non_numerical_factor_tuple = tuple(
            self.simplify(Pow(Var(var_name), exp))
            for var_name, exp in vars_factor_dict.items()
        )

        if number_factor == 1:
            factors = non_numerical_factor_tuple
        else:
            factors = (Num(number_factor), *non_numerical_factor_tuple)
        out = factors
        if len(factors) == 1:
            (factor,) = factors
            out = factor
        else:
            out = Prod(factors)
        # if neg_count % 2 == 1:
        #     out = Neg(out)
        return out

    def eval(self, node=None) -> float:
        if node is None:
            node = self.tree
        if not self._is_numerical(node):
            print(
                "Can't Evaluate a expression that contains variables. Evaluation is for purely numerical expressions"
            )
            raise SimplifierError("cant evaluate a expr containing variables")
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
