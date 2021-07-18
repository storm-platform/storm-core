#
# This file is part of Brazil Data Cube Reproducible Research Management CLI.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Unit-test for ExecutionGraphManager class"""

from tempfile import mkstemp
from typing import Tuple

from pytest import fixture

from bdcrrm_cli.graph import ExecutionGraphManager, VertexStatus
from bdcrrm_cli.hasher import multihash_checksum_sha256


@fixture
def reprozip_processes() -> Tuple[str, str, str, str]:
    """Fixture reprozip processes"""

    def create_process(command, inputs, outputs):
        return (
            mkstemp()[1], command, inputs, outputs
        )

    # Process 1
    process_1 = create_process(
        command = ["Rscript", "-e", "parallel_classification.R", "brick.tif"],
        inputs = ["process_1.tif"],
        outputs = ["process_1_out1.tif", "process_1_out2.tif"]
    )

    # Process 2
    process_2 = create_process(
        command = ["Rscript", "-e", "parallel_post_classification.R", "classification_map.tif"],
        inputs = ["process_1_out1.tif"],
        outputs = ["process_2_out1.tif"]
    )

    # Process 3
    process_3 = create_process(
        command = ["python3", "calc_zonal_statistics.py", "--data", "post_classification_map.tif"],
        inputs = ["process_1_out2.tif"],
        outputs = ["process_3_out1.tif"]
    )

    # Process 4
    process_4 = create_process(
        command = ["python3", "calc_temporal_statistics.py", "--data", "post_classification_map.tif"],
        inputs = ["process_2_out1.tif", "process_3_out1.tif"],
        outputs = ["process_4_out1.tif"]
    )

    return (process_1, process_2, process_3, process_4)


def test_when_4_process_is_added_to_graph_4_vertex_should_be_created(reprozip_processes):

    graph_manager = ExecutionGraphManager()

    graph_manager.add_vertex(*reprozip_processes[0])
    graph_manager.add_vertex(*reprozip_processes[1])
    graph_manager.add_vertex(*reprozip_processes[2])
    graph_manager.add_vertex(*reprozip_processes[3])

    assert len(graph_manager.vertices) == 4


def test_when_add_2_process_the_process1_should_be_connected_to_process2(reprozip_processes):

    graph_manager = ExecutionGraphManager()

    graph_manager.add_vertex(*reprozip_processes[0])
    graph_manager.add_vertex(*reprozip_processes[1])

    assert graph_manager.vertices[0].neighbors("out")[0].index == graph_manager.vertices[1].index


def test_when_add_3_process_the_process1_should_not_be_connected_to_process3(reprozip_processes):

    graph_manager = ExecutionGraphManager()

    graph_manager.add_vertex(*reprozip_processes[0])
    graph_manager.add_vertex(*reprozip_processes[1])
    graph_manager.add_vertex(*reprozip_processes[2])

    assert graph_manager.vertices[0].neighbors("out")[0].index != graph_manager.vertices[2].index


def test_when_add_2_process_disjoint_is_added_the_graph_should_have_no_edges(reprozip_processes):

    graph_manager = ExecutionGraphManager()

    graph_manager.add_vertex(*reprozip_processes[0])
    graph_manager.add_vertex(*reprozip_processes[3])

    assert len(graph_manager.vertices[0].neighbors("out")) == 0
    assert len(graph_manager.vertices[1].neighbors("out")) == 0


def test_when_vertex_is_added_sequentially_all_vertex_status_should_be_updated(reprozip_processes):
    graph_manager = ExecutionGraphManager()

    graph_manager.add_vertex(*reprozip_processes[0])
    graph_manager.add_vertex(*reprozip_processes[1])
    graph_manager.add_vertex(*reprozip_processes[2])
    graph_manager.add_vertex(*reprozip_processes[3])

    assert all(
        list(
            map(
                lambda status: status == VertexStatus.Updated, graph_manager.vertices["status"]
            )
        )
    )


def test_when_vertex_is_updated_all_subsequent_vertices_status_should_be_outdated(reprozip_processes):
    graph_manager = ExecutionGraphManager()

    graph_manager.add_vertex(*reprozip_processes[0])
    graph_manager.add_vertex(*reprozip_processes[1])
    graph_manager.add_vertex(*reprozip_processes[2])
    graph_manager.add_vertex(*reprozip_processes[3])

    # Update Process 3
    graph_manager.update_vertex(reprozip_processes[2][1], outputs=['process_3_out1.tif', 'stat_table.csv'])

    assert all(
        list(
            map(
                lambda status: status == VertexStatus.Outdated, graph_manager.vertices[3:]["status"]
            )
        )
    )


def test_when_try_updating_vertex_with_same_values_then_the_graph_should_not_be_updated(reprozip_processes):
    graph_manager = ExecutionGraphManager()

    graph_manager.add_vertex(*reprozip_processes[0])
    graph_manager.add_vertex(*reprozip_processes[1])
    graph_manager.add_vertex(*reprozip_processes[2])
    graph_manager.add_vertex(*reprozip_processes[3])

    # Update Process 2 with the same values
    graph_manager.update_vertex(reprozip_processes[1][1], inputs=reprozip_processes[1][2])

    assert all(
        list(
            map(
                lambda status: status == VertexStatus.Updated, graph_manager.vertices[2:]["status"]
            )
        )
    )


def test_when_try_add_a_already_added_vertex_with_same_values_then_the_graph_should_not_be_updated(reprozip_processes):
    graph_manager = ExecutionGraphManager()

    graph_manager.add_vertex(*reprozip_processes[0])
    graph_manager.add_vertex(*reprozip_processes[1])
    graph_manager.add_vertex(*reprozip_processes[2])
    graph_manager.add_vertex(*reprozip_processes[3])

    # (Re)Add Process 2 with the same values
    graph_manager.add_vertex(*reprozip_processes[1])

    assert all(
        list(
            map(
                lambda status: status == VertexStatus.Updated, graph_manager.vertices[2:]["status"]
            )
        )
    )


def test_when_try_add_a_already_added_vertex_with_different_values_then_the_graph_should_be_updated(reprozip_processes):
    graph_manager = ExecutionGraphManager()

    graph_manager.add_vertex(*reprozip_processes[0])
    graph_manager.add_vertex(*reprozip_processes[1])
    graph_manager.add_vertex(*reprozip_processes[2])
    graph_manager.add_vertex(*reprozip_processes[3])

    # (Re)Add Process 2 with the different values
    process_2 = reprozip_processes[1]
    graph_manager.add_vertex(*(
        process_2[0], process_2[1], [*process_2[2], "mynewfile.csv"], process_2[3]
    ))

    # Get vertex 4 (Process 2 dependent)
    process_4_command = reprozip_processes[3][1]
    process_4_vertex = graph_manager.vertices.select(command_checksum = multihash_checksum_sha256(process_4_command))

    assert process_4_vertex[0]["status"] == VertexStatus.Outdated
