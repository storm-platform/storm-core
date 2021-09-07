#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""bdcrrm-api utility for input template file generation."""

import json
from pathlib import Path

from bdcrrm_api.hasher import multihash_checksum_sha256


def prepare_the_required_input_files_gdalcubes(basedir: str, files_template: str, output_files_template: str):
    """Prepare the files that will be used to reproduce the experiment.

    Args:
        basedir (str): Base directory where the files used on the gdalcubes experiment
        is available on the machine.

        files_template (str): Path to the mapping template of the required files.

    Returns:
        None: updated files template will be saved on `output_files_template`
    """
    files = json.load(open(files_template))

    output_document = {
        "files": [],
        "checksum": {}
    }

    for file_path in Path(basedir).rglob("*.tif"):
        #
        # General definitions
        #
        file_name = path.name
        file_checksum = multihash_checksum_sha256(path)

        #
        # Save informations
        #
        for file in files["files"]:
            if file["source"] == file_name:
                output_document["files"].append({
                    "source": file_name,
                    "target": str(file_path.absolute())
                })

                output_document["checksum"][file_name] = file_checksum

    with open(output_files_template, "w") as ofile:
        json.dump(output_document, ofile)


if __name__ == "__main__":
    prepare_the_required_input_files_gdalcubes("lc8_scenes/uncompress/L8_Amazon", "files-template.json",
                                               "files-template-filled.json")
