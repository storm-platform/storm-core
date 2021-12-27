# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


from typing import Type

from functools import wraps
from .base import BaseComponentExecutor


def pass_component_executor(
    argname: str, component_executor_type: Type[BaseComponentExecutor]
):
    """Wrapper decorator function that inject a component executor
    instance.

    This decorator will check in the decorated function args if any
    instance of ``component_executor_type`` is present. If false,
    a new object of class ``component_executor_type`` will be created
    and inserted.

    Args:
        argname (str): Name of the argument to be searched in the kwargs.

        component_executor_type (Type[BaseComponentExecutor]): Component executor class.
    """

    def pass_instance(f):
        """Decorator to inject a valid ``component_executor_type`` object in the
        decorated function."""

        @wraps(f)
        def wrapper(*args, **kwargs):

            instance_founded = False
            for arg in args:
                if isinstance(arg, component_executor_type):
                    instance_founded = True

            if not instance_founded:
                instance_founded = argname in kwargs

            if instance_founded:
                return f(*args, **kwargs)

            _component_executor = component_executor_type()
            return f(*args, **{**kwargs, argname: _component_executor})

        return wrapper

    return pass_instance
