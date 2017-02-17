import pytest

from required import Requires, R, RequirementError


class TestRequires(object):

    def test_value_no_dependency_does_not_raise_error(self):
        requires = Requires("x", "y")
        data = {"x": 1}
        requires._validate("y", data)

    def test_exists_dependency_raises_requirements_error(self):
        requires = Requires("x", "y")
        data = {"x": 1}
        with pytest.raises(RequirementError):
            requires._validate("x", data)

    def test_triple_dependency_raises_correct_error(self):
        requires = Requires("x", "y") + Requires("y", "z")
        data = {"x": 1}

        with pytest.raises(RequirementError):
            requires._validate("x", data)

        with pytest.raises(RequirementError):
            requires._validate("y", data)

        requires._validate("z", data)

    def test_multiple_dependencies_requires_all(self):
        requires = Requires("x", "y") + Requires("x", "z")
        data = {"x": 1, "y": 2}

        with pytest.raises(RequirementError):
            requires._validate("x", data)

        data = {"x": 1, "z": 2}
        with pytest.raises(RequirementError):
            requires._validate("x", data)

        data = {"x": 1, "z": 2, "y": 2}
        requires._validate("x", data)

    def test_circular_dependency_requires_both(self):
        requires = Requires("x", "y") + Requires("y", "x")

        data = {"x": 1}
        with pytest.raises(RequirementError):
            requires._validate("x", data)

        data = {"y": 1}
        with pytest.raises(RequirementError):
            requires._validate("y", data)

        data = {"x": 1, "y": 2}
        requires._validate("y", data)
        requires._validate("x", data)

    def test_simple_expression_dependency_equal(self):
        requires = Requires("x", R("y") == 1)
        data = {"x": 1, "y": 2}
        with pytest.raises(RequirementError):
            requires._validate("x", data)

        data = {"x": 1, "y": 1}
        requires._validate("x", data)

    def test_simple_expression_dependency_greater_or_equal(self):
        requires = Requires("x", R("y") >= 1)
        data = {"x": 1, "y": 0}
        with pytest.raises(RequirementError):
            requires._validate("x", data)

        data = {"x": 1, "y": 1}
        requires._validate("x", data)

        data = {"x": 1, "y": 2}
        requires._validate("x", data)

        data = {"y": 2}
        requires._validate("y", data)

    def test_multi_expression_dependency_correctly_validates(self):
        requires = Requires("x", R("y") >= 1) + Requires("z", R("y") <= 1)

        data = {"x": 1, "y": 2, "z": 1}

        with pytest.raises(RequirementError):
            requires._validate("z", data)

        requires._validate("x", data)
        requires._validate("y", data)

        data = {"x": 1, "y": 1, "z": 1}
        requires._validate("z", data)

    def test_multi_r_in_expression_correctly_validates(self):
        requires = Requires("x", R("y") >= R("x")) + Requires("z", R("y") <= R("z"))

        data = {"x": 1, "y": 2, "z": 1}
        requires._validate("x", data)
        requires._validate("y", data)
        with pytest.raises(RequirementError):
            requires._validate("z", data)

        data = {"x": 1, "y": 2, "z": 3}
        requires.validate(data)
