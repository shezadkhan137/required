# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class BaseRequiredError(Exception):
    pass


class RequiredSyntaxError(BaseRequiredError):
    pass


class ResolveError(BaseRequiredError):
    def __init__(self, missing_field, *args, **kwargs):
        super(ResolveError, self).__init__(*args, **kwargs)
        self.missing_field = missing_field


class RequirementError(BaseRequiredError):
    def __init__(self,
                 field=None,
                 dependency_name=None,
                 dependency_value=None,
                 *args,
                 **kwargs):
        super(RequirementError, self).__init__(*args, **kwargs)
        self.field = field
        self.dependency_name = dependency_name
        self.dependency_value = dependency_value


class DecoratorError(BaseRequiredError):
    pass
