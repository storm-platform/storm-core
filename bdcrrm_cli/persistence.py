#
# This file is part of Brazil Data Cube Reproducible Research Management CLI.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Persistence Operations."""

import os

import bagit
import shutil

from tempfile import mkdtemp

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


class BagItExporter(object):
    """Exporter to save a experiment project in BagIt organization."""

    @staticmethod
    def export(project_name: str, project_meta_dir: str, output_dir: str, hashing_processes: int = 1) -> str:
        """Export an analysis project to a BagIt zip file.

        Args:
            project_name (str): Name of the project to be exported.

            project_dir (str): Directory where the project is located.

            output_dir (str): Directory where the project will be exported.

            hashing_processes (int): Number of processes to use for hashing files.

        Returns:
            str: Path to the exported bagit zip file.

        See:
            The BagIt File Packaging Format (V1.0): https://www.ietf.org/rfc/rfc8493.txt
        """
        tmp_directory = os.path.join(mkdtemp(), "bdcrrm")
        shutil.copytree(project_meta_dir, tmp_directory)

        # do bagit! 
        bagit.make_bag(tmp_directory, processes=hashing_processes)

        os.makedirs(output_dir, exist_ok=True)
        shutil.make_archive(
            os.path.join(output_dir, project_name), "zip", tmp_directory
        )


__all__ = (
    "BagItExporter",
    "GraphPersistencePickle"
)
