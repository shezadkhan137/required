# -*- coding: utf-8 -*-
import pytest

from required import Requires, R, RequirementError, validate


class TestPy3Requires(object):
    """
    Test py3 features
    """

    def test_required_decorator_works_with_keyword_only(self):
        requires = Requires("x", R("x") > R("y"))

        @validate(requires)
        def somefunction(*, x, y):
            return x, y

        with pytest.raises(RequirementError):
            somefunction(x=1, y=2)

        somefunction(x=2, y=1)

    def test_required_decorator_works_with_mixed_args_keyword_only(self):
        requires = Requires("x", R("x") > R("y"))

        @validate(requires)
        def somefunction(x, *, y):
            return x, y

        with pytest.raises(RequirementError):
            somefunction(1, y=2)

        somefunction(2, y=1)

    def test_required_decorator_works_with_keyword_only_with_defaults(self):
        requires = Requires("x", R("x") > R("y"))

        @validate(requires)
        def somefunction(*, x=0, y=0):
            return x, y

        with pytest.raises(RequirementError):
            somefunction()

        somefunction(x=2, y=1)
