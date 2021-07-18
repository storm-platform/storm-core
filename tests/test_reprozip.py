#
# This file is part of Brazil Data Cube Reproducible Research Management CLI.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Unit-test for ReproZip functionalities"""


from pytest import fixture

from bdcrrm_cli.reprozip import (_extract_execution_input_by_working_dir,
                                 _extract_execution_output)


@fixture
def reprozip_config_file():
    return {
        "inputs_outputs": [
            { # 1
                "read_by_runs": [0],
                "written_by_runs": [],
                "path": "/system/directory/so.lib"
            },
            { # 2
                "read_by_runs": [0],
                "written_by_runs": [],
                "path": "/system/another/directory/so2.lib"
            },
            { # 3
                "read_by_runs": [0],
                "written_by_runs": [],
                "path": "/my/working/dir/script.py"
            },
            { # 4
                "read_by_runs": [0],
                "written_by_runs": [],
                "path": "/my/working/dir/data/data.xlsx"
            },
            { # 5
                "read_by_runs": [],
                "written_by_runs": [0],
                "path": "/my/working/dir/data/out/data_processed.csv"
            },
            { # 6
                "read_by_runs": [],
                "written_by_runs": [0],
                "path": "/my/working/dir/data/out/data_processed_2.csv"
            }
        ]
    }


def test_when_input_filter_is_done_only_files_within_working_dir_should_be_returned(reprozip_config_file):
    working_dir = ["/my/working/dir/"]
    result = _extract_execution_input_by_working_dir(reprozip_config_file, working_dir)

    assert all(
        list(
            map(
                lambda file: "lib" not in file["path"] and "csv" not in file["path"], result
            )
        )
    )


def test_when_output_filter_is_done_all_written_files_should_be_returned(reprozip_config_file):
    result = _extract_execution_output(reprozip_config_file)

    assert all(
        list(
            map(
                lambda file: "csv" in file["path"], result
            )
        )
    )
