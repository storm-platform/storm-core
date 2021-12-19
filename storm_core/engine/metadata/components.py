# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from typing import Dict
from abc import ABC, abstractmethod

from ...helper.hasher import hash_file
from ...reprozip import reprozip_execution_metadata


class MetadataComponent(ABC):
    @abstractmethod
    def do_metadata(self, execution_compendium_path: str, **kwargs) -> Dict:
        pass


class IOMetadataComponent(MetadataComponent):
    def do_metadata(self, execution_compendium_path: str, **kwargs) -> Dict:
        ignored_files = kwargs.get("ignored_objects")
        working_directory = kwargs.get("working_directory")

        return reprozip_execution_metadata(
            execution_compendium_path, working_directory, ignored_files
        )


class FileChecksumMetadataComponent(MetadataComponent):
    def do_metadata(self, execution_compendium_path: str, **kwargs) -> Dict:

        hasher_algorithm = kwargs.get("algorithm_checksum_files")

        ignored_files = kwargs.get("ignored_objects")
        working_directory = kwargs.get("working_directory")

        package_metadata = reprozip_execution_metadata(
            execution_compendium_path, working_directory, ignored_files
        )

        result = {"inputs": [], "outputs": []}
        for file_type in result.keys():
            for file in package_metadata[file_type]:
                result[file_type].append(hash_file(file, hasher_algorithm))

        return result


__all__ = (
    "MetadataComponent",
    "IOMetadataComponent",
    "FileChecksumMetadataComponent",
)
