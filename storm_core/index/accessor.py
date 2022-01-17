# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from .search import IndexerQuerySearch, IndexerFacetedSearch, IndexerNeighborhoodSearch


class SearchAccessor:
    """Search accessor class.

    Accessor that provides access to the Execution Index
    search methods.
    """

    def __init__(self, execution_indexer):
        """Initializer.

        Args:
            execution_indexer (ExecutionIndexer): ExecutionIndexer object.
        """
        self._execution_indexer = execution_indexer

    @property
    def query(self):
        """Query Search operations."""
        return IndexerQuerySearch(self._execution_indexer)

    @property
    def faceted(self):
        """Faceted Search operations."""
        return IndexerFacetedSearch(self._execution_indexer)

    @property
    def neighborhood(self):
        """Neighborhood Query Search operations."""
        return IndexerNeighborhoodSearch(self._execution_indexer)
