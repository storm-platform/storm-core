# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

import pandas as pd

from pathlib import Path
from typing import Union, List


def parse_csv(file_path: Union[str, Path], column: str, **kwargs) -> List[str]:
    """Parse a CSV file column into a list of values.

    Args:
        file_path (Union[str, Path]): Path to CSV that will be loaded.

        column (str): Column of the CSV to load.

        kwargs: Extra options to the ``pandas.read_csv`` function.

    Returns:
        List[str]: List of values loaded.

    Note:
        The values loaded from the CSV file are converted to string.

    See:
        For more details about the ``pandas.read_csv`` function, please check the
        Pandas documentation: <https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html>
    """
    df = pd.read_csv(file_path, **kwargs)
    return df[column].astype(str).tolist()


class FileLoader:
    """File loader for scatter values definition.

    This class provides strategies to load
    values from different file types. Every
    strategy available load the file and return
    a single list of strings.
    """

    strategies = {"csv": parse_csv}

    @classmethod
    def load(cls, file_type, *args, **kwargs) -> List[str]:
        """Load values from a file."""
        _load_strategy = cls.strategies[file_type]
        return _load_strategy.__call__(*args, **kwargs)
