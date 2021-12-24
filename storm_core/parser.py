# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

import os

from igraph import Graph
from typing import Dict, List, Union

from copy import deepcopy
from .engine.executor.api import ExecutionPlan, ExecutableCommand, CommandJob


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


class StormfileCommandParameter:
    """StormFile Command Parameter class.

    Provides useful methods to handle the
    commands parameters.
    """

    def __init__(self, parameter: Dict):
        """Initializer.

        Args:
            parameter (Dict): Dicionary with the name of parameter and their definition.
        """

        self._parameter = parameter
        self._parameter_name = list(self._parameter.keys())[0]

        # resolving the value
        is_valid = True
        value = self._parameter.get(self._parameter_name)

        # validating
        if isinstance(value, dict):
            if "from_env" in value:
                value = os.environ.get(value.get("from_env"))
            else:
                is_valid = False
        elif not isinstance(value, (str, list)):
            is_valid = False

        if not is_valid:
            raise RuntimeError(f"Parameter `{self._parameter_name}` is invalid!")

        self._parameter_value = value

    @property
    def definition(self):
        """StormFile Command Parameter definition."""
        return deepcopy(self._parameter)

    @property
    def name(self):
        """StormFile Command Parameter name."""
        return self._parameter_name

    @property
    def value(self):
        """StormFile Command Parameter value."""
        return self._parameter_value

    @property
    def is_scatter(self):
        """Flag indicating if a Command Parameter is for a scatter operation."""
        return isinstance(self._parameter_value, list)


class StormfileParser:
    """Stormfile parser class.

    This class parses StormFile dict-encoded into a
    valid ``ExecutionPlan``.
    """

    storm_wildcard_pattern = "$storm-"
    """Stormfile Wildcard pattern."""

    @classmethod
    def generate_commands_by_scatter_template(
        cls, command_template: List[str], scatter_parameter: StormfileCommandParameter
    ) -> List[List[str]]:
        """Generate a list of commands using the scattered command and its parameters.

        Args:
            command_template (List[str]): Scatter command template used to generate all commands by
            replacing the parameters values.

            scatter_parameter (StormFileCommandParameter): Scattered parameter.

        Returns:
            List[List[str]]: List with the generated commands.

        Note:
            It is assumed that the parameters to be replaced in the template have a ``wildcard pattern`` defined. Also,
            the parameter's name must be equal in the ``command_template`` template and the ``parameters`` list.
        """
        filled_commands = []

        # finding the scatter parameter (for now, only one).
        parameter_to_scatter_index = next(
            i
            for i, v in enumerate(command_template)
            if v.replace(cls.storm_wildcard_pattern, "") == scatter_parameter.name
        )

        # creating the new commands by replace the template with
        # the scatter parameter value.
        for value in scatter_parameter.value:
            filled_command = deepcopy(command_template)
            filled_command[parameter_to_scatter_index] = value

            filled_commands.append(filled_command)
        return filled_commands

    @classmethod
    def generate_command_by_replace_parameters(
        cls, command_template: List[str], parameters: List[StormfileCommandParameter]
    ) -> List[str]:
        """Generate a command replacing its values with the values of the parameters.

        Args:
            command_template (List[str]): Command template used to generate the complete command, filled with the
            parameters values.

            parameters (List[StormFileCommandParameter]): List of parameters to populate the template.

        Returns:
            List[str]: Filled command.

        """
        filled_command = []

        for command_part in command_template:

            # we will fill each part of command
            # with the parameters value.
            filled_command_part = command_part

            if cls.storm_wildcard_pattern in command_part:
                command_parameter_name = command_part.replace(
                    cls.storm_wildcard_pattern, ""
                )
                command_parameter_value = list(
                    filter(lambda x: x.name == command_parameter_name, parameters)
                )

                # check if the parameter is defined
                if not command_parameter_value or not command_parameter_value[0].value:
                    raise RuntimeError(
                        f"Parameter `{command_parameter_name}` is not defined!"
                    )

                filled_command_part = command_parameter_value[0].value
            filled_command.append(filled_command_part)
        return filled_command

    @classmethod
    def parse(
        cls, stormfile_spec: Dict[str, Union[str, Dict[str, Dict], List]], **kwargs
    ) -> ExecutionPlan:
        """Parse a StormFile dict-encoded to a ExecutionPlan.

        Args:
            stormfile_spec (Union[str, Dict[str, Dict], List]]): Dictionary with the stormfile specification.

            kwargs: Extra parameters to the ``ExecutableCommand`` initializer.

        Returns:
            ExecutionPlan: ExecutionPlan instance.
        """
        g = Graph(directed=True)

        # parsing the commands
        command_groups = {}
        stormfile_steps_commands = stormfile_spec["steps"]

        for step_name in stormfile_steps_commands.keys():

            # rationale: each step is possible to have
            # many commands when the user declares a scatter
            # mode. We use the group concept per step to merge
            # these multiple commands if needed.
            command_groups[step_name] = []
            command_definition = stormfile_steps_commands[step_name]
            commands_to_execute = [command_definition["command"]]

            # parsing the command parameters
            command_parameters = command_definition.get("parameters", [])
            if command_parameters:
                command_parameters = [
                    StormfileCommandParameter({x: command_parameters[x]})
                    for x in command_parameters
                ]

                # checking for scatter definition in the command.
                execution_options = command_definition.get("execution_options")
                scatter_parameter = (
                    execution_options.get("scatter") if execution_options else None
                )

                if scatter_parameter:
                    # for now, the storm-client supports only one parameter at once.
                    # so we filter to get the first occurrence of the scatter command.
                    parameter_to_scattering = next(
                        filter(
                            lambda x: x.name == scatter_parameter, command_parameters
                        )
                    )

                    if parameter_to_scattering:
                        # building the commands based on the scatter template.
                        commands_to_execute = cls.generate_commands_by_scatter_template(
                            command_definition["command"], parameter_to_scattering
                        )

            for command_to_execute in commands_to_execute:
                # creating the command job and saving it on the graph.
                parsed_command = cls.generate_command_by_replace_parameters(
                    command_to_execute, command_parameters
                )

                command_executable = ExecutableCommand(parsed_command, **kwargs)
                command_job = CommandJob(command_executable)

                vertex_job = g.add_vertex(
                    name=command_job.execution_id, job=command_job
                )

                command_groups[step_name].append(
                    {
                        "vertex": vertex_job,
                        "dependencies": command_definition.get("depends", []),
                    }
                )
        # defining the job relations
        for command_group in command_groups:

            commands_in_group = command_groups[command_group]

            for command_in_group in commands_in_group:
                command_vertex = command_in_group["vertex"]
                command_dependencies_group = command_in_group["dependencies"]

                for command_dependency_group in command_dependencies_group:
                    for command_dependency in command_groups[command_dependency_group]:
                        dependency_vertex = command_dependency["vertex"]

                        g.add_edge(dependency_vertex, command_vertex)
        return ExecutionPlan(g)
