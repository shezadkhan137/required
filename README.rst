required: A Easy Dependency Validator 
=====================================

.. image:: https://travis-ci.org/shezadkhan137/required.svg?branch=master
    :target: https://travis-ci.org/shezadkhan137/required


`required` is a simple Python package which allows you to validate function argument dependencies in situations where there are a large number of optional parameters. Places where you may have this are:

* In a API where you may have a number of optional query parameters, that are only valid under some permutations 
* Functions which received **kwargs but need to validate that it is correct 

Some examples to make it a bit more clear:

```python

from required import Requires, R, RequirementError, validate

@validate(Requires("x", "y"))
def some_function(x=None, y=None):
    pass
```
