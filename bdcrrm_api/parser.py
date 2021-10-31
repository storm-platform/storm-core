#
# This file is part of SpatioTemporal Open Research Manager Core.
# Copyright (C) 2021 INPE.
#
# SpatioTemporal Open Research Manager Core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

import os

from igraph import Graph
from typing import Dict, List

from copy import deepcopy
from .engine.executor.api import ExecutionPlan, ExecutableCommand, CommandJob

COMMAND_PATTERN = "$storm-"


def _parse_command_by_parameter(command: List[str], parameters: List):
    new_command = []
    for command_part in command:
        new_command_part = command_part
        if COMMAND_PATTERN in command_part:
            command_parameter_name = command_part.replace(COMMAND_PATTERN, "")
            command_parameter_value = list(
                filter(
                    lambda x: x.name == command_parameter_name, parameters
                )
            )

            # check if the parameter is defined
            if not command_parameter_value or not command_parameter_value[0].value:
                raise RuntimeError(f"Parameter `{command_parameter_name}` is not defined!")

            new_command_part = command_parameter_value[0].value
        new_command.append(new_command_part)
    return new_command


def _parse_command_by_parameter_scatter(command: List[str], scatter_parameter):
    new_commands = []

    # finding the scatter parameter
    parameter_to_scatter_index = next(
        i for i, v in enumerate(command) if v.replace(COMMAND_PATTERN, "") == scatter_parameter.name
    )

    for value in scatter_parameter.value:
        new_command = deepcopy(command)
        new_command[parameter_to_scatter_index] = value

        new_commands.append(new_command)

    return new_commands


class CommandParameter:
    def __init__(self, parameter: Dict):
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
        return deepcopy(self._parameter)

    @property
    def name(self):
        return self._parameter_name

    @property
    def value(self):
        return self._parameter_value

    @property
    def is_scatter(self):
        return isinstance(self._parameter_value, list)


class CommandParser:

    @staticmethod
    def parse(research_pipeline_spec: Dict[str, Dict], reproducible_storage: str, **kwargs) -> ExecutionPlan:

        # creating the graph
        g = Graph(directed=True)

        # populating it (vertex)
        command_jobs = {}
        commands = research_pipeline_spec["steps"]
        for command_name in commands.keys():
            command_definition = commands[command_name]
            commands_to_execute = [command_definition["command"]]

            # parsing the command parameters
            command_parameters = command_definition.get("parameters", [])
            if command_parameters:
                command_parameters = list(
                    map(
                        lambda x: CommandParameter({x: command_parameters[x]}),
                        command_parameters
                    )
                )

                # checking for scatter definition
                execution_options = command_definition.get("execution_options")
                scatter_parameter = execution_options.get("scatter") if execution_options else None

                if scatter_parameter:
                    parameter_to_scattering = list(filter(lambda x: x.name == scatter_parameter, command_parameters))

                    if parameter_to_scattering:
                        commands_to_execute = _parse_command_by_parameter_scatter(
                            command_definition["command"], parameter_to_scattering[0]
                        )

            for command_to_execute in commands_to_execute:
                # creating the command job and saving it on graph
                parsed_command = _parse_command_by_parameter(command_to_execute, command_parameters)

                command_executable = ExecutableCommand(parsed_command, **kwargs)
                command_job = CommandJob(command_executable, reproducible_storage)

                vertex_job = g.add_vertex(name=command_job.execution_id, job=command_job)

                # mapping the command job id with the definition.
                command_jobs[command_name] = {"vertex": vertex_job,
                                              "dependencies": command_definition.get("depends", [])}

        # defining the job relations
        for command_name in commands.keys():
            command_vertex = command_jobs[command_name]["vertex"]
            command_dependencies = command_jobs[command_name]["dependencies"]

            for command_dependency in command_dependencies:
                dependency_vertex = command_jobs[command_dependency]["vertex"]

                g.add_edge(dependency_vertex, command_vertex)

        return ExecutionPlan(g)


__all__ = (
    "CommandParameter",
    "CommandParser"
)
