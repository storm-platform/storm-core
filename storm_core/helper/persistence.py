# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

try:
    import dill
except ImportError:
    raise ModuleNotFoundError(
        "To use the Persistence Helper module, please, install the dill library: `pip install dill`"
    )

from pathlib import Path
from typing import Union


class PicklePersistenceContainer:
    """A base (and generic) persistence container to store complete
    objects into pickle files."""

    def __init__(self, obj: object):
        """Initializer.

        Args:
            obj (object): Object to persist.
        """
        self._obj = obj

    @property
    def obj(self):
        return self._obj

    @classmethod
    def load(cls, path: Union[str, Path], **kwargs) -> object:
        """Load a dumped Persistence Container object pickle.

        Args:
            path (Union[str, Path]): Path to the pickle file.

        Returns:
            object: The loaded object.
        """
        object_path = Path(path)

        if not object_path.is_file():
            raise FileNotFoundError(f"File not found: {object_path}")

        with open(object_path, "rb") as ifile:
            return dill.load(ifile, **kwargs).obj

    @classmethod
    def save(
        cls,
        obj: object,
        path: Union[str, Path],
        **kwargs,
    ) -> Path:
        """Persist an arbitrary object into a pickle file.

        This function stores the given object in a ``PicklePersistenceContainer`` and
        then save it in a pickle file.

        Args:
            obj (object): Object to persist.

            path (Union[str, Path]): Path to the pickle file.

            kwargs (dict): ``dill.dump`` extra arguments.

        Returns:
            Path: Path to the created pickle file.

        Note:
            This function uses the ``dill`` library to read/write pickle files.

        See:
            For more details about the ``dill.dump`` function, please check the
            official documentation: https://dill.readthedocs.io/en/latest/

        """
        object_path = Path(path)
        object_path.parent.mkdir(parents=True, exist_ok=True)

        # saving the pickle object
        persistence_container = cls(obj)

        with open(object_path, "wb") as ofile:
            dill.dump(persistence_container, ofile, **kwargs)

        return object_path


__all__ = "PicklePersistenceContainer"
