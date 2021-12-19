# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Storm Project.
#
# storm-core is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from igraph import Graph

from ..engine.executor.api import ExecutionPlan, CommandJob, CompendiumJob


class GraphMutator:
    @staticmethod
    def mutate_graph_to_execution_plan_by_outdated_compendia(
        graph, outdated_compendia, output_directory
    ):
        # parsing the outdated executions to a Graph
        outdated_graph = Graph(directed=True)

        # adding vertices
        for outdated_compendium in outdated_compendia:
            command_job = CommandJob(
                outdated_compendium.command, output_directory, outdated_compendium.name
            )
            outdated_graph.add_vertex(name=outdated_compendium.name, job=command_job)

        # adding edges
        for vertex_src in outdated_graph.vs:

            # searching for the outdated_graph in the original graph
            vertex_src_original = graph.vs.select(name=vertex_src["name"])[
                0
            ]  # should exists!

            for vertex_predecessor_idx in graph.predecessors(vertex_src_original):
                vertex_predecessor = graph.vs[vertex_predecessor_idx]

                # check if the predecessor is in the outdated graph
                vertex_predecessor_outdated = outdated_graph.vs.select(
                    name=vertex_predecessor["name"]
                )

                if vertex_predecessor_outdated:
                    vertex_predecessor_outdated = vertex_predecessor_outdated[-1]

                    outdated_graph.add_edge(vertex_predecessor_outdated, vertex_src)
        # generating the execution plan
        return ExecutionPlan(outdated_graph) if outdated_graph.vs else None

    @staticmethod
    def mutate_index_graph_to_compendia_job_graph(
        graph, output_directory, current_compendia
    ) -> ExecutionPlan:
        # mutating the compendium graph to a job graph
        job_graph = Graph(directed=True)

        for ec, status in current_compendia:
            compendium_job = CompendiumJob(ec, output_directory=output_directory)

            job_graph.add_vertex(name=compendium_job.execution_id, job=compendium_job)

        # creating the edges
        for original_vertex in graph.vs:

            job_vertex = job_graph.vs.select(name=original_vertex["name"])[0]
            for vertex_predecessor in original_vertex.predecessors():
                job_vertex_predecessor = job_graph.vs.select(
                    name=vertex_predecessor["name"]
                )[0]

                job_graph.add_edge(job_vertex_predecessor, job_vertex)

        # generating the execution plan
        return ExecutionPlan(job_graph) if job_graph.vs else None


__all__ = "GraphMutator"
