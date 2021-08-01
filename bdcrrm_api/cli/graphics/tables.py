#
# This file is part of Brazil Data Cube Reproducible Research Management CLI.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Command-Line Interface Table Graphics."""

# from rich.console import Console
# from rich.table import Table
#
# from bdcrrm_api.graph import VertexStatus
#
#
# def show_table_execution_graph_status(graph_df: 'pandas.core.frame.DataFrame'):
#     table = Table(title="[bold]Execution Vertex Status[/bold]:", title_justify="left")
#
#     # Preparing table columns
#     table.add_column("Vertex ID", justify="center")
#     table.add_column("Command", justify="center")
#     table.add_column("Status", justify="center")
#
#     status_color = {
#         VertexStatus.Updated: "green",
#         VertexStatus.Outdated: "yellow",
#         VertexStatus.Invalid: "red"
#     }
#
#     status_color_template = "[bold {color}]{status}:heavy_check_mark:"
#
#     # add rows
#     for _, row in graph_df.iterrows():
#         # defining status style based on value
#         row_status = row.status[0]
#         row_status_color = status_color[row_status]
#
#         table.add_row(
#             str(row.name), row.command, status_color_template.format(color=row_status_color, status=row_status)
#         )
#
#     console = Console()
#     console.print(table)