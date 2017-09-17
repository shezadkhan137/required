# required: Easy multi-field validation

[![PyPI](https://img.shields.io/pypi/v/required.svg)]()
[![Build Status](https://travis-ci.org/shezadkhan137/required.svg?branch=master)](https://travis-ci.org/shezadkhan137/required)
[![Coverage Status](https://coveralls.io/repos/github/shezadkhan137/required/badge.svg?branch=master)](https://coveralls.io/github/shezadkhan137/required?branch=master)

Required is a simple libaray which allows you to validate dependencies
across multiple fields. The goal is to make writing things like Forms
and Seralizers much easier by providing a declariative way to encode
your complex validation logic.

Most Forms and Serializers limit you to doing validation on a single
field, and then have one single `clean` method where you can do
muti-field validation logic. The problem with this is that if you have a
large number of optional fields which depend on each other, your
validation code can quickly become unreadable, unmaintainable and
non-resuable.

The aim of Required is to do the following:

-  To have a declaritave way to encode validation logic
-  Allow you to maintain extreamly complex multi field valiation logic
-  Allow you to reuse your validation logic easily
-  Be flexible with what you want to validate

If this all sounds good. Read On!

## Installation 

Install using `pip`

```
pip install required
```

## Quickstart

Lets start with a quick example. 

You want to validate some business rules on some optional input paramaters (for example to a API endpoint or function). They are `start_date` and `end_date`.

The business rules:


*  `start_date`
   *  Only valid with `end_date`
   *  Must be after 2017
   *  Must be before 2018

*  `end_date` - filter events which start before this date

   *  Only valid with `start_date`
   *  Must be before 2018
   *  Must be after `start_date`

Theses rules can be written with `required` as follows:

```python
import datetime
from required import Requires, R

# start_date requirements
start_requires_end = Requires("start_date", "end_date")
start_after_2017 = Requires("start_date", R("start_date") > datetime.date(2017, 1, 1))
start_before_2018 = Requires("start_date", R("start_date") < datetime.date(2018, 1, 1))

# end_date requirements
end_requires_start = Requires("end_date", "start_date")
end_before_2018 = Requires("end_date", R("end_date") < datetime.date(2018, 1, 1))
end_after_start = Requires("end_date", R("end_date") > R("start_date"))
```

The above introduces the two important concepts of required; the `Requires` and `R` objects.

The `Requires` object is used to define pair-wise dependencies. It has two non-optional arguments, the first one is the target (key) of the constraint, and the second argument is the constraint itself. `Requires("start_date", "end_date")` means "start_date requires end_date to be present".

The `R` object acts as a placeholder for a future value. If you require a future value of `end_date` to be more than `start_date`, you would write it as `R("end_date") > R("start_date)`. Any such expression can be used as the constraint for the `Requires` object. 

The last step is simply summing all the  `Requires` together in order to combine the rules:

```python
# combine all the rules
all_rules = (
    start_requires_end + 
    start_after_2017 +
    start_before_2018 +
    end_requires_start +
    end_before_2018 +
    end_after_start
)
```

Once you have combined all the rules, you can simply call validate on the `all_rules` object with a dict of your data you want to validate.

```python
data = {
    "start_date": datetime.date(2017, 10, 10),
    "end_date": datetime.date(2017, 10, 9),
}

all_rules.validate(data)  
# RequirementError: end_date requires end_date to be greater than start_date
```

The above not only tells you that the data was invalid, but which rule it broke. The following correct data passes validation:

```python
data = {
    "start_date": datetime.date(2017, 10, 10),
    "end_date": datetime.date(2017, 10, 11),
}

all_rules.validate(data)  
```

## Cookbook

The following shows some recipes for forming validation rules with the `R` object.

```python
# Arithmetic on the `R` object follows normal maths rules.
R("x", R("x") + 1 < 1)
R("x", R("x") - R("y") == 1)

# A value `x` needs to be in an array
R("x", R("x").in_(array))

# The length of x must be 10
R("x", R("x").length() == 10)

# The length of x and y must be the same
R("x", R("x").length() == R("y").length())

# when x is present y must not be present
# from required import empty
R("x", R("y") == empty)

# x must be equal to the return value of a function
# this is useful if what you are checking is against
# is non-pure eg. current time

f = lambda x: 1
Requires("x", R("x") == Func(f, R("x")))

# the above can be used to ensure that a value is not in the past
R("start_date", R("start_date") > Func(datetime.now))

# Partial dependencies can be also specified with R objects

# x requires y when x is equal to 1
Requires(R("x") == 1, "y")
```

## Contributing 

If you want to contribute you are most welcome! This project is distributed under the [MIT](https://choosealicense.com/licenses/mit/) licence. It is tested using [tox](https://pypi.python.org/pypi/tox) against Python 2.7 and 3.4+
