# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from copy import deepcopy
from collections import defaultdict
from functools import wraps

from .expressions import RExpression


class Empty(object):
    def __repr__(self):
        return "<empty>"


empty = Empty()


class Dependency(object):
    def __init__(self, name, expression=None, message=None):
        self.name = name
        self.expression = expression
        self.message = message

    def get_key(self):
        return self.name

    def get_value(self):
        return self.expression or empty

    def get_error_message(self):
        return self.message


class Requires(object):
    """
    """

    empty = empty

    def __init__(self, from_, dep, message=None):
        # process from_ partial
        self._from_keys = set()
        from_name = self._get_from_name(from_)
        if from_name:
            self._from_keys.add(from_name)

        dep_obj = self._get_dep_object(from_, dep, message)
        self.adj = {from_: (dep_obj, )}

    def _get_from_name(self, from_):
        if isinstance(from_, RExpression):
            # partial on the from_ value
            from_names = from_.get_fields()
            assert len(from_names) == 1, "from_ must only contain one field"
            from_name = list(from_names)[0]
            return from_name
        return None

    def _get_dep_object(self, from_, dep, message):
        if isinstance(dep, RExpression):
            # Complex dependency
            dep_names = dep.get_fields() - {from_}
            assert len(dep_names) <= 1, "Currently do not support complex dependencies in expressions"
            if len(dep_names) == 1:
                dep_name = list(dep_names)[0]
                # expression dependecy
                return Dependency(name=dep_name, expression=dep, message=message)
            # self expression depedency
            return Dependency(name=from_, expression=dep, message=message)
        # flat full dependency
        return Dependency(name=dep, message=message)

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

    def _validate(self, field, data):
        for dependency in self.deps(field, data.get(field, self.empty)):

            dependency_name = dependency.get_key()
            dependency_value = dependency.get_value()

            if dependency_name not in data:
                raise RequirementError(
                    field,
                    dependency_name,
                    None,
                    "%s requires '%s' to be present" % (field, dependency_name)
                )

            if dependency_value is not self.empty:
                if not dependency_value(data):
                    error_message = dependency.get_error_message() or dependency_value.error(field, dependency_name, data)
                    raise RequirementError(
                        field,
                        dependency_name,
                        dependency_value,
                        error_message
                    )

    def validate(self, data):
        for key in data.keys():
            self._validate(key, data)


class RequirementError(Exception):

    def __init__(self, field=None, dependency_name=None, dependency_value=None, *args, **kwargs):
        super(RequirementError, self).__init__(*args, **kwargs)
        self.field = field
        self.dependency_name = dependency_name
        self.dependency_value = dependency_value


def validate(requires):
    def validate_decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            requires.validate(kwargs)
            return func(*args, **kwargs)
        return func_wrapper
    return validate_decorator
