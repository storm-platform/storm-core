# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from pathlib import Path

from igraph import plot
from typing import Dict, Union

from ..index.graph import GraphManager

GRAPH_PLOT_DEFAULT_STYLE = {
    "bbox": (400, 400),
    "margin": 27,
    "vertex_size": 45,
    "vertex_label_size": 22,
    "edge_curved": False,
}
"""Default plot style."""

GRAPH_PLOT_DEFAULT_STATUS_COLOR = {"updated": "green", "outdated": "yellow"}
"""Default plot status colos"""


def plot_styled_indexed_executions(
    graph_manager: GraphManager,
    filename: Union[str, Path],
    status_colors: Dict[str, str] = None,
    **kwargs
) -> Union[Path, None]:
    """Render in a Figure the relation of the indexed executions (as a digraph).

    Args:
        graph_manager (graph_manager): The Graph Manager object.

        filename (str): The filename of the graph image.

        status_colors (dict): Dict with the color of each vertex status. The available status is
        `updated` and `outdated`. A valid dictionary for the definition of colors looks like this::

            {
                "updated": "blue",
                "outdated": "pink"
            }

        **kwargs: Extra parameters to the ``igraph.plot`` function.

    Returns:
        Union[None, str]: if saved, returns the ``filename`` where the graph is rendered. Otherwise, returns None.

    See:
        To more information about the ``igraph.plot``, please check the official python-igraph documentation:
        <https://igraph.org/python/doc/api/igraph.drawing.html#plot>
    """
    filename = Path(filename).with_suffix(".png")
    if graph_manager.is_empty:
        return None

    # define label as status
    _graph = graph_manager.graph

    for vertex in _graph.vs:
        vertex["label"] = vertex.index

    visual_style = GRAPH_PLOT_DEFAULT_STYLE
    if kwargs:
        visual_style = kwargs

    # coloring the nodes based on their status.
    vertex_colors = []
    status_colors = status_colors if status_colors else GRAPH_PLOT_DEFAULT_STATUS_COLOR

    for status in _graph.vs["status"]:
        vertex_colors.append(status_colors[status])
    visual_style["vertex_color"] = vertex_colors
    visual_style["layout"] = _graph.layout_lgl()

    # Plot the graph
    plot(_graph, str(filename), **visual_style)

    return filename


def plot_dot_indexed_executions(
    graph_manager: GraphManager, filename: Union[str, Path], render=False
) -> Union[Path, None]:
    """Write the ``dot`` visual representation of the indexed executions relation.

    Args:
        graph_manager (graph_manager): The Graph Manager object.

        filename (str): The filename of the graph image.

        render (bool): Flag indicating if the generated ``dot`` should be rendered
        in a ``png`` file (graphviz required).

    Returns:
        Union[None, str]: if saved, returns the ``filename`` where the ``dot`` is generated. Otherwise, returns None.
    """
    filename = Path(filename).with_suffix(".dot")
    graph_manager.graph.write(filename, format="dot")

    if render:
        try:
            import graphviz
        except ImportError:
            raise ModuleNotFoundError(
                "To render the ``dot`` file, please, install the graphviz library: "
                "`pip install graphviz` or `poetry add graphviz`"
            )

        graphviz.render("dot", "png", filename)
    return filename


__all__ = (
    "plot_styled_indexed_executions",
    "plot_dot_indexed_executions",
)
