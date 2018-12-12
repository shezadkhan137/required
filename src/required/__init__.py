from __future__ import absolute_import, division, print_function

from .requires import Requires, empty
from .expressions import R, Func
from .decorator import validate
from .dsl import init_parser, init_transformer, build_requirements_factory
from .exceptions import RequiredSyntaxError, RequirementError, ResolveError, DecoratorError

__version__ = "0.4.0"

__title__ = "required"
__description__ = "A easy dependency validator"
__uri__ = "https://github.com/shezadkhan137/required"
__doc__ = __description__ + " <" + __uri__ + ">"

__author__ = "Shezad Khan"
__email__ = "shezadkhan137@gmail.com"

__license__ = "MIT"
__copyright__ = "Copyright (c) 2018 Shezad Khan"

__all__ = [
    "Requires",
    "R",
    "Func",
    "empty",
    "validate",
    "build_requirements_factory",
    "init_parser",
    "init_transformer",
    "RequirementError",
    "RequiredSyntaxError",
    "ResolveError",
    "DecoratorError",
]
