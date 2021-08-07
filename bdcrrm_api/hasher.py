#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Multihash functions."""

import hashlib
from pathlib import Path
from typing import Union

import multihash as _multihash


def checksum_string_or_list(string_or_list: str):
    """Generate a checksum from a string or list of strings."""
    if isinstance(string_or_list, list):
        string_or_list = "".join(string_or_list)

    # sorting
    string = "".join(sorted(string_or_list))

    return hashlib.sha256((''.join(sorted(string))).encode('utf-8')).digest()


def checksum_file(file_path: Union[str, Path], chunk_size=16384) -> bytes:
    """Read a file and generate a checksum using `sha256`.

    Args:
        file_path (str|Path): Path to the file

        chunk_size (int): Size in bytes to read per iteration. Default is 16384 (16KB).

    Returns:
        The digest value in bytes.

    Raises:
        IOError when could not open given file.

    Note:
        This code is adapted from: https://github.com/brazil-data-cube/bdc-catalog
    """
    algorithm = hashlib.sha256()

    def _read(stream):
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            algorithm.update(chunk)

    with open(str(file_path), "rb") as f:
        _read(f)

    return algorithm.digest()


def multihash_checksum_sha256(data: Union[str, list, Path]):
    """Generate the checksum multihash.

    This method follows the spec `multihash <https://github.com/multiformats/multihash>`_.
    We use `sha256` as described in ``check_sum``. The multihash spec defines the code `0x12` for `sha256` and
    must have `0x20` (32 chars) length.
    See more in https://github.com/multiformats/py-multihash/blob/master/multihash/constants.py#L4

    Args:
        data Union[str, list, Path]: Path to the file

    Returns:
        A string-like hash in hex-decimal

    Note:
        This code is adapted from: https://github.com/brazil-data-cube/bdc-catalog
    """
    sha256 = 0x12
    sha256_length = 0x20

    if isinstance(data, str) or isinstance(data, list):
        digest = checksum_string_or_list(data)
    elif isinstance(data, Path):
        digest = checksum_file(data)

    _hash = _multihash.encode(digest=digest, code=sha256, length=sha256_length)

    return _multihash.to_hex_string(_hash)


__all__ = (
    "multihash_checksum_sha256"
)
