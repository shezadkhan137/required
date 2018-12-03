# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import six
import operator

from .exceptions import ResolveError


class RExpression(object):
    def error(self, key, key_dep, data):
        raise NotImplementedError

    def get_fields(self):
        raise NotImplementedError

    def _resolve(self, val, data):
        if isinstance(val, R):
            return val._resolve(data)
        if isinstance(val, RExpression):
            return val(data)
        return val

    def __hash__(self):
        raise NotImplementedError

    def __eq__(self, other):
        return hash(self) == hash(other)


class In(RExpression):
    def __init__(self, field, values):
        self.field = field
        self.values = values

    def __call__(self, data):
        field = self._resolve(self.field, data)
        values = self._resolve(self.values, data)
        if isinstance(field, list) or isinstance(field, tuple):
            return not set(field).isdisjoint(set(values))
        return field in values

    def get_fields(self):
        fields = set()
        for item in (self.field, self.values):
            if isinstance(item, R):
                for field in item.get_fields():
                    fields.add(field)
        return fields

    def error(self, key, dep_key, data):
        dep = self.field.field if isinstance(self.field, R) else self.field
        values = self._resolve(self.values, data)
        if len(values) == 1:
            return "{key} requires {dep} to be {values}".format(
                key=key, dep=dep, values=" or ".join(map(str, values)))
        return "{key} requires {dep} to be either {values}".format(
            key=key, dep=dep, values=" or ".join(map(str, values)))

    def __hash__(self):
        if isinstance(self.values, R):
            return hash(hash(self.field) + hash(self.values))
        return hash(hash(self.field) + sum(map(hash, self.values)))


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
        dep = self.lhs.error() if isinstance(self.lhs, R) else self.lhs
        value = self.rhs.error() if isinstance(self.rhs, R) else self.rhs
        return self.error_msg.format(key=key, dep=dep, value=value)

    def get_fields(self):
        fields = set()
        for item in (self.lhs, self.rhs):
            if isinstance(item, R):
                for field in item.get_fields():
                    fields.add(field)
        return fields

    def __hash__(self):
        return hash(self.lhs) + hash(self.rhs) + hash(self.get_operator())

    def __and__(self, other):
        return And(self, other)

    def __or__(self, other):
        return Or(self, other)


class And(GenericOp):

    @staticmethod
    def op(lhs_value, rhs_value):
        return lhs_value and rhs_value

    error_msg = "{key} requires {dep} and {value} to be true"


class Or(GenericOp):

    @staticmethod
    def op(lhs_value, rhs_value):
        return lhs_value or rhs_value

    error_msg = "{key} requires {dep} or {value} to be true"


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
    op = operator.gt
    error_msg = "{key} requires {dep} to be greater than {value}"


class NotEq(GenericOp):
    op = operator.ne
    error_msg = "{key} requires {dep} not be {value}"


class R(object):
    def __init__(self, field):
        self.field = field

    def get_fields(self):
        if isinstance(self.field, FieldOp):
            return self.field.get_fields()
        return {self.field}

    def error(self):
        if isinstance(self.field, FieldOp):
            return "({error})".format(error=self.field.error())
        return self.field

    def _resolve(self, data):
        try:
            if isinstance(self.field, FieldOp):
                return self.field._resolve(data)
            return data[self.field]
        except KeyError:
            raise ResolveError(self.field,
                               'missing key %s in data' % self.field)

    def in_(self, *container):
        return In(self, *container)

    def __le__(self, other):
        return Lte(self, other)

    def __lt__(self, other):
        return Lt(self, other)

    def __ge__(self, other):
        return Gte(self, other)

    def __gt__(self, other):
        return Gt(self, other)

    def __eq__(self, other):
        return Eq(self, other)

    def __ne__(self, other):
        return NotEq(self, other)

    # Arithmetic operators

    def __add__(self, other):
        fieldop = FieldOp(operator.add, self, other)
        return R(fieldop)

    def __sub__(self, other):
        fieldop = FieldOp(operator.sub, self, other)
        return R(fieldop)

    def __mul__(self, other):
        fieldop = FieldOp(operator.mul, self, other)
        return R(fieldop)

    def __div__(self, other):
        fieldop = FieldOp(operator.div, self, other)
        return R(fieldop)

    def __truediv__(self, other):
        fieldop = FieldOp(operator.truediv, self, other)
        return R(fieldop)

    def __pow__(self, other):
        fieldop = FieldOp(operator.pow, self, other)
        return R(fieldop)

    def length(self):
        fieldop = FieldOp(len, self)
        return R(fieldop)

    def __hash__(self):
        return hash(self.field)


class FieldOp(object):

    div_op = operator.div if six.PY2 else operator.truediv

    OP_LOOKUP = {
        operator.add: "+",
        operator.sub: "-",
        operator.mul: "*",
        operator.pow: "**",
        div_op: "/",
    }

    def __init__(self, operator, *args, **kwargs):
        self.operator = operator
        self.args = args
        self.kwargs = kwargs

    def get_fields(self):
        fields = set()
        for arg in self.args:
            if isinstance(arg, R):
                for field in arg.get_fields():
                    fields.add(field)
        return fields

    def _resolve_arg(self, arg, data):
        if isinstance(arg, R):
            return arg._resolve(data)
        return arg

    def _resolve(self, data):
        resolved_args = tuple(
            (self._resolve_arg(arg, data) for arg in self.args))
        resolved_kwargs = {
            key: self._resolve_arg(value, data)
            for key, value in self.kwargs.items()
        }
        return self.operator(*resolved_args, **resolved_kwargs)

    def error(self):
        if len(self.args) == 2:
            lhs = self.args[0]
            rhs = self.args[1]
            lhs_error = lhs.error() if isinstance(lhs, R) else lhs
            rhs_error = rhs.error() if isinstance(rhs, R) else rhs
            return "{lhs} {op} {rhs}".format(
                lhs=lhs_error,
                op=self.OP_LOOKUP.get(self.operator, "<op>"),
                rhs=rhs_error,
            )

        arg_errors = map(self.resolve_error, self.args)
        return "{op}({args})".format(
            op=self.OP_LOOKUP.get(self.operator, self.operator.__name__),
            args=",".join(arg_errors),
        )

    def resolve_error(self, arg):
        return arg.error() if isinstance(arg, R) else arg

    def __hash__(self):
        return hash(self.operator) + sum(map(hash, self.args))


def Func(func, *args, **kwargs):
    return R(FieldOp(func, *args, **kwargs))
