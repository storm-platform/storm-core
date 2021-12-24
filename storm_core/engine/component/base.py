# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


from abc import ABC
from typing import List


class BaseComponentExecutor(ABC):
    """Component executor base class.

    A component is a generic piece of software that can be
    used to extend a pre-defined behavior in classes and
    functions.

    This class defines a base component executor, a class
    with the capabilities to execute components.
    """

    config = None
    """Component Executor configuration property."""

    def __init__(self, methods: List[str]):
        """Initializer.

        Args:
            methods (List[str]): List with the name of ``methods`` used
            by the executor.
        """

        self._methods = methods

    @property
    def methods(self):
        """List all components method
        used by this executor."""
        return self._methods.copy()

    def run_components(self, **kwargs):
        """Execute the registered components.

        Args:
            kwargs: Arguments to the executed components.

        """
        results = {}
        for component_cls in self.config.components:

            component_obj = component_cls()
            for valid_method in self._methods:

                if hasattr(component_obj, valid_method):
                    component_result = getattr(component_obj, valid_method)(**kwargs)
                    results = {**results, **component_result}
        return results


__all__ = "BaseComponentExecutor"
