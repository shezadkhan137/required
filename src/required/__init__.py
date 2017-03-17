from __future__ import absolute_import, division, print_function

from .requires import Requires, RequirementError, validate
from .expressions import R

__version__ = "0.2.2"

__title__ = "required"
__description__ = "A easy dependency validator"
__uri__ = "https://github.com/shezadkhan137/required"
__doc__ = __description__ + " <" + __uri__ + ">"

__author__ = "Shezad Khan"
__email__ = "shezadkhan137@gmail.com"

__license__ = "MIT"
__copyright__ = "Copyright (c) 2017 Shezad Khan"

__all__ = [
    "Requires",
    "RequirementError",
    "R",
    "validate"
]
