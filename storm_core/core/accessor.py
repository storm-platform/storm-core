# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from .operations import ReproducibleOperations
from ..graph.index.indexer import ExecutionIndexer


class PipelineServicesAccessor:
    def __init__(self, graph_manager, execution_engine):
        self._graph_manager = graph_manager
        self._execution_engine = execution_engine

    @property
    def index(self):
        return ExecutionIndexer(self._graph_manager)

    @property
    def operations(self):
        return ReproducibleOperations(self._execution_engine, self.index)
