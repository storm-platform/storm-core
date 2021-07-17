#
# This file is part of Brazil Data Cube Reproducible Research Management CLI.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Graph Manager."""

from datetime import datetime
from typing import Dict, List

from dictdiffer import diff
from igraph import Graph, VertexSeq, plot

from .hasher import multihash_checksum_sha256


class VertexStatus:
    """Execution Graph Manager Vertex Status. Is used to define when a vertex is `updated` or `outdated`."""

    Updated = "updated",
    Outdated = "outdated"


class ExecutionGraphManager:
    """Execution Graph Manager.

    This class is responsible for the management of execution graphs, which are used to keep 
    track of the execution history of the CLI.
    """

    def __init__(self, graph: Graph = None):
        """Create Execution Graph Manager."""
        self._graph = graph or Graph(directed = True)

    @property
    def graph(self) -> Graph:  # we need expose the graph ?
        """Return the execution graph in a `igraph.Graph` object."""
        return self._graph.copy()

    @property
    def vertices(self) -> VertexSeq:
        """Return the vertices of the execution graph in a `igraph.VertexSeq` object."""
        return self._graph.copy().vs

    def _define_who_vertex_is_outdated(self, vertex, reference_date) -> None:
        """Define who the vertex is outdated.

        Args:
            vertex (igraph.Vertex): The vertex to be checked.

            reference_date (datetime): The reference date.

        Returns:
            None: The graph instance is inplace updated.
        """
        if vertex["updated_in"] < reference_date:
            vertex["status"] = VertexStatus.Outdated
        
        # only use the "outgoing" edges to define the neighbors
        for vertex_neighbor in vertex.neighbors("out"):
            self._define_who_vertex_is_outdated(vertex_neighbor, reference_date)


    def add_vertex(self, repropack: str, command: List[str], inputs: Dict[str, Dict], outputs: Dict[str, Dict]) -> None:
        """Add a new vertex to the execution graph.

        This method adds a run with its executed command information created by the ReproZip package to the graph. 
        Determining the position of the run on the graph is done based on inputs and outputs.

        Args:
            repropack (str): The name of the ReproZip package.

            command (List[str]): A list with the commands executed by the ReproZip package.

            inputs (Dict[Dict]): A dict with `path` and `checksum` of input files. 

            outputs (Dict[Dict]): A dict with `path` and `checksum` of output files. 

        Returns:
            None: The new vertex is added or updated.

        Note:
            If the command is already in the graph, it is only updated.
        """
        _command_checksum = multihash_checksum_sha256(command)

        actual_vertex = list(
            filter(
                lambda vertex: vertex["command_checksum"] == _command_checksum, self._graph.vs
            )
        )

        if actual_vertex:
            vertex = actual_vertex[0]
            self.update_vertex(command, repropack, inputs, outputs)
        else:
            vertex = self._graph.add_vertex(        
                inputs = inputs,
                outputs = outputs,
                repropack = repropack,
                updated_in = datetime.now(),
                status = VertexStatus.Updated,
                command = " ".join(command),
                command_checksum = _command_checksum,
            )

        if len(self._graph.vs) > 1:  # If there is more than one node in the graph
            # rebuild the graph

            # 1. Remove all edges
            self._graph.delete_edges()

            # 2. Rebuild edges
            for vertex_l1 in self._graph.vs:
                reference_outputs = set(vertex_l1["outputs"])
                
                for vertex_l2 in self._graph.vs:

                    if vertex_l1 != vertex_l2:
                        if not set(vertex_l2["inputs"]).isdisjoint(reference_outputs):
                            self._graph.add_edge(vertex_l1, vertex_l2)

        self._define_who_vertex_is_outdated(vertex, vertex["updated_in"])


    def update_vertex(self, command: List[str], repropack: str = None, 
                            inputs: Dict[str, Dict] = None, outputs: Dict[str, Dict] = None) -> None:
        """Update a vertex from the execution graph.

        This method updates a previously executed execution that is already present in the execution graph.

        Args:
            repropack (str): The name of the ReproZip package.

            command (List[str]): A list with the commands executed by the ReproZip package.

            inputs (Dict[Dict]): A dict with `path` and `checksum` of input files. 

            outputs (Dict[Dict]): A dict with `path` and `checksum` of output files. 

        Returns:
            None: The new vertex is updated.

        Note:
            The determination of the execution already added to the graph is done based on the `command`. 
            The update considers only the change of `inputs`, `outputs`, and `repropack`.
        """
        _command_checksum = multihash_checksum_sha256(command)

        selected_vertex = self._graph.vs.select(command_checksum = _command_checksum)
        if len(selected_vertex) == 1:  # bingo!
            vertex = selected_vertex[0]

            # define what attribute to update
            variables = { "repropack": repropack, "inputs": inputs, "outputs": outputs }
            invalid_variables = list(
                filter(
                    lambda key: variables[key] is None, variables.keys()
                )
            )

            vertex_attributes = vertex.attributes()
            vertex_attributes = { key: vertex_attributes[key] for key in variables.keys() }

            # check if the valid attributes differs from the old ones
            differences = list(diff(
                vertex_attributes, variables, ignore=invalid_variables
            ))

            if differences:  # only update attributes if there are differences
                vertex.update_attributes({ k: variables[k] for k in variables.keys() if k not in invalid_variables })

            vertex["status"] = VertexStatus.Updated
            vertex["updated_in"] = datetime.now()

            self._define_who_vertex_is_outdated(vertex, vertex["updated_in"])

    def delete_vertex(self, command: List[str]) -> None:
        """Delete a vertex from the execution graph.

        Args:
            command (List[str]): A list with the commands executed by the ReproZip package.

        Returns:
            None: The vertex is deleted inplace.
        """
        _command_checksum = multihash_checksum_sha256(command)

        def _delete(vertex):
            """Remove all vertices subsequent to the one being removed."""
            for vertex_neighbor in vertex.neighbors('out'):
                _delete(vertex_neighbor)
            self._graph.delete_vertices(vertex)
        
        selected_vertex = self._graph.vs.selected(command_checksum = _command_checksum)
        if len(selected_vertex) == 1:  # bingo!
            vertex = selected_vertex[0]

            _delete(vertex)


def plot_execution_graph(graph_manager: ExecutionGraphManager, filename: str, status_colors: Dict[str, str] = None, **kwargs) -> None:
    """Plot the execution graph.

    Args:
        graph (ExecutionGraphManager): The execution graph manager.

        filename (str): The filename of the graph image.

        **kwargs (dict): A dict with extra the plot arguments.
    
    Returns:
        None: The graph is saved on the `filename`.

    See:
        https://igraph.org/python/doc/api/igraph.drawing.html#plot
    """
    
    _graph = graph_manager.graph

    # define label as status
    for vertex in _graph.vs:
        vertex['label'] = vertex.index + 1

    visual_style = {}

    # Set bbox and margin
    visual_style["bbox"] = (400, 400)
    visual_style["margin"] = 27
    
    # Set vertex colours
    visual_style["vertex_color"] = 'white'
    
    # Set vertex size
    visual_style["vertex_size"] = 45
    
    # Set vertex lable size
    visual_style["vertex_label_size"] = 22
    
    # Don't curve the edges
    visual_style["edge_curved"] = False
    
    # Set the layout
    visual_style["layout"] = _graph.layout_lgl()
    
    if status_colors:
        vertex_colors = []
        for status in _graph.vs["status"]:
            # ToDo: Investigate why this type change occurs
            if isinstance(status, str):
                vertex_colors.append(status_colors[status])
            else:
                vertex_colors.append(status_colors[status[0]])

        visual_style["vertex_color"] = vertex_colors

    if kwargs:
        visual_style.update(kwargs)

    # Plot the graph
    plot(_graph, filename, **visual_style)


__all__ = (
    "VertexStatus",
    "ExecutionGraphManager",

    "plot_execution_graph"
)
