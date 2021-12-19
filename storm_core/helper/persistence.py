# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""SpatioTemporal Open Research Manager Core Persistence Operations."""

from typing import Union

from igraph import Graph


class GraphPersistencePickle(object):
    """Graph persistence using pickle."""

    @staticmethod
    def save_graph(graph: Graph, pickle_file: str) -> None:
        """Save a graph to a persistence store into a pickle file.

        Args:
            graph (igraph.Graph): Graph to be saved.

            pickle_file (str): Full path to the file where the graph will be saved.

        Returns:
            None: Graph is saved to a persistence store.
        """
        graph.write_pickle(pickle_file)

    @staticmethod
    def load_graph(pickle_file: str) -> Union[Graph, None]:
        """Load a graph from a persistence store.

        Args:
            pickle_file (str): Full path to the pickle file that will be loaded.

        Returns:
            igraph.Graph: Graph loaded from a persistence store.
        """
        return Graph.Read_Pickle(pickle_file)


__all__ = "GraphPersistencePickle"
