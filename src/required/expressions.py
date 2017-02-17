# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import operator


class RExpression(object):

    def error(self, key, key_dep, data):
        raise NotImplementedError

    def get_fields(self):
        raise NotImplementedError

    def _resolve(self, val, data):
        if isinstance(val, R):
            return data.get(val.field, None)
        return val


class In(RExpression):

    def __init__(self, field, *values):
        self.field = field
        self.values = values

    def __call__(self, data):
        value = self._resolve(self.field, data)
        if isinstance(value, list) or isinstance(value, tuple):
            return not set(value).isdisjoint(set(self.values))
        return value in self.values

    def get_fields(self):
        return {
            item.field
            for item in (self.field, self.values)
            if isinstance(item, R)
        }

    def error(self, key, dep_key, data):
        dep = self.field.field if isinstance(self.field, R) else self.field
        if len(self.values) == 1:
            return "{key} requires {dep} to be {values}".format(
                key=key, dep=dep, values=" or ".join(self.values))
        return "{key} requires {dep} to be either {values}".format(
            key=key, dep=dep, values=" or ".join(self.values))


class GenericOp(RExpression):

    op = None
    error_msg = None

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def get_operator(self):
        return self.op

    def __call__(self, data):
        lhs_value = self._resolve(self.lhs, data)
        rhs_value = self._resolve(self.rhs, data)
        return self.get_operator()(lhs_value, rhs_value)

    def error(self, key, dep_key, data):
        dep = self.lhs.field if isinstance(self.lhs, R) else self.lhs
        value = self.rhs.field if isinstance(self.rhs, R) else self.rhs
        return self.error_msg.format(key=key, dep=dep, value=value)

    def get_fields(self):
        return {
            item.field
            for item in (self.lhs, self.rhs)
            if isinstance(item, R)
        }


class Lte(GenericOp):
    op = operator.le
    error_msg = "{key} requires {dep} to be less than or equal to {value}"


class Gte(GenericOp):
    op = operator.ge
    error_msg = "{key} requires {dep} to be greater than or equal to {value}"


class Eq(GenericOp):
    op = operator.eq
    error_msg = "{key} requires {dep} to be equal to {value}"


class Lt(GenericOp):
    op = operator.lt
    error_msg = "{key} requires {dep} to be less than {value}"


class Gt(GenericOp):
    op = operator.lt
    error_msg = "{key} requires {dep} to be greater than {value}"


class NotEq(GenericOp):
    op = operator.ne
    error_msg = "{key} requires {dep} not be {value}"


class R(object):

    def __init__(self, field):
        self.field = field

    def in_(self, *container):
        return In(self, *container)

    def __le__(self, other):
        return Lte(self, other)

    def __ge__(self, other):
        return Gte(self, other)

    def __eq__(self, other):
        return Eq(self, other)

    def __ne__(self, other):
        return NotEq(self, other)
