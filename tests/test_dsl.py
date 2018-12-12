# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from required import Requires, R, Func
from required.dsl import build_requirements_factory, init_transformer, init_parser

def custom_f(x):
    return x

statement_matches = [
    ("x -> y", Requires("x", "y"), {}),
    ("x -> x > (y + 1)", Requires("x", R("x") > R("y") + 1), {}),
    ("x -> x > y", Requires("x", R("x") > R("y")), {}),
    ("x -> x < y", Requires("x", R("x") < R("y")), {}),
    ("x -> len(x) < y", Requires("x", Func(len, R("x")) < R("y")), {}),
    ("x -> x in y", Requires("x", R("x").in_(R("y"))), {}),
    ("len(x) == 0 -> y", Requires(Func(len, R("x")) == 0, "y"), {}),
    ("len(x) > 0 -> y", Requires(Func(len, R("x")) > 0, "y"), {}),
    ("abs(x) > 0 -> y", Requires(Func(abs, R("x")) > 0, "y"), {}),
    ("x > 0 -> x > y", Requires(R("x") > 0, R("x") > R("y")), {}),
    ("x -> (len(x) + 1) < y", Requires("x", Func(len, R("x")) + 1 < R("y")), {}),
    ("x -> (len(x) + 1) < y", Requires("x", Func(len, R("x")) + 1 < R("y")), {}),
    ("x -> (len(y) + len(z)) < x", Requires("x", Func(len, R("y")) + Func(len, R("z")) < R("x")), {}),
    (
        "x -> y; x -> z > y",
        Requires("x", "y") + Requires("x", R("z") > R("y")),
        {}
    ),
    (
        "x -> y;x -> z > y;",
        Requires("x", "y") + Requires("x", R("z") > R("y")),
        {}
    ),
    (
        """
        x -> y
        x -> z > y
        """,
        Requires("x", "y") + Requires("x", R("z") > R("y")),
        {}
    ),
    (
        """
        x -> y;
        x -> z > y;
        """,
        Requires("x", "y") + Requires("x", R("z") > R("y")),
        {}
    ),
    (
        """x -> y
        x -> z > y
        """,
        Requires("x", "y") + Requires("x", R("z") > R("y")),
        {}
    ),
    (
        """
        x -> y
        len(x) > 0 -> len(z) > len(y)
        """,
        Requires("x", "y") + Requires(Func(len, R("x")) > 0, Func(len, R("z")) > Func(len, R("y"))),
        {}
    ),
    (
        """
        x->y
        len(x)>0->len(z)>len(y)
        """,
        Requires("x", "y") + Requires(Func(len, R("x")) > 0, Func(len, R("z")) > Func(len, R("y"))),
        {}
    ),
    (
        """
        x->y;
        """,
        Requires("x", "y"),
        {}
    ),
    (
        """
        x      ->              y;
        x->              z             ;
        """,
        Requires("x", "y") + Requires("x", "z"),
        {}
    ),
    (
        """

        Some other docstring thing

        Requires {
            x -> y
            x -> z
        }""",
        Requires("x", "y") + Requires("x", "z"),
        {}
    ),
    (
        """
        Some other docstring thing

        Requires {
            x -> y
            x -> z
        }

        some things after requires
        """,
        Requires("x", "y") + Requires("x", "z"),
        {}
    ),
    (
        """
        something
        something

        Thing:
            @!->

        Requires {
            x == "hello" -> y == "world";
            x == 1.01 -> y == "world";
            x == -1.01 -> y == "world";
        }
        """,
        Requires(R("x") == "hello", R("y") == "world") +
        Requires(R("x") == 1.01, R("y") == "world") +
        Requires(R("x") == -1.01, R("y") == "world"),
        {}
    ),
    (
        """
        something
        something

        Thing:
            @!->

        Requires {
            x == "hello" -> y == "world"; x == 1.01 -> y == "world"; x == -1.01 -> y == "world";}
        """,
        Requires(R("x") == "hello", R("y") == "world") +
        Requires(R("x") == 1.01, R("y") == "world") +
        Requires(R("x") == -1.01, R("y") == "world"),
        {}
    ),
    (
        """
        customf(x) == "hello" -> customf(y) == "world";
        """,
        Requires(Func(custom_f, R("x")) == "hello", Func(custom_f, R("y")) == "world"),
        {"customf": custom_f}
    ),
    (
        """
        arr -> len(arr) >= 1
        """,
        Requires("arr", Func(len, R("arr")) >= 1),
        {}
    )

]


class TestBuildRequirements(object):

    @pytest.mark.parametrize("dsl_txt,requires,callables_dict", statement_matches)
    def test_matches_requires_single_requires(self, dsl_txt, requires, callables_dict):
        callables_dict = callables_dict or {"len": len, "abs": abs}
        requirements_builder = build_requirements_factory(init_parser(), init_transformer(callables_dict))
        r1 = requirements_builder(dsl_txt)
        assert r1 == requires
