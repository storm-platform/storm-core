#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Command-Line Interface Tree Graphics."""

from typing import List

from rich.tree import Tree


def tree_one_root_with_children(root_name: str, children: List[str]) -> Tree:
    """Create the a tree with only one root node and several children.

    Args:
        root_name (str): Root name.

        children (List[str]): Root children.

    Returns:
        Tree: Generated tree.
    """
    tree = Tree(root_name)

    for child in children:
        tree.add(child)

    return tree
