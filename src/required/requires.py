# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from copy import deepcopy
from collections import defaultdict
from functools import wraps

from .expressions import RExpression


class Empty(object):
    def __repr__(self):
        return "<empty>"


class Requires(object):
    """
    """

    empty = Empty()

    def __init__(self, from_, dep):
        # process from_ partial
        self._from_keys = set()
        if isinstance(from_, RExpression):
            # partial on the from_ value
            from_names = from_.get_fields()
            assert len(from_names) == 1, "from_ must only contain one field"
            from_name = list(from_names)[0]
            self._from_keys.add(from_name)

        if isinstance(dep, RExpression):
            # Complex dependency
            dep_names = dep.get_fields() - {from_}
            assert len(dep_names) <= 1, "Currently do not support complex dependencies in expressions"
            if len(dep_names) == 1:
                dep_name = list(dep_names)[0]
                self.adj = {from_: ((dep_name, dep),)}
                return

        # Full dependency or self ref
        self.adj = {from_: (dep,)}

    def __add__(self, other):
        assert isinstance(other, Requires)
        combined = list(self.adj.items()) + list(other.adj.items())
        d = defaultdict(list)
        for key, value in combined:
            d[key].extend(list(value))
        self._from_keys = self._from_keys.union(other._from_keys)
        new = deepcopy(self)
        new.adj = d
        return new

    def deps(self, key, value, seen=None):
        # DFS of the dependency graph

        partial_key = (key, value) if key in self._from_keys else None

        # use of seen so we terminate and don't blow the stack
        seen = seen if seen else set()
        seen.add(partial_key or key)

        if key not in self.adj and partial_key is None:
            # key has no dependencies or partial dependencies
            return []

        rels = self.adj.get(key, list())

        if partial_key:
            # We need to resolve the partial dependency
            # to see if it is valid.
            lookup = dict((partial_key,))
            partial_rels = []
            for exp in self.adj.keys():
                if isinstance(exp, RExpression):
                    if exp(lookup):
                        dependencies_from_partial = self.adj.get(exp)
                        for dep in dependencies_from_partial:
                            partial_rels.append(dep)
            rels.extend(partial_rels)

        deps = []
        for dep in rels:
            if dep not in seen:
                deps.append(dep)
                child_deps = self.deps(dep, value, seen)
                deps.extend(child_deps)
        return deps

    def _validate(self, key, data):
        for dep_key in self.deps(key, data.get(key, self.empty)):
            if isinstance(dep_key, tuple):
                dep_key, dep_value = dep_key
            elif isinstance(dep_key, RExpression):
                dep_key, dep_value = key, dep_key
            else:
                dep_value = self.empty
            if dep_key not in data:
                raise RequirementError("%s requires '%s' to be present" % (key, dep_key))
            if dep_value is not self.empty:
                if not dep_value(data):
                    raise RequirementError(dep_value.error(key, dep_key, data))

    def validate(self, data):
        for key in data.keys():
            self._validate(key, data)


class RequirementError(Exception):
    pass

def validate(requires):
    def validate_decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            requires.validate(kwargs)
            return func(*args, **kwargs)
        return func_wrapper
    return validate_decorator
