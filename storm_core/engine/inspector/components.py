#
# This file is part of SpatioTemporal Open Research Manager Core.
# Copyright (C) 2021 INPE.
#
# SpatioTemporal Open Research Manager Core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from abc import ABC, abstractmethod

from ...reprozip import reprozip_remove_environment_variables, filter_reprozip_config_files


class InspectorComponent(ABC):

    @abstractmethod
    def inspect_data_files(self, execution_compendium_path: str, **kwargs):
        pass

    @abstractmethod
    def inspect_environment_variables(self, execution_compendium_path: str, **kwargs):
        pass


class InspectorFileRemoverComponent(InspectorComponent):

    def inspect_data_files(self, execution_compendium_path: str, **kwargs):
        previous_output = kwargs.get("previous_outputs")
        data_directories = kwargs.get("data_directories")

        files_not_packaged = filter_reprozip_config_files(execution_compendium_path, data_directories, previous_output)
        return {"unpacked_files": files_not_packaged}

    def inspect_environment_variables(self, execution_compendium_path: str, **kwargs):
        env_to_unpack = kwargs.get("environment_variables_to_remove")

        unpacked_env = reprozip_remove_environment_variables(execution_compendium_path, env_to_unpack)
        return {"unpacked_environment_variables": unpacked_env}


__all__ = (
    "InspectorFileRemoverComponent"
)
