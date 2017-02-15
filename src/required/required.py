# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from copy import deepcopy
from collections import defaultdict

from .expression import RExpression


class Requires(object):
    """
    Helper class which provides a nice way to express
    argument dependencies. Made for our Search API but can be
    extended to anything which needs argument dependencies checking.

    Args:
        ...
        from_ (str, dict): from_ is the name of the argument which you want to express
                           the dependency for. If it is a string, it means that any value
                           of the argument requires the dependency. If it is a dict, it is
                           of the form '{argument: value}' where the dependency is only valid
                           if the the argument is equal to value. Value must be a hashable type.

        deps (tuple): Tuple passed in as *args of names of dependencies for the argument
        partial_deps: Dict passed in as **kwargs describes partial depenedencies where the
                      argument is valid only for those dependencies. dict key is the dependency
                      name and dict value is any callable which takes the argument value and
                      dependency value as params. See example for this to be more clear

    Example:

        rq = Requires("radius", "location") +
        Requires("location", entity=Any(ObjectType.VENUE, ObjectType.EVENT)) +
        Requires({"sort": "distance"}, entity=Any(ObjectType.EVENT, ObjectType.VENUE)) +

        Rq has a dependency graph which looks like:

                               +------------------+
                               |                  |
                               |       ENTITY     |
                           +--->  (Venue, Event)  <-----+
                           |   |                  |     |
                           |   +------------------+     |
                           |                            |
                          +----------+     +----------------+
                          |          |     |                |
                     +----> Location |     | SORT = distance|
                     |    |          |     |                |
                     |    +----------+     +----------------+
              +--------+
              |        |
              | Radius |
              |        |
              +--------+

        This is the same as:
            * Radius requires Location
            * Location requires entities of (Venue OR Event)
            * Sort=distance requires entities of (Venue OR Event)
    """

    class Empty(object):
        def __repr__(self):
            return "<empty>"

    empty = Empty()

    def __init__(self, from_, *deps):
        # process from_ partial
        self._from_keys = set()
        if isinstance(from_, dict):
            # partial on the from_ value
            assert len(from_) == 1, "from_ must be len 1"
            from_ = from_.items()[0]
            self._from_keys.add(from_[0])

        rexpressions = [dep for dep in deps if isinstance(dep, RExpression)]
        deps = [dep for dep in deps if not isinstance(dep, RExpression)]

        partial_deps = {}
        for rexpression in rexpressions:
            dep_names = rexpression.get_fields() - {from_}
            assert len(dep_names) == 1, "Currently do not support complex dependencies in expressions"
            dep_name = list(dep_names)[0]
            partial_deps[dep_name] = rexpression

        assert set(deps).isdisjoint(set(partial_deps.keys())), "Cannot have full dep and partial dep"
        self.adj = {from_: tuple(deps) + tuple(partial_deps.items())}

    def __add__(self, other):
        assert isinstance(other, Requires)
        combined = self.adj.items() + other.adj.items()
        d = defaultdict(list)
        for key, value in combined:
            d[key].extend(list(value))
        self._from_keys = self._from_keys.union(other._from_keys)
        new = deepcopy(self)
        new.adj = d
        return new

    def deps(self, key, value, seen=None):
        # DFS of the dependency graph
        # use of seen so we terminate and don't blow the stack
        seen = seen if seen else set()
        seen.add(key)
        rels = self.adj[key] + self.adj[(key, value)] if key in self._from_keys else self.adj[key]
        deps = []
        for dep in rels:
            if dep not in seen:
                deps.append(dep)
                child_deps = self.deps(dep, value, seen)
                deps.extend(child_deps)
        return deps

    def validate(self, key, data):
        for dep_key in self.deps(key, data[key]):
            if isinstance(dep_key, tuple):
                dep_key, dep_value = dep_key
            else:
                dep_value = self.empty
            if dep_key not in data:
                raise RequirementError("%s requires '%s' to be present" % (key, dep_key))
            if dep_value is not self.empty:
                if not dep_value(data):
                    raise RequirementError(dep_value.error(key, dep_key, data))


class RequirementError(Exception):
    pass
