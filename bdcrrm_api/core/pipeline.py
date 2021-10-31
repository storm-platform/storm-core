#
# This file is part of SpatioTemporal Open Research Manager Core.
# Copyright (C) 2021 INPE.
#
# SpatioTemporal Open Research Manager Core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from .compendium import ExecutionCompendium
from .accessor import PipelineServicesAccessor


class ResearchPipeline:
    def __init__(self, name, execution_engine, graph_manager):
        self._name = name

        self._graph_manager = graph_manager
        self._execution_engine = execution_engine

    @property
    def name(self):
        return self._name

    @property
    def inputs(self):
        return self._graph_manager.inputs

    @property
    def outputs(self):
        return self._graph_manager.outputs

    @property
    def is_empty(self):
        return self._graph_manager.is_empty

    @property
    def is_outdated(self):
        return self._graph_manager.is_outdated

    @property
    def services(self):
        return PipelineServicesAccessor(self._graph_manager, self._execution_engine)

    def to_frame(self, **kwargs):
        return self._graph_manager.to_frame(**kwargs)


__all__ = (
    "ResearchPipeline",
    "ExecutionCompendium"
)
