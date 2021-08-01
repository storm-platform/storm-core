#
# This file is part of Brazil Data Cube Reproducible Research Management CLI.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Graph Manager."""

import copy
import itertools
from datetime import datetime
from typing import Dict, List

from dictdiffer import diff
from igraph import Graph, VertexSeq, plot

from .config import GraphStyleConfig
from .hasher import multihash_checksum_sha256

# FixMe: Workaround to enable neighbor deletion in igraph
# https://igraph.org/python/doc/api/igraph._igraph.GraphBase.html#neighborhood
MAX_IGRAPH_ORDER = 10000


class VertexStatus:
    """Execution Graph Manager Vertex Status. Is used to define when a vertex is `updated` or `outdated`."""

    Updated = "updated"
    Outdated = "outdated"


class ExecutionGraphManager(object):
    """Execution Graph Manager.

    This class is responsible for the management of execution graphs, which are used to keep
    track of the execution history of the CLI.
    """

    def __init__(self, graph: Graph = None):
        """Create Execution Graph Manager."""
        self._graph = graph or Graph(directed=True)

    def __copy__(self):
        """Create a copy instance of the execution graph manager."""
        return ExecutionGraphManager(self._graph)

    def __deepcopy__(self, memodict={}):
        """Create a deepcopy instance of the execution graph manager."""
        return ExecutionGraphManager(self.graph)

    @property
    def graph(self) -> Graph:
        """Return the execution graph in a `igraph.Graph` object."""
        return copy.deepcopy(self._graph)

    @property
    def vertices(self) -> VertexSeq:
        """Return the vertices of the execution graph in a `igraph.VertexSeq` object."""
        return self.graph.vs

    @property
    def is_outdated(self) -> bool:
        """Returns a flag indicating whether or not there are `outdated` vertices."""
        return len(self._graph.vs.select(status=VertexStatus.Outdated)) > 0 if self._graph else False

    @property
    def is_empty(self) -> bool:
        """Returns a flag indicating if the graph is empty (no vertices)."""
        return len(self._graph.vs) == 0

    @property
    def inputs(self) -> List:
        """Returns vertices inputs."""
        return list(itertools.chain(*self._graph.vs["inputs"])) if not self.is_empty else []

    @property
    def outputs(self) -> List:
        """Returns vertices outputs."""
        return list(itertools.chain(*self._graph.vs["outputs"])) if not self.is_empty else []

    def to_frame(self, dim="vertex") -> "pandas.core.frame.DataFrame":
        """Return the vertices rel."""
        if dim not in ("vertex", "edge"):
            raise RuntimeError("`dim` must be `vertex` or `edge`.")

        # introspecting to retrieve operation
        frame_op = getattr(self._graph, f"get_{dim}_dataframe")
        return frame_op()

    def _define_vertices_required_inputs(self) -> None:
        """Define the vertices required input files.

        A file is considered required when it is not generated by one of the nodes preceding the analyzed node.
        Necessary files are also considered to be those that are not in the project's playback package.
        """
        for vertex in self._graph.vs:
            # retrieving all possible inputs for the current vertex.
            possible_inputs = list(
                itertools.chain(
                    *[x["outputs"] for x in vertex.neighbors(mode="in")]
                )
            )

            # checking which inputs are already defined.
            difference = set(vertex["inputs"]).difference(possible_inputs)

            # update vertex
            vertex["inputs_to_define"] = difference

    def _define_who_vertex_is_outdated(self, vertex, reference_date) -> None:
        """Define who vertex is outdated.

        A vertex is considered out of date if its last update date is less than the `reference_date`.
        Args:
            vertex (igraph.Vertex): The vertex where the verification starts.

            reference_date (datetime): The reference date that will be used to determine if vertex is outdated.

        Returns:
            None: The graph instance is inplace updated.
        """
        if vertex["updated_in"] < reference_date:
            vertex["status"] = VertexStatus.Outdated

        # only use the "outgoing" edges to define the neighbors
        for vertex_neighbor in vertex.neighbors(mode="out"):
            self._define_who_vertex_is_outdated(vertex_neighbor, reference_date)

    def _rebuild_graph(self) -> None:
        """Recreate the edges of the execution graph.

        Returns:
            None: The graph instance is inplace updated.
        """
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
                lambda vtx: vtx["command_checksum"] == _command_checksum, self._graph.vs
            )
        )

        if actual_vertex:
            vertex = actual_vertex[0]
            self.update_vertex(command, repropack, inputs, outputs)
        else:
            vertex = self._graph.add_vertex(
                inputs=inputs,
                outputs=outputs,
                repropack=repropack,
                updated_in=datetime.now(),
                status=VertexStatus.Updated,
                command=" ".join(command),
                command_checksum=_command_checksum,
                inputs_to_define=set()
            )

        self._rebuild_graph()
        self._define_who_vertex_is_outdated(vertex, vertex["updated_in"])

        self._define_vertices_required_inputs()

    def update_vertex(self, command: List[str], repropack: str = None,
                      inputs: Dict[str, Dict] = None, outputs: Dict[str, Dict] = None) -> None:
        """Update a vertex from the execution graph.

        This method updates a previously executed execution that is already present in the execution graph.

        Args:
            command (List[str]): A list with the commands executed by the ReproZip package.

            repropack (str): The name of the ReproZip package.

            inputs (Dict[Dict]): A dict with `path` and `checksum` of input files.

            outputs (Dict[Dict]): A dict with `path` and `checksum` of output files.

        Returns:
            None: The new vertex is updated.

        Note:
            The determination of the execution already added to the graph is done based on the `command`.
            The update considers only the change of `inputs`, `outputs`, and `repropack`.
        """
        _command_checksum = multihash_checksum_sha256(command)

        selected_vertex = self._graph.vs.select(command_checksum=_command_checksum)
        if len(selected_vertex) == 1:  # bingo!
            vertex = selected_vertex[0]

            # define what attribute to update
            variables = {"repropack": repropack, "inputs": inputs, "outputs": outputs}
            invalid_variables = list(
                filter(
                    lambda key: variables[key] is None, variables.keys()
                )
            )

            vertex_attributes = vertex.attributes()
            vertex_attributes = {key: vertex_attributes[key] for key in variables.keys()}

            # check if the valid attributes differs from the old ones
            differences = list(diff(
                vertex_attributes, variables, ignore=invalid_variables
            ))

            if differences:  # only update attributes if there are differences
                vertex.update_attributes({k: variables[k] for k in variables.keys() if k not in invalid_variables})

            vertex["status"] = VertexStatus.Updated
            vertex["updated_in"] = datetime.now()

            self._define_who_vertex_is_outdated(vertex, vertex["updated_in"])
            self._define_vertices_required_inputs()

    def delete_vertex(self, command: List[str], include_neighbors: bool = True) -> None:
        """Delete a vertex from the execution graph.

        Args:
            command (List[str]): A list with the commands executed by the ReproZip package.

            include_neighbors (bool): Flag indicating whether the removed node's neighbors should also be
            considered for removal.

        Returns:
            None: The vertex is deleted inplace.
        """
        _command_checksum = multihash_checksum_sha256(command)

        # delete strategies
        def _delete_vertex_only(vtx):
            """Remove a specific vertex from the execution graph."""
            self._graph.delete_vertices(vtx)

        def _delete_neighborhood(vtx):
            """Remove all vertices subsequent to the one being removed."""
            neighborhood = self._graph.neighborhood(vtx, mode="out", order=MAX_IGRAPH_ORDER)

            # deleting all vertices (including `vertex`)
            self._graph.delete_vertices(neighborhood)

        selected_vertex = self._graph.vs.select(command_checksum=_command_checksum)
        if len(selected_vertex) == 1:
            vertex = selected_vertex[0]

            if include_neighbors:
                _delete_neighborhood(vertex)
            else:
                _delete_vertex_only(vertex)
            self._rebuild_graph()
        self._define_vertices_required_inputs()


def plot_execution_graph(graph_manager: ExecutionGraphManager, filename: str,
                         status_colors: Dict[str, str] = GraphStyleConfig.GRAPH_DEFAULT_VERTICES_COLOR,
                         **kwargs) -> None:
    """Plot the execution graph.

    Args:
        graph_manager (ExecutionGraphManager): The execution graph manager.

        filename (str): The filename of the graph image.

        status_colors (dict): Dict with the color of each vertex status. The available status is
        `updated` and `outdated`. A valid dictionary for the definition of colors looks like this:

            {
                "updated": "blue",
                "outdated": "pink"
            }

        **kwargs (dict): A dict with extra the plot arguments.

    Returns:
        None: The graph is saved on the `filename`.

    See:
        https://igraph.org/python/doc/api/igraph.drawing.html#plot
    """
    _graph = graph_manager.graph

    # define label as status
    for vertex in _graph.vs:
        vertex["label"] = vertex.index

    visual_style = {
        "bbox": (400, 400),
        "margin": 27,
        "vertex_color": "white",
        "vertex_size": 45,
        "vertex_label_size": 22,
        "edge_curved": False,
        "layout": _graph.layout_lgl()
    }

    if status_colors:
        vertex_colors = []
        for status in _graph.vs["status"]:
            vertex_colors.append(status_colors[status])
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
