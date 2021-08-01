#
# This file is part of Brazil Data Cube Reproducible Research Management CLI.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube Reproducible Research Persistence Operations."""

import os
import pickle
import shutil
from tempfile import mkdtemp
from typing import Dict, Union, Tuple

import bagit
from igraph import Graph

from .config import GraphPersistenceConfig, EnvironmentConfig, ProjectConfig
from .hasher import multihash_checksum_sha256
from .project import Project


class GraphPersistencePickle(object):
    """Graph persistence using pickle."""

    @staticmethod
    def save_graph(graph, directory) -> None:
        """Save a graph to a persistence store into a pickle file.

        Args:
            graph (igraph.Graph): Graph to be saved.

            directory (str): Directory where the `meta` graph file will be saved.

        Returns:
            None: Graph is saved to a persistence store.
        """
        graph.write_pickle(os.path.join(directory, GraphPersistenceConfig.GRAPH_DEFAULT_PICKLE_NAME))

    @staticmethod
    def load_graph(directory) -> Union[Graph, None]:
        """Load a graph from a persistence store.

        Args:
            directory (str): Directory where the `meta` graph file is located.

        Returns:
            igraph.Graph: Graph loaded from a persistence store.
        """
        # ToDo: Review this return
        try:
            return Graph.Read_Pickle(os.path.join(directory, GraphPersistenceConfig.GRAPH_DEFAULT_PICKLE_NAME))
        except:
            return None


class BagItExporter(object):
    """Exporter to save a project into a BagIt organization."""

    @staticmethod
    def load_bagit(project_file: str, base_directory: str, processes: int = 1) -> Tuple[str, str]:
        """Import already finished `bdcrrm` project.

        Args:
            project_file (str): path to the finalized project zip file.

            base_directory (str): directory where the project will be extracted.

            processes (int): Number of processes used to validate the `bagit` file.

        Returns:
            Tuple[str, str]: Tuple with the project name and the path to the imported files.
        """
        # extract and validate bagit
        tmp_dir = mkdtemp()

        shutil.unpack_archive(project_file, tmp_dir)

        # validate bagit
        bag = bagit.Bag(tmp_dir)
        bag.validate(processes=processes)

        # load the project definition file
        exported_files = os.path.join(tmp_dir, "data")

        project_path = os.path.join(exported_files, ProjectConfig.PROJECT_DEFAULT_FILENAME)
        project_definition = Project.load(open(project_path, "r"))

        # move to the new folder
        base_project_path = os.path.join(base_directory, project_definition.metadata.name)
        project_metadata_path = os.path.join(base_project_path, EnvironmentConfig.REPROPACK_BASE_PATH)

        shutil.move(exported_files, project_metadata_path)
        return project_definition.metadata.name, base_project_path

    @staticmethod
    def save_bagit(project_name: str, project_meta_dir: str, output_dir: str, hashing_processes: int = 1) -> str:
        """Export an analysis project to a BagIt zip file.

        Args:
            project_name (str): Name of the project to be exported.

            project_meta_dir (str): Directory where the project is located.

            output_dir (str): Directory where the project will be exported.

            hashing_processes (int): Number of processes to use for hashing files.

        Returns:
            str: Path to the exported bagit zip file.

        See:
            The BagIt File Packaging Format (V1.0): https://www.ietf.org/rfc/rfc8493.txt
        """
        tmp_directory = os.path.join(mkdtemp(), "bdcrrm")
        shutil.copytree(project_meta_dir, tmp_directory)

        # do bagit!
        bagit.make_bag(tmp_directory, processes=hashing_processes)

        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, project_name)

        shutil.make_archive(output_path, "zip", tmp_directory)
        return output_path


class FilesPersistencePickle(object):
    """Files persistence using pickle."""

    @staticmethod
    def load_files(project_metadata_dir: str) -> Dict:
        """Load the list of files used in the experiments and not made available in the packages.

        Args:
            project_metadata_dir (str): Project metadata directory

        Returns:
            Dict: A dictionary with the `files` and `checksum` keys. Each of these keys represents, respectively, the
            list of files and their checksums.

        Note:
            If the `files` file in the project's metadata directory is not identified, the function will return the
            dictionary, with the same fields, but without content.
        """
        files_pickle_path = os.path.join(project_metadata_dir, EnvironmentConfig.REPROPACK_FILES_REFERENCE_PATH)

        # check pickle and load
        files_already_added = {"checksum": {}, "files": []}
        if os.path.isfile(files_pickle_path):
            with open(files_pickle_path, "rb") as ifile:
                files_already_added = pickle.load(ifile)
        return files_already_added

    @staticmethod
    def save_files(files: Dict, project_metadata_dir: str) -> None:
        """Export the reference to the files that have been removed from the ReproZip package.

        Args:
            files (Dict[str]): Name of the project to be exported.

            project_metadata_dir (str): Project metadata directory
        Returns:
            None: The `files` are dumped to a pickle file.
        """
        files_already_added = FilesPersistencePickle.load_files(project_metadata_dir)
        files_pickle_path = os.path.join(project_metadata_dir, EnvironmentConfig.REPROPACK_FILES_REFERENCE_PATH)

        for key in files.keys():
            currently_files = files.get(key)

            if currently_files:  # Sometimes a particular filter may not remove any files.
                # generating checksum.
                files_already_added["checksum"].update({os.path.basename(file):
                                                            multihash_checksum_sha256(file)
                                                        for file in currently_files})

                # generating `files_reference` structure (with ReproZip required filename)
                for currently_file in currently_files:
                    files_already_added["files"].append({
                        "source": os.path.basename(currently_file),
                        "target": ""
                    })

        # removing duplicated files
        files_already_added["files"] = [dict(t) for t in {tuple(d.items()) for d in files_already_added["files"]}]

        # writing the updated pickle the new version
        with open(files_pickle_path, "wb") as ofile:
            pickle.dump(files_already_added, ofile)


__all__ = (
    "BagItExporter",
    "GraphPersistencePickle",
    "FilesPersistencePickle"
)
