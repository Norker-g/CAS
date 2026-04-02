# tests/test_simplify.py

import pytest

from algebra_nodes import Num, Var, Sum, Prod, Neg, Inv, Pow
from simplify import Simplifier


@pytest.fixture
def s() -> Simplifier:
    return Simplifier()


def test_num_stays_same(s: Simplifier) -> None:
    assert s.simplify(Num(5)) == Num(5)


def test_var_stays_same(s: Simplifier) -> None:
    assert s.simplify(Var("x")) == Var("x")


def test_sum_singleton_collapses(s: Simplifier) -> None:
    assert s.simplify(Sum((Num(5),))) == Num(5)


def test_prod_singleton_collapses(s: Simplifier) -> None:
    assert s.simplify(Prod((Var("x"),))) == Var("x")


def test_flatten_nested_sum(s: Simplifier) -> None:
    expr = Sum((Num(1), Sum((Num(2), Num(3)))))
    assert s.simplify(expr) == Num(6)


def test_flatten_nested_prod(s: Simplifier) -> None:
    expr = Prod((Num(2), Prod((Num(3), Num(4)))))
    assert s.simplify(expr) == Num(24)


def test_add_numeric_terms(s: Simplifier) -> None:
    expr = Sum((Num(2), Num(3)))
    assert s.simplify(expr) == Num(5)


def test_multiply_numeric_factors(s: Simplifier) -> None:
    expr = Prod((Num(2), Num(3), Num(4)))
    assert s.simplify(expr) == Num(24)


def test_zero_in_sum_is_removed(s: Simplifier) -> None:
    expr = Sum((Var("x"), Num(0)))
    assert s.simplify(expr) == Var("x")


def test_multiple_zeros_in_sum(s: Simplifier) -> None:
    expr = Sum((Num(0), Var("x"), Num(0)))
    assert s.simplify(expr) == Var("x")


def test_one_in_prod_is_removed(s: Simplifier) -> None:
    expr = Prod((Var("x"), Num(1)))
    assert s.simplify(expr) == Var("x")


def test_multiple_ones_in_prod(s: Simplifier) -> None:
    expr = Prod((Num(1), Var("x"), Num(1)))
    assert s.simplify(expr) == Var("x")


def test_zero_in_prod_annihilates(s: Simplifier) -> None:
    expr = Prod((Var("x"), Num(0), Var("y")))
    assert s.simplify(expr) == Num(0)


def test_neg_of_num(s: Simplifier) -> None:
    assert s.simplify(Neg(Num(5))) == Num(-5)


def test_double_neg_eliminates(s: Simplifier) -> None:
    assert s.simplify(Neg(Neg(Var("x")))) == Var("x")


def test_neg_inside_sum_numeric_part(s: Simplifier) -> None:
    expr = Sum((Num(5), Neg(Num(2))))
    assert s.simplify(expr) == Num(3)


def test_inv_of_num(s: Simplifier) -> None:
    assert s.simplify(Inv(Num(2))) == Num(0.5)


def test_double_inv_eliminates(s: Simplifier) -> None:
    assert s.simplify(Inv(Inv(Var("x")))) == Var("x")


def test_pow_zero_exponent(s: Simplifier) -> None:
    expr = Pow(Var("x"), Num(0))
    assert s.simplify(expr) == Num(1)


def test_pow_one_exponent(s: Simplifier) -> None:
    expr = Pow(Var("x"), Num(1))
    assert s.simplify(expr) == Var("x")


def test_pow_of_num(s: Simplifier) -> None:
    expr = Pow(Num(2), Num(3))
    assert s.simplify(expr) == Num(8)


def test_one_to_any_power(s: Simplifier) -> None:
    expr = Pow(Num(1), Var("x"))
    assert s.simplify(expr) == Num(1)


def test_zero_to_positive_power(s: Simplifier) -> None:
    expr = Pow(Num(0), Num(3))
    assert s.simplify(expr) == Num(0)


def test_combine_like_terms_simple(s: Simplifier) -> None:
    expr = Sum((Var("x"), Var("x")))
    expected = Prod((Num(2), Var("x")))
    assert s.simplify(expr) == expected


def test_combine_like_terms_with_coefficients(s: Simplifier) -> None:
    expr = Sum((Prod((Num(2), Var("x"))), Prod((Num(3), Var("x")))))
    expected = Prod((Num(5), Var("x")))
    assert s.simplify(expr) == expected


def test_x_plus_neg_x_becomes_zero(s: Simplifier) -> None:
    expr = Sum((Var("x"), Neg(Var("x"))))
    assert s.simplify(expr) == Num(0)


def test_combine_like_factors_into_power(s: Simplifier) -> None:
    expr = Prod((Var("x"), Var("x")))
    expected = Pow(Var("x"), Num(2))
    assert s.simplify(expr) == expected


def test_combine_power_factors(s: Simplifier) -> None:
    expr = Prod((Pow(Var("x"), Num(2)), Var("x")))
    expected = Pow(Var("x"), Num(3))
    assert s.simplify(expr) == expected


def test_x_times_inv_x_becomes_one(s: Simplifier) -> None:
    expr = Prod((Var("x"), Inv(Var("x"))))
    assert s.simplify(expr) == Num(1)


def test_nested_expression(s: Simplifier) -> None:
    expr = Sum(
        (
            Prod((Num(2), Var("x"))),
            Prod((Num(3), Var("x"))),
            Num(0),
        )
    )
    expected = Prod((Num(5), Var("x")))
    assert s.simplify(expr) == expected


def test_discard_empty_sum_to_zero(s: Simplifier) -> None:
    assert s.simplify(Sum(tuple())) == Num(0)


def test_discard_empty_prod_to_one(s: Simplifier) -> None:
    assert s.simplify(Prod(tuple())) == Num(1)
