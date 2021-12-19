# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


from abc import ABC
from typing import List


class ComponentExecutor(ABC):
    def __init__(self, config, valid_component_methods: List[str]):
        self._config = config

        self._valid_component_methods = valid_component_methods

    @property
    def valid_component_methods(self):
        return self._valid_component_methods.copy()

    def run_components(self, execution_compendium_path: str, **kwargs):
        results = {}
        for component_cls in self._config.components:

            component_obj = component_cls()

            for valid_method in self._valid_component_methods:
                if hasattr(component_obj, valid_method):
                    component_result = getattr(component_obj, valid_method)(
                        execution_compendium_path, **kwargs
                    )

                    results = {**results, **component_result}
        return results


__all__ = "ComponentExecutor"
