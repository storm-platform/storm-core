# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from abc import ABC
from typing import List, Tuple, Optional, Generator

from .graph import VertexStatus
from .graph.manager import MAX_IGRAPH_ORDER
from .model import ExecutionCompendium, ExecutionCompendiumFactory


class IndexerSearch(ABC):
    """Index search class.

    In the Storm Core, all executions are indexed in a graph database. This class
    provides the abstract methods access the graph database and its content.
    """

    def __init__(self, execution_indexer):
        """Initializer.

        Args:
            execution_indexer (ExecutionIndexer): Execution indexer object.
        """
        self._execution_indexer = execution_indexer

    def query(self, **kwargs) -> Generator[Tuple[ExecutionCompendium, str], None, None]:
        """Query method to search indexed execution compendia."""
        pass


class IndexerQuerySearch(IndexerSearch):
    """Indexer basic query search.

    This class provides an implementation of the query method
    that allows base search queries in the graph index database.
    """

    def query(self, **kwargs) -> Generator[Tuple[ExecutionCompendium, str], None, None]:
        """Query method to search indexed execution compendia.

        Args:
            kwargs: Query predicates.

        Returns:
            Generator[Tuple[ExecutionCompendium, str]]: A generator with the execution
            compendia and the status.

        See:
            In the ``kwargs``, the ``igraph`` predicates can be used. For more information
            about these predicates, please, check the official igraph documentation:
            <https://igraph.org/python/api/latest/igraph.VertexSeq.html#select>.
        """
        compendia_vertex = (
            self._execution_indexer.graph_manager.search_vertex(**kwargs) or []
        )

        for compendium_vertex in compendia_vertex:
            # creating the execution compendium object.
            execution_compendium = ExecutionCompendiumFactory.create_compendium(
                compendium_vertex
            )

            # yielding with the current status.
            yield execution_compendium, compendium_vertex["status"]


class IndexerNeighborhoodSearch(IndexerSearch):
    """Indexer Neighborhood search.

    This class provides an implementation of the query method
    that allows base search queries combined with the neighborhood
    search.
    """

    def query(
        self, neighborhood_mode, **kwargs
    ) -> Generator[
        Tuple[ExecutionCompendium, Optional[List[ExecutionCompendium]], str], None, None
    ]:
        """Query method to search indexed execution compendia.

        Args:
            neighborhood_mode (str): Mode of the neighborhood relation (e.g., "in" or "out").

            kwargs: Query predicates.

        Returns:
            Generator[Tuple[ExecutionCompendium, Optional[List[ExecutionCompendium]], str], None, None]: A generator with
            the execution compendia, it neighborhood and the status.

        See:
            In the ``kwargs``, the ``igraph`` predicates can be used. For more information
            about these predicates, please, check the official igraph documentation:
            <https://igraph.org/python/api/latest/igraph.VertexSeq.html#select>.
        """
        compendia_vertex = (
            self._execution_indexer.graph_manager.search_vertex(**kwargs) or []
        )

        for compendium_vertex in compendia_vertex:
            # creating the execution compendium object.
            execution_compendium = ExecutionCompendiumFactory.create_compendium(
                compendium_vertex
            )

            # searching the neighborhood
            neighborhood = self._execution_indexer.graph_manager.graph.neighborhood(
                compendium_vertex, mode=neighborhood_mode, order=MAX_IGRAPH_ORDER
            )

            # creating the execution compendium objects
            execution_compendium_neighborhood = [
                ExecutionCompendiumFactory.create_compendium(nh)
                for nh in (neighborhood or [])
            ]

            # yielding with the current status.
            yield execution_compendium, execution_compendium_neighborhood, compendium_vertex[
                "status"
            ]


class IndexerFacetedSearch(IndexerSearch):
    """Class with predefined queries (facets) based on in the
    execution compendium properties.
    """

    def outdated_compendia(
        self,
    ) -> Generator[Tuple[ExecutionCompendium, str], None, None]:
        """Retrieve all outdated execution compendia.

        Returns:
            Generator[Tuple[ExecutionCompendium, str], None, None]: A generator with the outdated execution compendia objects.
            The objects are returned in topological order.
        """
        _graph = self._execution_indexer.graph_manager.graph
        for vertex_index in _graph.topological_sorting(mode="out"):
            vertex = _graph.vs[vertex_index]

            if vertex["status"] == VertexStatus.Outdated:
                selected_vertex = next(
                    self._execution_indexer.search.query.query(name=vertex["name"])
                )
                yield selected_vertex


__all__ = (
    "IndexerSearch",
    "IndexerQuerySearch",
    "IndexerNeighborhoodSearch",
    "IndexerFacetedSearch",
)
