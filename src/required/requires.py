# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import six
import itertools

from copy import deepcopy
from collections import defaultdict

from .expressions import RExpression, R, ResolveError
from .exceptions import RequirementError


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

    def __eq__(self, other):
        return (self.name == other.name and self.expression == other.expression
                and self.message == other.message)

    def __hash__(self):
        return hash(
            hash(self.name) + hash(self.expression) + hash(self.message))


class PartialDependency(object):
    def __init__(self, from_, keys=None):
        self._keys = keys or defaultdict(set)
        if isinstance(from_, RExpression):
            # partial on the from_ value
            from_names = from_.get_fields()
            assert len(from_names) == 1, "from_ must only contain one field"
            from_name = list(from_names)[0]
            self._keys[from_name].add(from_)

    def __add__(self, other):
        new_keys = defaultdict(set)
        for key, value in itertools.chain(self._keys.items(),
                                          other._keys.items()):
            new_keys[key] |= (value)
        return PartialDependency(None, new_keys)

    def __contains__(self, value):
        return value in self._keys

    def get(self, value):
        return self._keys[value]

    def __eq__(self, other):
        return self._keys == other._keys


class Requires(object):
    """
    """

    empty = empty

    def __init__(self, from_, dep, message=None):

        if isinstance(from_, six.string_types):
            from_ = R(from_)

        self.partials = PartialDependency(from_)
        self.adj = {
            self._hash(from_): self._get_dep_object(from_, dep, message)
        }

    def _hash(self, obj):
        return hash(obj)

    def _get_dep_object(self, from_, dep, message):
        if isinstance(dep, RExpression):
            # Complex dependency
            dep_names = dep.get_fields() - from_.get_fields()
            if len(dep_names) >= 1:
                return tuple(
                    Dependency(name=dep_name, expression=dep, message=message)
                    for dep_name in dep_names)
            # self expression depedency
            return (Dependency(
                name=list(from_.get_fields())[0],
                expression=dep,
                message=message), )
        # flat full dependency
        return (Dependency(name=dep, message=message), )

    def __add__(self, other):
        assert isinstance(other, Requires)
        combined = list(self.adj.items()) + list(other.adj.items())
        d = defaultdict(list)
        for key, value in combined:
            d[key].extend(list(value))
        partials = self.partials + other.partials

        new = deepcopy(self)
        new.adj = d
        new.partials = partials

        return new

    def deps(self, key, value, seen=None):
        # DFS of the dependency graph

        partial_key = (key, value) if key in self.partials else None

        # use of seen so we terminate and don't blow the stack
        seen = seen if seen else set()
        seen.add(partial_key or key)

        hash_key_lookup = self._hash(R(key))

        if hash_key_lookup not in self.adj and partial_key is None:
            # key has no dependencies or partial dependencies
            return []

        rels = self.adj.get(hash_key_lookup, list())

        if partial_key:
            # We need to resolve the partial dependency
            # to see if it is valid.
            lookup = dict((partial_key, ))
            partial_rels = []
            for exp in self.partials.get(key):
                if exp(lookup):
                    hash_exp_lookup = self._hash(exp)
                    dependencies_from_partial = self.adj.get(hash_exp_lookup)
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
                    field, dependency_name, None,
                    "%s requires '%s' to be present" % (field,
                                                        dependency_name))

            if dependency_value is not self.empty:
                try:
                    if not dependency_value(data):
                        error_message = dependency.get_error_message(
                        ) or dependency_value.error(field, dependency_name,
                                                    data)
                        raise RequirementError(field, dependency_name,
                                               dependency_value, error_message)
                except ResolveError as e:
                    raise RequirementError(
                        field, dependency_name, None,
                        "%s requires '%s' to be present" % (field,
                                                            e.missing_field))

    def validate(self, data):
        for key in data.keys():
            self._validate(key, data)

    def __eq__(self, other):
        return (self.adj == other.adj and self.partials == other.partials)
