#
# This file is part of SpatioTemporal Open Research Manager Core.
# Copyright (C) 2021 INPE.
#
# SpatioTemporal Open Research Manager Core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Graph Serializer."""

import functools
import json
from datetime import datetime
from typing import Dict, Union

from igraph import Graph


class JSONGraphConverter(object):
    """JSON Graph converter.

    Serializes/deserializes the igraph.Graph object into a JSON object.
    The JSON format used when reading/writing must follow the `json-graph-specification`.

    See:
        For more information about the `json-graph-specification`, please refer to the official documentation:
        https://github.com/jsongraph/json-graph-specification
    """

    @staticmethod
    def to_json(graph: Graph, attribute_as_index=None, **kwargs) -> Dict:
        """Save a graph to a persistence store into a JSON file.

        Args:
            graph (igraph.Graph): Graph to be saved.

            attribute_as_index (str): Attribute that should be used as the vertex identifier.

            kwargs (Dict): Extra parameters to JSON Graph object.
        Returns:
            None: Graph is saved to a persistence store.
        """

        # defining node identifier function
        def node_mapper(x):
            return x.attributes()[attribute_as_index] if attribute_as_index else x.index

        # add vertex
        nodes = {
            node_mapper(node): {
                # converting attributes to avoid type errors
                "metadata": json.loads(json.dumps(node.attributes(), default=str))
            } for node in graph.vs
        }

        # add edges
        edges = [
            {
                "source": node_mapper(graph.vs[edge.source]),
                "target": node_mapper(graph.vs[edge.target])
            } for edge in graph.es
        ]

        # ToDo: Add `jsongraph/json-graph-specification` validator
        return {
            "graph": {
                "directed": graph.is_directed(),
                "nodes": nodes if nodes else {},
                "edges": edges if edges else [],
                **kwargs
            }
        }

    @staticmethod
    def from_json(data: Dict, attribute_as_index=None) -> Union[Graph, None]:
        """Save a graph to a persistence store into a JSON file.

        Args:
            data (Dict): Dict in the `json-graph-specification` format that will be transformed into `igraph.Graph`.

            attribute_as_index (str): Attribute that should be used as the vertex identifier.
        Returns:
            Union[igraph.Graph, None]: `igraph.Graph` loaded or None.
        """
        # ToDo: Add GraphJSON validator (marshmallow)
        # extract data
        graph_data = data["graph"]
        graph_vertices = graph_data.get("nodes", {})
        graph_edges = graph_data.get("edges", [])

        g = Graph(directed=graph_data.get("directed", False))

        #
        # Rebuilding the graph
        #

        # adding vertices
        for vertex in graph_vertices:
            vertex_data = graph_vertices[vertex]

            metadata = vertex_data.get("metadata", {})

            # Change date types
            metadata["updated_in"] = datetime.fromisoformat(metadata["updated_in"])

            g.add_vertex(**metadata)

        # adding edges
        for edge in graph_edges:
            node_source_id = edge["source"]
            node_target_id = edge["target"]
            if attribute_as_index:
                _filter = lambda x, attr_value: x.attributes()[attribute_as_index] == attr_value

                node_source_id = filter(functools.partial(_filter, attr_value=edge["source"]), g.vs)
                node_target_id = filter(functools.partial(_filter, attr_value=edge["target"]), g.vs)

            g.add_edge(node_source_id, node_target_id)
        return g


__all__ = (
    "JSONGraphConverter"
)
