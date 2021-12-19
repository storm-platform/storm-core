..
    Copyright (C) 2021 Storm Project.

    storm-project is free software; you can redistribute it and/or modify
    it under the terms of the MIT License; see LICENSE file for more details.


Running Storm Core on the Command Line Interface
===================================================

The `Storm Core` provides a command-line tool called `storm-core` that allows reproducible experiments' management, execution, and sharing. Below is a summary of the commands and functionalities that are available in the `storm-core`.

**Project management commands**

+-------------------------------+------------------------------------------------------------------+
|            Command            |                            Description                           |
+-------------------------------+------------------------------------------------------------------+
|   `storm-core project graph`  |                Manage the Project Execution Graph.               |
+-------------------------------+------------------------------------------------------------------+
|   `storm-core project info`   |          Show general details about the current project.         |
+-------------------------------+------------------------------------------------------------------+
|   `storm-core project init`   | Initialize a new Brazil Data Cube Reproducible Research project. |
+-------------------------------+------------------------------------------------------------------+
|  `storm-core project inputs`  |       Manage the project required inputs for reproduction.       |
+-------------------------------+------------------------------------------------------------------+
| `storm-core project settings` |                         Project Settings.                        |
+-------------------------------+------------------------------------------------------------------+
| `storm-core project shipment` |               Commands to share the project.                     |
+-------------------------------+------------------------------------------------------------------+

**Project settings commands**

+---------------------------------------------------+------------------------------------+
|                      Command                      |             Description            |
+---------------------------------------------------+------------------------------------+
|       `storm-core project settings secrets`       |           Project secrets          |
+---------------------------------------------------+------------------------------------+
|     `storm-core project settings metadata-set`    |      Update project metadata.      |
+---------------------------------------------------+------------------------------------+
|     `storm-core project settings datasources`     | Project settings for data sources. |
+---------------------------------------------------+------------------------------------+
| `storm-core project settings working-directories` |    Project working directories.    |
+---------------------------------------------------+------------------------------------+

**Project Graph Management commands**

+------------------------------------------+---------------------------------------------+
|                  Command                 |                 Description                 |
+------------------------------------------+---------------------------------------------+
| `storm-core project graph delete-vertex` |            Delete a graph vertex.           |
+------------------------------------------+---------------------------------------------+
|      `storm-core project graph plot`     | Plot the project execution graph on a file. |
+------------------------------------------+---------------------------------------------+
|      `storm-core project graph show`     |      Show the project execution graph.      |
+------------------------------------------+---------------------------------------------+

**Project required inputs commands**

+--------------------------------------+---------------------------------------------------------------------------------------------------------------+
|                Command               |                                                  Description                                                  |
+--------------------------------------+---------------------------------------------------------------------------------------------------------------+
|   `storm-core project inputs list`   |                  Lists the inputs that are required to be defined  to reproduce this project.                 |
+--------------------------------------+---------------------------------------------------------------------------------------------------------------+
| `storm-core project inputs template` | Create a template file to make it easier for the  user to specify the inputs needed to reproduce the project. |
+--------------------------------------+---------------------------------------------------------------------------------------------------------------+

**Reproducible experiment production commands**

+--------------------------------+----------------------------------------------------+
|             Command            |                     Description                    |
+--------------------------------+----------------------------------------------------+
|  `storm-core production make`  | Execute an arbitrary command in a reproducible way |
+--------------------------------+----------------------------------------------------+
| `storm-core production remake` |            (Re)Execute outdated commands           |
+--------------------------------+----------------------------------------------------+

**Experiment reproduction commands**

+--------------------------------+---------------------+
|             Command            |     Description     |
+--------------------------------+---------------------+
| `storm-core reproduction make` | Reproduce a project |
+--------------------------------+---------------------+
