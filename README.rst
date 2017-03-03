required: A Easy Dependency Validator
=====================================

|PyPI| |Build Status| |Coverage Status|

``required`` is a simple Python package which allows you to validate
function argument dependencies in situations where there are a large
number of optional parameters. Places where you may have this are:

-  In a API where you may have a number of optional query parameters,
   that are only valid under some permutations
-  Functions which receive \*\*kwargs but need to validate that it is
   correct

Installation
------------

Install using ``pip``

::

    pip install required

Examples
--------

Basic Dependencies
~~~~~~~~~~~~~~~~~~

Say you have a function which takes two optional arguments, however, the
first one ``x`` is only valid when ``y`` has been passed. You could
eaily express this with:

.. code:: python

    from required import Requires, R, validate

    x_requires_y = Requires("x", "y")
    @validate(x_requires_y)
    def fn1(x=None, y=None):
        return x,y

    fn1(x=1)  # RequirementError: x requires 'y' to be present
    fn1(x=1, y=1)  # (1,1)

Expression Dependencies
~~~~~~~~~~~~~~~~~~~~~~~

Thats a contrived example you say?! Ok, something a little bit more
complex. You have a function which takes two arguments ``v`` and ``w``,
but ``v`` is only valid when the value of ``v`` is less than ``w``.

.. code:: python

    v_less_than_w = Requires("v", R("v") <= R("w"))

    @validate(v_less_than_w)
    def fn2(v, w):
       return v,w

    fn2(v=3, w=2)  # RequirementError: x requires x to be less than or equal to y
    fn2(v=1, w=2)  # (1,2)

Combined Dependencies
~~~~~~~~~~~~~~~~~~~~~

Yes, but what if I have more than one constraint I hear you say? Well,
yes, thats ok too. Imagine a function which takes ``x``, ``y``,\ ``z``.
``x`` requires ``y`` to be greater than ``x`` and ``z`` requires ``y``
to be less than ``z``

.. code:: python


    x_less_than_y = Requires("x", R("y") >= R("x"))
    y_less_than_z = Requires("z", R("y") <= R("z"))

    @validate(x_less_than_y + y_less_than_z)
    def fn3(x,y,z):
        return x,y,z

    fn3(x=1, y=2, z=1)  # RequirementError: z requires y to be less than or equal to z
    fn3(x=1, y=2, z=3)  # (1,2,3)

Arithmetic with R objects
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    y_must_be_zero = Requires("x", R("y") + R("x") == R("x"))
    @validate(y_must_be_zero)
    def fn4(x,y):
        return x,y

    fn4(x=1, y=2)  # RequirementError
    fn4(x=1, y=0)  # (0, 1)

Caveats
-------

-  The validation is done through dictionary types. Therefore all
   parameters to your function must be passed as \*\*kwargs, \*args are
   unchecked.
-  Currently this is still in the early stages and so most likely have
   bugs. YMMV
-  Only a limited number of expressions are currently supported
-  Only simple comparison operations are supported

TODO
----

-  Add more expression operators
-  Add support for more complex expressions

.. |PyPI| image:: https://img.shields.io/pypi/v/required.svg
   :target: https://pypi.python.org/pypi/required
.. |Build Status| image:: https://travis-ci.org/shezadkhan137/required.svg?branch=master
   :target: https://travis-ci.org/shezadkhan137/required
.. |Coverage Status| image:: https://coveralls.io/repos/github/shezadkhan137/required/badge.svg?branch=master
   :target: https://coveralls.io/github/shezadkhan137/required?branch=master
