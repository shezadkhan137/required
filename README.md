# required: A easy to use DSL for validation

[![PyPI](https://img.shields.io/pypi/v/required.svg)]()
[![Build Status](https://travis-ci.org/shezadkhan137/required.svg?branch=master)](https://travis-ci.org/shezadkhan137/required)
[![Coverage Status](https://coveralls.io/repos/github/shezadkhan137/required/badge.svg?branch=master)](https://coveralls.io/github/shezadkhan137/required?branch=master)

Required is a simple library which allows you to validate dependencies
across multiple fields. The goal is to make writing things like forms, seralizers and functions much easier by providing a declarative way to encode validation logic. It aims to:

-  Have a declarative way to encode validation logic
-  Allow you to maintain validation logic easily
-  Allow you to reuse your validation logic easily
-  Be flexible with what you want to validate

If this all sounds good. Read On!

## Installation 

Install using `pip`

```
pip install required
```

## Quickstart

You can use required in a number of ways. The easiest way is to use the `validate` decorator to validate inputs to function calls. 

```python
from required import validate

@validate
def calculate_sum(positive_number, negative_number):
    """
    positive_number -> positive_number > 0
    negative_number -> negative_number < 0
    """
    return positive_number + negative_number
    
# the following will raise a validation exception
calculate_sum(1, 1)

# this will pass validation
calculate_sum(1, -1) # 0
```

If you want to have other information in the docstring, the validation rules can be wrapped inside of `Requires { }` as shown below:

```python

@validate
def calculate_sum(positive_number, negative_number):
    """
    Other documentation relating to calculate_sum
    
    Requires {
        positive_number -> positive_number > 0
        negative_number -> negative_number < 0
    }
    
    You can also put information after the requires rules
    """
    return positive_number + negative_number
```

Validation rules are written in the doc string of the function. They look like: 

`[param] -> [expression_1] [comparator] [expression_2]`

When `param` is present, it requires `expression_1 [comparator] expression_2` to evaluate to true. 

The most simple expressions are just variables passed into the function to validate, however they can be more complex. See cookbook for more examples.

The comparator can be one of the standard python comparator operations; `==`, `!=`, `in`, `>=` `<=`, `>`, `<`.



## Cookbook

The following shows some examples for writing validation rules

```

# Arithmetic on the objects follow normal maths rules.
# you need to put brackets to define expressions
x -> (x + 1) < 1
x -> (x - y) == 1

# A value `x` needs to be in an array
x -> x in arr

# The length of x must be 10
# see section on registering functions
x -> len(x) == 10

# The length of x and y must be the same
x -> len(x) == len(y)

# when x is present y must not be present
# TODO: not implemented in DSL yet
x -> x == <empty>

# x must be equal to the return value of a function
x -> x == func(x)

# Partial dependencies can be also specified

# when x == 1 then y must be 2
x == 1 -> y == 2

# when x == 1 then y must be set
x == 1 -> y
```

## Registering callables

You can register callables into the validation scope. This is useful when you want to call normal python builtins or custom callables. 

```python
from required import validate

scoped_validate = validate.register_callables({
 "len": len,
 "abs": abs
})

@scoped_validate
def return_first_element(arr):
    """
    arr -> len(arr) >= 1
    """
    return arr[0]


# validation scoped callables can also be nested
# len, abs and my_func are available in the second_scoped_validate decorator

second_scoped_validate = scoped_validate.register_callables({
    "my_func": my_func
})

# or inserted at function level
@validate(callables_dict={"new_func": new_func})
def other_function(var):
    """
    var -> new_func(var) >= 1
    """
    return var
```


## Contributing 

If you want to contribute you are most welcome! This project is distributed under the [MIT](https://choosealicense.com/licenses/mit/) licence. It is tested using [tox](https://pypi.python.org/pypi/tox) against Python 2.7 and 3.4+
