#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Graph Executor module."""

from abc import ABC, abstractmethod
from typing import Callable

from igraph import Graph
from paradag import DAG, dag_run, MultiThreadProcessor, SequentialProcessor


class TopologicalExecutor(ABC):
    """Interface for determining the format of a TopologicalExecutor. The implementations
       of this class are responsible for providing functionalities that allow the execution of
       tasks represented in directed acyclic graphs.
    """

    @staticmethod
    @abstractmethod
    def make(fnc: Callable, graph: Graph, **kwargs):
        """Execute a ExecutionGraph
        Args:
            fnc (Callable): Function used to execute the graph vertices.

            graph (igraph.Graph): Complete Directed Acyclic Graph that will be executed.

            kwargs (dict): Extra parameters used to the `TopologicalExecutor`.
        """


class CustomizableSelector:
    """Customizable dag_run selector to change the number of process used."""

    def __init__(self, processors: int):
        self._processors = processors

    def select(self, running, idle):
        task_number = max(0, self._processors - len(running))
        return list(idle)[:task_number]


class ReproStandardExecutor:
    """Reproduction executor of an execution graph.

    This class implements all the rules necessary for parallel
    reproduction (multiprocessing) of a execution graph.
    """

    def __init__(self, fnc: Callable, graph: Graph, **kwargs):
        """
            Args:
                fnc (Callable): Function used to process the graph vertices.

                graph (igraph.Graph): Execution graph with all steps that will be processed.

                kwargs (dict): Extra parameters for the `fnc`.
        """
        self._fnc = fnc
        self._graph = graph
        self._extra_options = kwargs

        self.__level = []

    def param(self, vertex_index):
        """Select the vertex that will be processed."""
        return self._graph.vs[vertex_index]

    def execute(self, param):
        """Execute a vertex."""
        self._fnc(param, self.__level, **self._extra_options)

    def deliver(self, _, result):
        """Deliver results to descendants vertices"""
        if result:
            self.__level.extend(result)


class ReproParaDAGParallelTopologicalExecutor(TopologicalExecutor):

    @staticmethod
    def make(fnc, graph: Graph, **kwargs):
        processor = kwargs.get("processor_options", {})

        # creating the base execution graph
        dag = DAG()
        dag.add_vertex(*[v.index for v in graph.vs])

        # defining who will be execute the graph
        processor_class = MultiThreadProcessor

        if processor:
            processors_number = processor["processors"]
            if processor["processor_mode"] == "single":
                processor_class = SequentialProcessor
        else:
            processors_number = 1

        # submitting the jobs
        for vertex_index in graph.topological_sorting():
            vertex = graph.vs[vertex_index]

            for vertex_neighbors in vertex.predecessors():
                dag.add_edge(vertex_neighbors.index, vertex.index)

        dag_run(dag, processor=processor_class(),
                executor=ReproStandardExecutor(fnc, graph, **kwargs.get("fnc_options", {})),
                selector=CustomizableSelector(processors_number))


__all__ = (
    "TopologicalExecutor",
    "ReproParaDAGParallelTopologicalExecutor"
)
