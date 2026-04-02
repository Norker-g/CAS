from algebra_nodes import AlgebraNode, Num, Var, Neg, Inv, Sum, Prod, Pow
import logging
from collections.abc import Iterable
import math
import itertools
from typing import reveal_type


log = logging.getLogger(__name__)


class SimplifierError(Exception):
    pass


class Simplifier:
    def _is_numerical(self, tree: AlgebraNode):
        is_numerical = True
        for node in tree.walk():
            if isinstance(node, Var):
                is_numerical = False
        return is_numerical

    def simplify(self, node: AlgebraNode) -> AlgebraNode:

        if self._is_numerical(node):
            return self.eval(node)

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
                        self.simplify(
                            Prod((simplified_pow.exp, simplified_pow.base.exp))
                        ),
                    )
                if isinstance(simplified_pow.base, Prod):
                    out = Prod(
                        tuple(
                            self.simplify(Pow(factor, exp))
                            for factor in simplified_pow.base.factors
                        )
                    )
                    log.debug(out)
                    return out
                return simplified_pow
            case Neg(expr):
                if isinstance(expr, Neg):
                    return self.simplify(expr.expr)
                return node
            case Inv(expr):
                if isinstance(expr, Inv):
                    return self.simplify(expr.expr)
                return self.simplify(Pow(expr, Num(-1)))
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

    def _get_nums_from_product(self, node: Prod) -> tuple[Num, ...]:
        coeffs: list[Num] = []
        for factor in node.factors:
            if self._is_numerical(factor):
                coeffs.append(self.eval(factor))
        return tuple(coeffs)

    def _simplify_terms(self, terms: Iterable) -> tuple:
        reformed_terms = []  # contains terms after each of them has been simplified enough
        simplified = False
        for term in terms:
            reformed_terms.append(self.simplify(term))
        while not simplified:
            log.debug(reformed_terms)
            reformed_terms_buf = []
            simplified = True
            for term in reformed_terms:
                match term:
                    case Neg(expr):
                        reformed_terms_buf.append(self.simplify(Prod((Num(-1), expr))))
                        simplified = False
                    case Inv(expr):
                        reformed_terms_buf.append(self.simplify(Pow(expr, Num(-1))))
                        simplified = False
                    case Sum(terms):
                        reformed_terms_buf.remove(term)
                        reformed_terms_buf.extend(terms)
                        simplified = False
                    case _:
                        reformed_terms_buf.append(term)
            reformed_terms = reformed_terms_buf
        return tuple(reformed_terms)

    def _simplify_sum(self, node: Sum) -> AlgebraNode:
        log.debug(f"simplifying sum: {node}")
        reformed_terms = self._simplify_terms(
            node.terms
        )  # contains factors after each of them has been simplified enough
        log.debug(f"simplified terms: {reformed_terms}")
        # Now every numerical term is simplified
        numerical_term: int | float = 0
        term_coeff_dict: dict[
            tuple, int | float
        ] = {}  # contains (tuple for the product of terms):coefficient
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
                    coefficients = self._get_nums_from_product(term)
                    # calculates the coefficient of the term
                    coefficient: int | float = 1
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
            self.simplify(Prod((Num(coefficient), *term)))
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
        # flattening the factors, by reducing Inv, Neg and Prod
        # log.debug("started simplifying factors")
        reformed_factors = [
            self.simplify(factor) for factor in node.factors
        ]  # contains factors after each of them has been simplified enough
        simplified = False
        while not simplified:
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
        log.debug(f"finished simplifying factors: {reformed_factors}")
        number_factor: int | float = 1
        vars_factor_dict: dict[
            str, tuple[AlgebraNode, ...]
        ] = {}  # contains the var names and then their exponents as sums, evaluated at the end
        distributive_terms = []
        # combining like terms
        for factor in reformed_factors:
            log.debug(f"processing term: {factor}")
            match factor:
                case Num(value):
                    number_factor *= value
                    if value == 0:  # checks for multiplication by 0
                        return Num(0)
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
                    distributive_terms.append(factor.terms)
                case Prod() | Inv() | Neg():
                    log.error(
                        f"Unexpected Behaviour: {type(node)} inside a Prod, Should have been flattened"
                    )
                    raise SimplifierError(
                        f"Unexpected Behaviour: {type(node)} inside a Prod"
                    )

                case _:
                    # log.error(f"Unexpected Behaviour: {type(node)} inside a Prod")
                    raise SimplifierError(
                        f"Unexpected Behaviour: {type(node)} inside a Prod"
                    )
        alg_vars_factor_dict: dict[str, AlgebraNode] = {}
        for key, exp in vars_factor_dict.items():  # type: ignore
            alg_vars_factor_dict[key] = self.simplify(Sum(exp))  # type: ignore
        vars_factor_dict = dict(sorted(vars_factor_dict.items()))

        non_numerical_factor_tuple = tuple(
            self.simplify(Pow(Var(var_name), exp))
            for var_name, exp in alg_vars_factor_dict.items()
            if exp != Num(0)
        )
        # Multiplication by 0 check inside iterators
        if number_factor == 1 and len(non_numerical_factor_tuple) > 0:
            factors = non_numerical_factor_tuple
        else:
            factors = (Num(number_factor), *non_numerical_factor_tuple)
        if len(factors) == 1:
            (factor,) = factors
            out = factor
        else:
            out = Prod(factors)

        if len(distributive_terms) > 0:
            distributed_terms = itertools.product(*distributive_terms)
            return Sum(
                tuple(self.simplify(Prod((out, *term))) for term in distributed_terms)
            )

        return out

    def eval(self, node) -> Num:
        if not self._is_numerical(node):
            print(
                "Can't Evaluate a expression that contains variables. Evaluation is for purely numerical expressions"
            )
            raise SimplifierError("cant evaluate a expr containing variables")
        match node:
            case Pow(base=b, exp=e):
                return Num(self.eval(b).value ** self.eval(e).value)
            case Sum(terms=t):
                ret: int | float = 0
                for term in t:
                    ret += self.eval(term).value
                return Num(ret)
            case Prod(factors=f):
                ret = 1
                for factor in f:
                    ret *= self.eval(factor).value
                return Num(ret)
            case Neg(expr=e):
                return Num(-1 * self.eval(e).value)
            case Inv(expr=e):
                return Num(1 / self.eval(e).value)
            case Num(value=v):
                return node
        raise Exception(f"Node type {type(node)} not recognized")
