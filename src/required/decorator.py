# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import six
import inspect

from .requires import Requires
from .dsl import build_requirements_factory as default_build_requirements_factory, init_transformer, init_parser
from .exceptions import DecoratorError


class Validate(object):

    def __init__(self, callables_dict=None, build_requirements_factory=None):
        self.callables_dict = callables_dict or {}
        self.build_requirements_factory = build_requirements_factory or default_build_requirements_factory
        self.requirements_builder = self.build_requirements_factory(
            init_parser(),
            init_transformer(callables_dict)
        )

    def _inherit_callables_dict(self, callables_dict):
        new_callables_dict = callables_dict.copy()
        new_callables_dict.update(self.callables_dict)
        return new_callables_dict

    def register_callables(self, callables_dict):
        return Validate(self._inherit_callables_dict(callables_dict), self.build_requirements_factory)

    def __call__(self, arg=None, callables_dict=None):

        if callables_dict is not None and arg is None:
            # called with validate(callable_dict=...)
            return self.register_callables(callables_dict)

        if arg is None:
            raise DecoratorError('Error, arg must be provided if callables_dict is None')

        if isinstance(arg, Requires):
            requires = arg
            func = None
        else:
            func = arg
            docstring = func.__doc__

            if not docstring:
                raise DecoratorError("If function doesn't have a docstring, you must pass a requires object explicitly")

            requirements_builder = None
            if callables_dict:
                requirements_builder = self.build_requirements_factory(
                    init_parser(),
                    init_transformer(self._inherit_callables_dict(callables_dict))
                )

            requirements_builder = requirements_builder or self.requirements_builder
            requires = requirements_builder(
                docstring,
            )

        def validate_decorator(func):
            if six.PY3:
                fullargspec = inspect.getfullargspec(func)
                inspected_args = fullargspec.args or ()
                inspected_defaults = fullargspec.defaults or ()
                inspected_kwonlyargs_defaults = fullargspec.kwonlydefaults or {}
            else:
                argspec = inspect.getargspec(func)
                inspected_args = argspec.args or ()
                inspected_defaults = argspec.defaults or ()
                inspected_kwonlyargs_defaults = {}

            @six.wraps(func)
            def func_wrapper(*args, **kwargs):
                args_as_dict = dict(zip(inspected_args, args + inspected_defaults))
                args_as_dict.update(inspected_kwonlyargs_defaults)
                args_as_dict.update(kwargs)
                requires.validate(args_as_dict)
                return func(*args, **kwargs)
            return func_wrapper

        return validate_decorator(func) if func is not None else validate_decorator


validate = Validate()
