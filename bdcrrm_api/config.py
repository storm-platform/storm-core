#
# This file is part of Brazil Data Cube Reproducible Research Management CLI.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Management CLI Configurations."""


class ProjectConfig:
    """Project configuration."""

    PROJECT_DEFAULT_FILENAME = "project.yml"


class EnvironmentConfig:
    """Base configuration."""

    REPROPACK_BASE_PATH = ".bdcrrm"
    REPROPACK_EXEC_PATH = "executions"


class GraphPersistenceConfig:
    """Graph Persistence configuration."""

    GRAPH_DEFAULT_PICKLE_NAME = "meta"  # frozen
