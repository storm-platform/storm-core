#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Docker Environment Manager."""

import docker.models.containers

import docker


def _connect_to_docker_daemon() -> docker.DockerClient:
    """Connect to the docker daemon using the Docker environment variables.

    To connect to the Docker Daemon, this function uses the following environment variables:
     - `DOCKER_HOST`: The URL to the Docker host.
     - `DOCKER_TLS_VERIFY`: Verify the host against a CA certificate.
     - `DOCKER_CERT_PATH`: A path to a directory containing TLS certificates to use when connecting to the Docker host.
    Returns:
        docker.DockerClient: A client configured from environment variables.
    See:
        For more information about DockerClient and the information used to connect to the Docker Daemon, please
        refer to the Docker SDK for Python documentation: https://docker-py.readthedocs.io/en/stable/client.html
    """
    return docker.from_env(timeout=None)


def run_container(**kwargs):
    """Run Docker Container on Host Machine Docker Daemon.

    Args:
        kwargs (dict): Arguments to the `client.containers.run` function from `Docker SDK`

    See:
        https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.ContainerCollection.run
    """
    client = _connect_to_docker_daemon()
    return client.containers.run(**kwargs)


def export_container(container_obj: docker.models.containers.Container, output_file: str):
    """Export Docker Container from the Host Machine Docker Daemon.

    Args:
        container_obj (docker.models.containers.Container): Object of the container that will be exported.

        output_file (str): full path to the tar file where container will be exported.

    Returns:
        None: Container will be saved on `output_file`.

    See:
        https://docker-py.readthedocs.io/en/stable/containers.html?highlight=export#docker.models.containers.Container.export
    """
    with open(output_file, "wb") as ofile:
        for chunk in container_obj.export():
            ofile.write(chunk)


def remove_image(image_name: str, force=True, noprune=False):
    """Remove a Docker Image from the Host Machine Docker Daemon.

    Args:
        image_name (str): Name of the image that will be removed.

        force (bool): Force removal of the image

        noprune (bool): Do not delete untagged parents

    Returns:
        None: Image will be deleted on Docker Daemon.

    See:
        https://docker-py.readthedocs.io/en/stable/containers.html?highlight=export#docker.models.containers.Container.export
    """
    client = _connect_to_docker_daemon()
    client.images.remove(image_name, force=force, noprune=noprune)


def import_image_from_tarfile(tarfile: str, repository: str, tag="latest"):
    """Import a Docker Image to the Host Machine Docker Daemon from a tarfile.

    Args:
        tarfile (str): Full path to the tarfile that will be imported.

        repository (str): Image name

        tag (str): Image tag

    Returns:
        None: Image will be imported to the Docker Daemon.

    See:
        https://docker-py.readthedocs.io/en/stable/containers.html?highlight=export#docker.models.containers.Container.export
    """
    client = _connect_to_docker_daemon()
    return client.api.import_image_from_file(tarfile, repository=repository, tag=tag)
