#
# This file is part of SpatioTemporal Open Research Manager Core.
# Copyright (C) 2021 INPE.
#
# SpatioTemporal Open Research Manager Core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from typing import Union
from pathlib import Path

from storm_hasher import StormHasher


def hash_file(file_path: Union[str, Path], algorithm: str = "md5"):
    hash_digest = StormHasher(algorithm).hash_file(file_path)

    return {
        "key": file_path,
        "algorithm": algorithm,
        "checksum": hash_digest
    }


def check_checksum(file_path: Union[str, Path], expected_checksum, algorithm: str = "md5"):
    file_hash_digest = hash_file(file_path, algorithm).get("checksum")

    if expected_checksum != file_hash_digest:
        raise RuntimeError(f"Invalid checksum for {file_path}!")


__all__ = (
    "hash_file",
    "check_checksum"
)
