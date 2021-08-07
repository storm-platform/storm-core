..
    This file is part of Brazil Data Cube Reproducible Research Management API.
    Copyright (C) 2021 INPE.

    Brazil Data Cube Reproducible Research Management API is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


Running bdcrrm-api on the Command Line Interface
===================================================

The `bdcrrm-api` provides a command-line tool called `bdcrrm-cli` that allows reproducible experiments' management, execution, and sharing. Below is a summary of the commands and functionalities that are available in the `bdcrrm-cli`.

**Project management commands**

+-------------------------------+------------------------------------------------------------------+
|            Command            |                            Description                           |
+-------------------------------+------------------------------------------------------------------+
|   `bdcrrm-cli project graph`  |                Manage the Project Execution Graph.               |
+-------------------------------+------------------------------------------------------------------+
|   `bdcrrm-cli project info`   |          Show general details about the current project.         |
+-------------------------------+------------------------------------------------------------------+
|   `bdcrrm-cli project init`   | Initialize a new Brazil Data Cube Reproducible Research project. |
+-------------------------------+------------------------------------------------------------------+
|  `bdcrrm-cli project inputs`  |       Manage the project required inputs for reproduction.       |
+-------------------------------+------------------------------------------------------------------+
| `bdcrrm-cli project settings` |                         Project Settings.                        |
+-------------------------------+------------------------------------------------------------------+
| `bdcrrm-cli project shipment` |               Commands to share the project.                     |
+-------------------------------+------------------------------------------------------------------+

**Project settings commands**

+---------------------------------------------------+------------------------------------+
|                      Command                      |             Description            |
+---------------------------------------------------+------------------------------------+
|       `bdcrrm-cli project settings secrets`       |           Project secrets          |
+---------------------------------------------------+------------------------------------+
|     `bdcrrm-cli project settings metadata-set`    |      Update project metadata.      |
+---------------------------------------------------+------------------------------------+
|     `bdcrrm-cli project settings datasources`     | Project settings for data sources. |
+---------------------------------------------------+------------------------------------+
| `bdcrrm-cli project settings working-directories` |    Project working directories.    |
+---------------------------------------------------+------------------------------------+

**Project Graph Management commands**

+------------------------------------------+---------------------------------------------+
|                  Command                 |                 Description                 |
+------------------------------------------+---------------------------------------------+
| `bdcrrm-cli project graph delete-vertex` |            Delete a graph vertex.           |
+------------------------------------------+---------------------------------------------+
|      `bdcrrm-cli project graph plot`     | Plot the project execution graph on a file. |
+------------------------------------------+---------------------------------------------+
|      `bdcrrm-cli project graph show`     |      Show the project execution graph.      |
+------------------------------------------+---------------------------------------------+

**Project required inputs commands**

+--------------------------------------+---------------------------------------------------------------------------------------------------------------+
|                Command               |                                                  Description                                                  |
+--------------------------------------+---------------------------------------------------------------------------------------------------------------+
|   `bdcrrm-cli project inputs list`   |                  Lists the inputs that are required to be defined  to reproduce this project.                 |
+--------------------------------------+---------------------------------------------------------------------------------------------------------------+
| `bdcrrm-cli project inputs template` | Create a template file to make it easier for the  user to specify the inputs needed to reproduce the project. |
+--------------------------------------+---------------------------------------------------------------------------------------------------------------+

**Reproducible experiment production commands**

+--------------------------------+----------------------------------------------------+
|             Command            |                     Description                    |
+--------------------------------+----------------------------------------------------+
|  `bdcrrm-cli production make`  | Execute an arbitrary command in a reproducible way |
+--------------------------------+----------------------------------------------------+
| `bdcrrm-cli production remake` |            (Re)Execute outdated commands           |
+--------------------------------+----------------------------------------------------+

**Experiment reproduction commands**

+--------------------------------+---------------------+
|             Command            |     Description     |
+--------------------------------+---------------------+
| `bdcrrm-cli reproduction make` | Reproduce a project |
+--------------------------------+---------------------+
