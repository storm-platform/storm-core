# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

try:
    import bagit
except ImportError:
    raise ModuleNotFoundError(
        "To use the Export Helper module, please, install the python-bagit library: `pip install bagit`"
    )

import shutil

from pathlib import Path
from typing import Union

from tempfile import mkdtemp


class BagItExporter:
    """Export class to save a directory into a zipped BagIt."""

    @staticmethod
    def save(
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        **kwargs,
    ) -> Path:
        """Export a directory to a Bagit zip file.

        Args:
            input_path (Union[str, Path]): Directory path to save in the BagIt.

            output_path (Union[str, Path]): Output zip file path.

            kwargs: Extra parameters to the ``bagit.make_bag`` function.

        Returns:
            Path: Path to the generated zipped bagit.

        See:
            For more details about the ``bagit.make_bag`` function, please check the
            bagit-python library repository: <https://github.com/LibraryOfCongress/bagit-python>

        See:
            To more information about the BagIt format, please use the BagIt File Packaging Format Specification (v1.0):
            <https://www.ietf.org/rfc/rfc8493.txt>
        """
        input_path = Path(input_path)
        output_path = Path(output_path)

        if not input_path.is_dir():
            raise NotADirectoryError("The input path must be a valid directory.")

        # copying the original files: we do this to avoid directories changes
        # in the original files.
        tmp_dir = Path(mkdtemp()) / "storm"

        shutil.copytree(input_path, tmp_dir)

        # bagit!
        bagit.make_bag(tmp_dir, **kwargs)

        # moving the generated bagit
        shutil.make_archive(output_path, "zip", tmp_dir)

        shutil.rmtree(tmp_dir)
        return output_path

    @staticmethod
    def load(input_path: Union[str, Path], output_path: Union[str, Path], **kwargs):
        """Import a BagIt.

        Args:
            input_path (Union[str, Path]): Path to the bagit file.

            output_path (Union[str, Path]): Output directory.

            kwargs: Extra parameters to the ``bagit.Bag.validate`` function.

        Returns:
            Path: Path to the output directory.

        See:
            For more details about the ``bagit.Bag.validate`` function, please check the
            bagit-python library repository: https://github.com/LibraryOfCongress/bagit-python

        See:
            To know more about BagIt, please use the BagIt File Packaging Format Specification (v1.0):
            <https://www.ietf.org/rfc/rfc8493.txt>.
        """
        input_path = Path(input_path)
        output_path = Path(output_path)

        if not input_path.is_file():
            raise FileNotFoundError("The input path must be a valid BagIt file.")

        # extract and validating the BagIt.
        tmp_dir = Path(mkdtemp()) / "storm"

        shutil.unpack_archive(input_path, tmp_dir)

        # validating
        bag = bagit.Bag(str(tmp_dir))  # nqa
        bag.validate(**kwargs)

        # move the validate files
        exported_data = tmp_dir / "data"

        shutil.move(exported_data, output_path)
        shutil.rmtree(tmp_dir)

        return output_path


__all__ = "BagItExporter"
