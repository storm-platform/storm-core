#
# This file is part of Brazil Data Cube Reproducible Research Management CLI.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Persistence Operations."""

import os
from igraph import Graph

from .config import GraphPersistenceConfig


class GraphPersistencePickle(object):
    """Graph persistence using pickle."""

    @staticmethod
    def save_graph(graph, directory):
        """Save a graph to a persistence store into a pickle file.
        
        Args:
            graph (igraph.Graph): Graph to be saved.

            directory (str): Directory where the `meta` graph file will be saved.

        Returns:
            None: Graph is saved to a persistence store.
        """
        graph.write_pickle(os.path.join(directory, GraphPersistenceConfig.GRAPH_DEFAULT_PICKLE_NAME))

    @staticmethod
    def load_graph(directory):
        """Load a graph from a persistence store.
        
        Args:
            directory (str): Directory where the `meta` graph file is located.

        Returns:
            igraph.Graph: Graph loaded from a persistence store.
        """

        # ToDo: Review this return
        try:
            return Graph.Read_Pickle(os.path.join(directory, GraphPersistenceConfig.GRAPH_DEFAULT_PICKLE_NAME))
        except:
            return None


__all__ = (
    "GraphPersistencePickle"
)
