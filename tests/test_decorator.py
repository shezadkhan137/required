# -*- coding: utf-8 -*-
import pytest

from functools import partial

from required import (
    Requires, R,
    RequirementError, validate,
    init_parser, init_transformer,
    DecoratorError,
)


class TestDecorator(object):
    def test_required_decorator_works_when_called_with_kwargs(self):
        requires = Requires("x", R("x") > R("y"))

        @validate(requires)
        def somefunction(x, y):
            return x, y

        with pytest.raises(RequirementError):
            somefunction(x=1, y=2)

        somefunction(x=2, y=1)

    def test_required_decorator_works_when_called_with_args(self):
        requires = Requires("x", R("x") > R("y"))

        @validate(requires)
        def somefunction(x, y):
            return x, y

        with pytest.raises(RequirementError):
            somefunction(0, 2)

        somefunction(x=2, y=0)

    def test_required_decorator_works_when_called_with_args_kwargs(self):
        requires = Requires("x", R("x") > R("y"))

        @validate(requires)
        def somefunction(x, y):
            return x, y

        with pytest.raises(RequirementError):
            somefunction(10, y=20)

        somefunction(20, y=10)

    def test_required_decorator_works_when_called_with_star(self):
        requires = Requires("x", R("x") > R("y"))

        @validate(requires)
        def somefunction(x, y):
            return x, y

        with pytest.raises(RequirementError):
            somefunction(*(11, 21))

        with pytest.raises(RequirementError):
            somefunction(11 * (21, ))

        somefunction(*(21, 11))

    def test_required_decorator_works_with_defaults(self):
        requires = Requires("x", R("x") > R("y"))

        @validate(requires)
        def somefunction(x=1, y=2):
            return x, y

        with pytest.raises(RequirementError):
            somefunction()

        somefunction(y=0)
        somefunction(x=3)

    def test_required_decorator_with_docstring(self):
        @validate
        def somefunction(x=1, y=2):
            """
            x -> x > y
            """
            return x, y

        with pytest.raises(RequirementError):
            somefunction()

        somefunction(y=0)
        somefunction(x=3)

    def test_required_decorator_with_docstring_partial(self):
        @validate
        def somefunction(x, y):
            """
            x == 1 -> x == y;
            x > 1 -> x > y
            """
            return x, y

        with pytest.raises(RequirementError):
            somefunction(1, 2)

        with pytest.raises(RequirementError):
            somefunction(2, 2)

        somefunction(1, 1)
        somefunction(2, 1)

    def test_required_decorator_with_docstring_and_other_content(self):
        @validate
        def somefunction(variable_one, variable_two):
            """
            This is a doc string with other content
            before the requires

            Requires {
                variable_one == 1 -> variable_one == variable_two;
                variable_one > 1 -> variable_one > variable_two;
            }

            this is content after the requires.
            """
            return variable_one, variable_two

        with pytest.raises(RequirementError):
            somefunction(1, 2)

        with pytest.raises(RequirementError):
            somefunction(2, 2)

        somefunction(1, 1)
        somefunction(2, 1)

    def test_required_decorator_with_single_variable_custom_function(self):

        custom_validate = validate.register_callables({
            "onefunc": lambda x: x,
            "twofunc": lambda x: x,
        })

        @custom_validate
        def somefunction(variable_one, variable_two):
            """
            onefunc(variable_one) == 1 -> twofunc(variable_two) == 1;
            """
            return variable_one, variable_two

        with pytest.raises(RequirementError):
            somefunction(1, 2)

        somefunction(1, 1)

    def test_required_decorator_with_multi_variable_custom_function(self):

        custom_validate = validate.register_callables({
            "onefunc": lambda x, y: x,
        })

        @custom_validate
        def somefunction(variable_one, variable_two):
            """
            onefunc(variable_one, 1) == 1 -> onefunc(variable_two,1) == 1;
            """
            return variable_one, variable_two

        with pytest.raises(RequirementError):
            somefunction(1, 2)

        somefunction(1, 1)

    def test_required_decorator_with_function_scope_inheritance(self):

        custom_validate_outer = validate.register_callables({
            "outfunc": lambda x, y: x,
        })

        custom_validate_inner = custom_validate_outer.register_callables({
            "innerfunc": lambda x, y: y,
        })

        @custom_validate_inner
        def somefunction(variable_one, variable_two):
            """
            outfunc(variable_one, 1) == 1 -> innerfunc(1, variable_two) == 1;
            """
            return variable_one, variable_two

        with pytest.raises(RequirementError):
            somefunction(1, 2)

        with pytest.raises(RequirementError):
            somefunction(1, -1)

        assert somefunction(1, 1) == (1, 1)

    def test_required_decorator_with_function_override_inheritance(self):

        custom_validate_outer = validate.register_callables({
            "outfunc": lambda x, y: x,
        })

        @custom_validate_outer(callables_dict={
            "innerfunc": lambda x, y: y,
        })
        def somefunction(variable_one, variable_two):
            """
            outfunc(variable_one, 1) == 1 -> innerfunc(1, variable_two) == 1;
            """
            return variable_one, variable_two

        with pytest.raises(RequirementError):
            somefunction(1, 2)

        with pytest.raises(RequirementError):
            somefunction(1, -1)

        assert somefunction(1, 1) == (1, 1)

    def test_required_decorator_no_docstring_raises_exception(self):

        with pytest.raises(DecoratorError):

            @validate
            def somefunction(variable_one, variable_two):
                return variable_one, variable_two

    def test_required_decorator_called_directly(self):

        with pytest.raises(DecoratorError):
            validate()
