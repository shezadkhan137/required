import pytest

from required import Requires, R, RequirementError


class TestRequires(object):

    def test_value_no_dependency_does_not_raise_error(self):
        requires = Requires("x", "y")
        data = {"x": 1}
        requires.validate("y", data)

    def test_exists_dependency_raises_requirements_error(self):
        requires = Requires("x", "y")
        data = {"x": 1}
        with pytest.raises(RequirementError):
            requires.validate("x", data)

    def test_triple_dependency_raises_correct_error(self):
        requires = Requires("x", "y") + Requires("y", "z")
        data = {"x": 1}

        with pytest.raises(RequirementError):
            requires.validate("x", data)

        with pytest.raises(RequirementError):
            requires.validate("y", data)

        requires.validate("z", data)

    def test_multiple_dependencies_requires_all(self):
        requires = Requires("x", "y") + Requires("x", "z")
        data = {"x": 1, "y": 2}

        with pytest.raises(RequirementError):
            requires.validate("x", data)

        data = {"x": 1, "z": 2}
        with pytest.raises(RequirementError):
            requires.validate("x", data)

        data = {"x": 1, "z": 2, "y": 2}
        requires.validate("x", data)

    def test_circular_dependency_requires_both(self):
        requires = Requires("x", "y") + Requires("y", "x")

        data = {"x": 1}
        with pytest.raises(RequirementError):
            requires.validate("x", data)

        data = {"y": 1}
        with pytest.raises(RequirementError):
            requires.validate("y", data)

        data = {"x": 1, "y": 2}
        requires.validate("y", data)
        requires.validate("x", data)
