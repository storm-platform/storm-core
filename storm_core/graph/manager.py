#
# This file is part of SpatioTemporal Open Research Manager Core.
# Copyright (C) 2021 INPE.
#
# SpatioTemporal Open Research Manager Core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""SpatioTemporal Open Research Manager Core Graph Manager."""

import copy
import itertools
from datetime import datetime
from typing import Dict, List, Union

from dictdiffer import diff
from igraph import Graph, VertexSeq

from storm_hasher import StormHasher

# FixMe: Workaround to enable neighbor deletion in igraph
# https://igraph.org/python/doc/api/igraph._igraph.GraphBase.html#neighborhood
MAX_IGRAPH_ORDER = 10000


class VertexStatus:
    """Execution Graph Manager Vertex Status. Is used to define when a vertex is `updated` or `outdated`."""

    Updated = "updated"
    Outdated = "outdated"


class GraphManager(object):
    """Graph Manager.

    This class is responsible to manage graph to create `Research Pipelines`.
    """

    def __init__(self, graph: Graph = None, checksum_algorithm: str = "sha256"):
        """Create Execution Graph Manager."""
        self._graph = graph or Graph(directed=True)
        self._hasher = StormHasher(checksum_algorithm)

    def __copy__(self):
        """Create a copy instance of the execution graph manager."""
        return GraphManager(self._graph, self._hasher.algorithm)

    def __deepcopy__(self, memodict={}):
        """Create a deepcopy instance of the execution graph manager."""
        return GraphManager(self.graph, self._hasher.algorithm)

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
        """Return a flag indicating whether or not there are `outdated` vertices."""
        return len(self._graph.vs.select(status=VertexStatus.Outdated)) > 0 if self._graph else False

    @property
    def is_empty(self) -> bool:
        """Return a flag indicating if the graph is empty (no vertices)."""
        return len(self._graph.vs) == 0

    @property
    def inputs(self) -> List:
        """Return vertices inputs."""
        return list(itertools.chain(*self._graph.vs["inputs"])) if not self.is_empty else []

    @property
    def outputs(self) -> List:
        """Return vertices outputs."""
        return list(itertools.chain(*self._graph.vs["outputs"])) if not self.is_empty else []

    def search_vertex(self, **kwargs):
        """Search graph vertices.

        Args:
            kwargs: Attributes and values to be search.

        Returns:
            VertexSeq: Sequence of found vertex.
        """
        search_result = None

        if self._graph.vs:
            search_result = self._graph.vs.select(**kwargs)
        return search_result

    def to_frame(self, dim="vertex") -> "pandas.core.frame.DataFrame":
        """Return the vertices rel as a DataFrame.

        Args:
            dim (str): Dimension used to transform the graph in a DataFrame. This value can be a `vertex`, for vertex
                       tables or `edge` for edge tables.

        Returns:
            DataFrame: DataFrame with the selected dim data.
        """
        if dim not in ("vertex", "edge"):
            raise RuntimeError("`dim` must be `vertex` or `edge`.")

        # introspecting to retrieve operation
        frame_op = getattr(self._graph, f"get_{dim}_dataframe")
        return frame_op()

    def _define_vertices_required_inputs(self) -> None:
        """Define the vertices required input files.

        A file is considered required when it is not generated by one of the nodes preceding the analyzed node.
        Necessary files are also considered to be those that are not in the execution compendium.
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
            vertex["external_inputs_required"] = list(difference)

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

    def add_vertex(self,
                   name: str,
                   environment_package: str,
                   environment_package_checksum: str,
                   environment_package_checksum_algorithm: str,
                   command: str,
                   command_checksum: str,
                   command_config: Dict,
                   inputs: List[str],
                   outputs: List[str],
                   metadata: Dict[str, Union[Dict, List, str]]) -> None:
        """Add a new vertex to the execution graph.

        This method adds a run with its executed command information created by the ReproZip package to the graph.
        Determining the position of the run on the graph is done based on inputs and outputs.

        Args:
            name (str): Vertex name.

            environment_package (str): The name of the ReproZip package.

            environment_package_checksum (str): ... ToDo

            environment_package_checksum_algorithm (str): ... ToDo

            command (str): A list with the commands executed by the ReproZip package.

            command_checksum (str): ... ToDo

            command_config (Dict): ... ToDo

            inputs (Dict[Dict]): A dict with `path` and `checksum` of input files.

            outputs (Dict[Dict]): A dict with `path` and `checksum` of output files.

            metadata (Dict[str, Union[Dict, List, str]]): ... ToDo
        Returns:
            None: The new vertex is added or updated.

        Note:
            If the command is already in the graph, it is only updated.
        """
        actual_vertex = self.search_vertex(name=name)

        # Note que todas as informações que estão sendo inseridas no grafo tem uma característica comum!
        # Elas são características que serão utilizadas para a indexação das informações! Acho que eu poderia
        # utilizar essa ideia para armazenar essas informações em um container que tenha uma abstração
        # maior nesse quesito!

        if actual_vertex:
            vertex = actual_vertex[0]
            self.update_vertex(command, environment_package, environment_package_checksum,
                               environment_package_checksum_algorithm, metadata, inputs, outputs)
        else:
            vertex = self._graph.add_vertex(
                name=name,
                inputs=inputs,
                outputs=outputs,
                command=command,
                metadata=metadata,
                updated_in=datetime.now(),
                external_inputs_required=[],
                status=VertexStatus.Updated,
                command_config=command_config,
                command_checksum=command_checksum,
                environment_package=environment_package,
                environment_package_checksum=environment_package_checksum,
                environment_package_checksum_algorithm=environment_package_checksum_algorithm
            )

        self._rebuild_graph()
        self._define_who_vertex_is_outdated(vertex, vertex["updated_in"])

        self._define_vertices_required_inputs()

    def update_vertex(self,
                      name: str,
                      environment_package: str,
                      environment_package_checksum: str,
                      environment_package_checksum_algorithm: str,
                      metadata: Dict[str, Union[Dict, List, str]],
                      inputs: List[str] = None,
                      outputs: List[str] = None) -> None:
        """Update a vertex from the execution graph.

        This method updates a previously executed execution that is already present in the execution graph.

        Args:
            name (str): Vertex name.

            environment_package (str): The name of the ReproZip package.

            environment_package_checksum (str): ...

            environment_package_checksum_algorithm (str): ... ToDo

            metadata (Dict[str, Union[Dict, List, str]]): ... ToDo

            inputs (Dict[Dict]): A dict with `path` and `checksum` of input files.

            outputs (Dict[Dict]): A dict with `path` and `checksum` of output files.

        Returns:
            None: The new vertex is updated.

        Note:
            The determination of the execution already added to the graph is done based on the `command`.
            The update considers only the change of `inputs`, `outputs`, and `repropack`.
        """
        selected_vertex = self.search_vertex(name=name)
        if len(selected_vertex) == 1:  # bingo!
            vertex = selected_vertex[0]

            # define what attribute to update
            variables = {
                "inputs": inputs,
                "outputs": outputs,
                "metadata": metadata,
                "environment_package": environment_package,
                "environment_package_checksum": environment_package_checksum,
                "environment_package_checksum_algorithm": environment_package_checksum_algorithm
            }
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

    def delete_vertex(self, name: str, include_neighbors: bool = True) -> None:
        """Delete a vertex from the execution graph.

        Args:
            name (str): Vertex name.

            include_neighbors (bool): Flag indicating whether the removed node's neighbors should also be
            considered for removal.

        Returns:
            None: The vertex is deleted inplace.
        """

        # delete strategies
        def _delete_vertex_only(vtx):
            """Remove a specific vertex from the execution graph."""
            self._graph.delete_vertices(vtx)

        def _delete_neighborhood(vtx):
            """Remove all vertices subsequent to the one being removed."""
            neighborhood = self._graph.neighborhood(vtx, mode="out", order=MAX_IGRAPH_ORDER)

            # deleting all vertices (including `vertex`)
            self._graph.delete_vertices(neighborhood)

        selected_vertex = self.search_vertex(name=name)
        if len(selected_vertex) == 1:
            vertex = selected_vertex[0]

            if include_neighbors:
                _delete_neighborhood(vertex)
            else:
                _delete_vertex_only(vertex)
            self._rebuild_graph()
        self._define_vertices_required_inputs()


__all__ = (
    "VertexStatus",
    "GraphManager"
)