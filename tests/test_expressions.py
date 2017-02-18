# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from required.expressions import (
    R, Lte, Lt, Gte, Gt, Eq, NotEq
)


class TestOperators(object):

    def test_lte_operator(self):
        lhs = R("x")
        rhs = R("y")
        op = Lte(lhs, rhs)
        assert op({"x": 1, "y": 2})
        assert not op({"x": 3, "y": 2})
        assert op({"x": 1, "y": 1})

    def test_lt_operator(self):
        lhs = R("x")
        rhs = R("y")
        op = Lt(lhs, rhs)
        assert op({"x": 1, "y": 2})
        assert not op({"x": 3, "y": 2})
        assert not op({"x": 1, "y": 1})

    def test_gte_operator(self):
        lhs = R("x")
        rhs = R("y")
        op = Gte(lhs, rhs)
        assert not op({"x": 1, "y": 2})
        assert op({"x": 3, "y": 2})
        assert op({"x": 1, "y": 1})

    def test_gt_operator(self):
        lhs = R("x")
        rhs = R("y")
        op = Gt(lhs, rhs)
        assert not op({"x": 1, "y": 2})
        assert op({"x": 3, "y": 2})
        assert not op({"x": 1, "y": 1})

    def test_eq_operator(self):
        lhs = R("x")
        rhs = R("y")
        op = Eq(lhs, rhs)
        assert not op({"x": 1, "y": 2})
        assert not op({"x": 2, "y": 1})
        assert op({"x": 1, "y": 1})

    def test_neq_operator(self):
        lhs = R("x")
        rhs = R("y")
        op = NotEq(lhs, rhs)
        assert op({"x": 1, "y": 2})
        assert op({"x": 2, "y": 1})
        assert not op({"x": 1, "y": 1})
