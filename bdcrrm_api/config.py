#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Management CLI Configurations."""
from .graph_executor import ReproParaDAGParallelTopologicalExecutor


class ProjectConfig:
    """Project configuration."""

    PROJECT_DEFAULT_FILENAME = "project.yml"


class EnvironmentConfig:
    """Base configuration."""

    REPROPACK_BASE_PATH = ".bdcrrm"
    REPROPACK_EXEC_PATH = "executions"
    REPROPACK_RESULT_PATH = "results"

    REPROPACK_FILES_REFERENCE_PATH = "files"


class GraphPersistenceConfig:
    """Graph Persistence configuration."""

    GRAPH_DEFAULT_PICKLE_NAME = "meta"


class GraphStyleConfig:
    """Graph Style configuration."""

    GRAPH_DEFAULT_VERTICES_COLOR = {
        "updated": "green",
        "outdated": "yellow"
    }


class ExecutionEngineConfig:
    """Execution engine configuration."""

    DEFAULT_GRAPH_EXECUTOR_CLASS = ReproParaDAGParallelTopologicalExecutor
