# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import operator

from os import path
from six.moves import reduce

from lark import Lark, Transformer, v_args

from .requires import Requires
from .expressions import R, Func
from .exceptions import RequiredSyntaxError


def read_grammer_file(filename='grammer.lark'):
    basepath = path.dirname(__file__)
    grammer_filepath = path.abspath(path.join(basepath, filename))
    with open(grammer_filepath) as f:
        return f.read()


def init_parser():
    grammer = read_grammer_file()
    parser = Lark(grammer)
    return parser


@v_args(inline=True)
class TreeToRequiresTransformer(Transformer, object):

    def __init__(self, callables_dict, *args, **kwargs):
        super(TreeToRequiresTransformer, self).__init__(*args, **kwargs)
        self.function_whitelist_lookup = callables_dict

    def var_expression(self, var):
        return R(var.value)

    def number_expression(self, var):
        return float(var.value)

    def func_expression(self, func):
        return func

    def string_expression(self, var):
        return var.value.strip('"')

    def op_expression(self, lhs, op, rhs, *others):
        op_lookup = {
            "+": operator.add,
            "-": operator.sub,
            "*": operator.mul,
            "/": operator.truediv,
            "==": operator.eq,
        }
        r_op = op_lookup.get(op.value)
        if callable(r_op):
            return r_op(lhs, rhs, *others)
        return getattr(lhs, r_op)(rhs, *others)

    def arglist(self, *args):
        return args

    def func(self, func_name, arglist):
        try:
            func_resolved = self.function_whitelist_lookup[func_name.value]
        except KeyError:
            raise RequiredSyntaxError('disallowed function call %s' % func_name)
        return Func(func_resolved, *arglist)

    def expression_comparison(self, lhs_exp, comp_op, rhs_exp):
        op_lookup = {
            "==": operator.eq,
            ">": operator.gt,
            "<": operator.lt,
            ">=": operator.ge,
            "<=": operator.le,
            "!=": operator.ne,
            "in": "in_"
        }
        r_op = op_lookup.get(comp_op.value)
        if callable(r_op):
            return r_op(lhs_exp, rhs_exp)
        return getattr(lhs_exp, r_op)(rhs_exp)

    def var_comparison(self, var):
        return R(var.value)

    def rule(self, lhs, rhs):
        return Requires(lhs, rhs)

    def statement(self, *rules):
        return reduce(operator.add, rules)

    def start(self, *rules):
        return reduce(operator.add, rules)


def init_transformer(callables_dict):
    return TreeToRequiresTransformer(callables_dict)


def build_requirements_factory(parser, transformer):
    def inner(text):
        parse_tree = parser.parse(text)
        return transformer.transform(parse_tree)
    return inner


__all__ = [
    "build_requirements_factory",
    "init_parser",
    "init_transformer",
]
