# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from typing import List, Union
from collections import Callable

from storm_hasher import StormHasher


class ExecutableCommand:
    def __init__(
        self,
        command: Union[str, List],
        split_fnc: Callable = lambda x: x.split(" "),
        checksum_algorithm="sha256",
    ):
        _cmd = command
        if isinstance(command, str):
            _cmd = split_fnc(command)

        # extracting the command parts
        self._command = _cmd
        self._command_executor = _cmd[0]
        self._command_arguments = _cmd[1:]

        self._split_fnc = split_fnc

        # calculating checksum
        self._checksum_algorithm = checksum_algorithm
        self._command_checksum = StormHasher(checksum_algorithm).hash_command(command)

    @property
    def command(self):
        return self._command

    @property
    def arguments(self):
        return self._command_arguments

    @property
    def checksum(self):
        return self._command_checksum

    @property
    def checksum_algorithm(self):
        return self._checksum_algorithm

    @property
    def binary_executor(self):
        return self._command_executor

    @property
    def split_function(self):
        return self._split_fnc

    def __str__(self):
        return " ".join(self._command)
