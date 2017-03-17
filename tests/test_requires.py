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

    def test_hybrid_with_two_r_expressions_add(self):
        requires = Requires("x", R("y") + R("x") == 1)
        data = {"x": 1, "y": 0}
        requires.validate(data)

        data = {"x": 1, "y": 1}
        with pytest.raises(RequirementError):
            requires.validate(data)

    def test_hybrid_with_one_r_expression_add(self):
        requires = Requires("x", R("x") < R("y") + 1)
        data = {"x": 0.5, "y": 0}
        requires.validate(data)

        data = {"x": 1, "y": 1}
        requires.validate(data)

        data = {"x": 2, "y": 1}
        with pytest.raises(RequirementError):
            requires.validate(data)

    def test_hybrid_with_complex_add_both_sides(self):
        req = R("x") + 1 == R("y") + 2
        requires = Requires("x", req)
        data = {"x": 1, "y": 0}
        requires.validate(data)

        data = {"x": 1, "y": 1}
        with pytest.raises(RequirementError):
            requires.validate(data)

    def test_hybrid_with_complex_sub_both_sides(self):
        req = R("x") - R("y") == 0
        requires = Requires("x", req)
        data = {"x": 1, "y": 1}
        requires.validate(data)

        data = {"x": -1, "y": 1}
        with pytest.raises(RequirementError):
            requires.validate(data)

    def test_hybrid_with_complex_mul_both_sides(self):
        req = R("x") * 2 == R("y") * 4
        requires = Requires("x", req)
        data = {"x": 2, "y": 1}
        requires.validate(data)

        data = {"x": -1, "y": 1}
        with pytest.raises(RequirementError):
            requires.validate(data)

    def test_hybrid_with_complex_pow_both_sides(self):
        req = R("x") ** 2 == R("y") ** 4
        requires = Requires("x", req)
        data = {"x": 1, "y": 1}
        requires.validate(data)

        data = {"x": 2, "y": 1}
        with pytest.raises(RequirementError):
            requires.validate(data)

    def test_hybrid_with_complex_div_both_sides(self):
        req = R("x") == R("y") / 2
        requires = Requires("x", req)
        data = {"x": 4, "y": 8}
        requires.validate(data)

        data = {"x": 2, "y": 1}
        with pytest.raises(RequirementError):
            requires.validate(data)

    def test_r_in_method_checks_value_in_list(self):
        req = R("y").in_([1, 2])
        requires = Requires("x", req)
        data = {"x": 4, "y": 1}
        requires.validate(data)

        data = {"x": 2, "y": 10}
        with pytest.raises(RequirementError):
            requires.validate(data)

    def test_r_in_method_checks_value_in_single_list(self):
        req = R("y").in_([1])
        requires = Requires("x", req)
        data = {"x": 4, "y": 1}
        requires.validate(data)

        data = {"x": 2, "y": 10}
        with pytest.raises(RequirementError):
            requires.validate(data)

    def test_partial_dependency_simple_present(self):
        requires = Requires({"x": 1}, "y")
        data = {"x": 1}
        with pytest.raises(RequirementError):
            requires.validate(data)

        data = {"x": 1, "y": "hello"}
        requires.validate(data)

    def test_partial_dependency_simple_in(self):
        req = R("y").in_([1])
        requires = Requires({"x": 1}, req)
        data = {"x": 1}
        with pytest.raises(RequirementError):
            requires.validate(data)

        data = {"x": 1, "y": 2}
        with pytest.raises(RequirementError):
            requires.validate(data)

        data = {"x": 1, "y": 1}
        requires.validate(data)

    def test_multi_partial_dependency_simple_all_satisifed(self):
        requires = Requires({"x": 1}, "y") + Requires({"x": 2}, "z")

        data = {"x": 1}
        with pytest.raises(RequirementError):
            requires.validate(data)

        data = {"x": 1, "y": "hello"}
        requires.validate(data)

        data = {"x": 2, "y": "hello"}
        with pytest.raises(RequirementError):
            requires.validate(data)

        data = {"x": 2, "z": "hello"}
        requires.validate(data)

        data = {"x": 2}
        with pytest.raises(RequirementError):
            requires.validate(data)

        data = {"x": 2, "y": "hello"}
        with pytest.raises(RequirementError):
            requires.validate(data)

        data = {"x": 2, "z": "hello"}
        requires.validate(data)

    def test_simple_self_dependency(self):
        requires = Requires("x", R("x") > 1)
        data = {"x": 1}
        with pytest.raises(RequirementError):
            requires.validate(data)

        data = {"x": 2}
        requires.validate(data)
