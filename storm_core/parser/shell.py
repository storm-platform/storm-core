# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from igraph import Graph
from typing import List

from ..execution.job import CommandJob
from ..execution.plan import ExecutionPlan
from ..execution.command import ExecutableCommand


class ShellCommandParser:
    """Single Command Parser class.

    This class provides a helpful and straightforward way
    to parse single shell command (and its parameters) to
    a valid ``ExecutionPlan`` object instance.
    """

    @staticmethod
    def parse(command: List[str], **kwargs) -> ExecutionPlan:
        """Parse a single shell command to ExecutionPlan.

        Args:
            command (List[str]): Command in a list of strings (e.g., ['python3', 'script1.py']).

            kwargs: Extra parameters to the ``ExecutableCommand`` initializer.

        Returns:
            ExecutionPlan: ExecutionPlan instance.
        """
        g = Graph(directed=True)

        # creating the executable command
        command_executable = ExecutableCommand(command, **kwargs)
        command_job = CommandJob(command_executable)

        # adding the command into the graph
        g.add_vertex(name=command_job.execution_id, job=command_job)

        return ExecutionPlan(g)
