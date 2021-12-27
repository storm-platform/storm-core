# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


from .search import QuerySearch, FacetedIndexSearchAccessor


class SearchAccessor:
    @property
    def query(self):
        return QuerySearch(self._execution_indexer)

    @property
    def faceted(self):
        return FacetedIndexSearchAccessor(self._execution_indexer)

    def __init__(self, execution_indexer):
        self._execution_indexer = execution_indexer
