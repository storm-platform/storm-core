#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Command-Line Interface Graph Graphics."""

from typing import List, Tuple, Union

import click
from igraph import Graph


def _ascii_dag(graph: Graph) -> Union[None, 'AsciiGraph']:
    """Generate a ASCII Directed Acyclic Graph (DAG).

    Args:
        graph (igraph.Graph): Graph instance that is used to generate the ASCII DAG.

    Returns:
        Union[None, AsciiGraph]: If the graph is displayed, the created graph instance is returned. Otherwise,
        None will be returned.
    """
    from asciidag.graph import Graph as AsciiGraph
    from asciidag.node import Node

    def vertex_parents(vertex_id: int, edgelist: List[Tuple]) -> List[Tuple]:
        """Return all vertex parents based on a edge list.

        Args:
            vertex_id (int): Vertex ID.

            edgelist (List[Tuple]): List with tuples with all graph edges.

        Returns:
            List[Tuple]: Edges that is related to `vertex_id`.
        """
        return list(
            filter(
                lambda x: x[0] == vertex_id, edgelist
            )
        )

    if not graph:
        return None  # initially, the project does not have a graph.
    ascii_graph = AsciiGraph()

    # generate ascii nodes
    edgelist = graph.get_edgelist()
    nodes = {
        v.index: Node(f"{str(v.index)} ({v['command']})") for v in graph.vs
    }

    # connect the nodes
    for vertex in graph.vs:
        node_parents = vertex_parents(vertex.index, edgelist)

        nodes[vertex.index].parents.extend([
            nodes[i[1]] for i in node_parents
        ])

    # show!
    ascii_graph.show_nodes(list(nodes.values()))
    return ascii_graph


def show_ascii_execution_graph(graph: Graph):
    """Display the project execution graph on the terminal.

    Args:
        graph (Graph): Project graph instance.

    Returns:
        None: Graph will be presented on the CLI terminal

    Raises:
        ModuleNotFoundError: When `asciidag` library is not avaliable.
    """
    try:
        _graph = _ascii_dag(graph)

        if not _graph:
            click.secho("Project Graph is empty...", bold=True)

    except ModuleNotFoundError:
        click.secho("To visualize the graph it is necessary to install the `asciidag` "
                    "library. To do so, use:")
        click.secho("\t pip install asciidag", bold=True)


__all__ = (
    "show_ascii_execution_graph"
)
