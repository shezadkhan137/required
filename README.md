required: A Easy Dependency Validator 
=====================================

[![Build Status](https://travis-ci.org/shezadkhan137/required.svg?branch=master)](https://travis-ci.org/shezadkhan137/required)

`required` is a simple Python package which allows you to validate function argument dependencies in situations where there are a large number of optional parameters. Places where you may have this are:

* In a API where you may have a number of optional query parameters, that are only valid under some permutations 
* Functions which receive **kwargs but need to validate that it is correct 

Some examples to make it a bit more clear:

```python

>>> from required import Requires, R, validate
>>> @validate(Requires("x", "y"))
... def some_function(x=None, y=None):
...     pass

>>> some_function(x=1)
RequirementError: x requires 'y' to be present


>>> @validate(Requires("x", R("x") <= R("y")))
... def x_must_be_less_or_equals_to_y(x, y):
...     return x,y

>>> x_must_be_less_or_equals_to_y(x=3, y=2)
RequirementError: x requires x to be less than or equal to y


>>> @validate(Requires("x", R("y") >= R("x")) + Requires("z", R("y") <= R("z")))
... def z_must_be_gte_y_and_y_must_gte_x(x,y,z):
...     return x,y,z

>>> z_must_be_gte_y_and_y_must_gte_x(x=1, y=2, z=1)
RequirementError: z requires y to be less than or equal to z
```

### Caveats

* The validation is done through dictionary types. Therefore all parameters to your function
must be passed as **kwargs, *args are unchecked.

* Currently this is still in the early stages and so most likely have bugs. YMMV

* Only a limited number of expressions are currently supported

* Only simple comparison operations are supported

### TODO

* Add more expression operators

* Add support for more complex expressions

* Add tests for partial dependencies
