import docker


class DockerInterface(object):
    """
    This class servers as an interface to Docker.
    """
    def __init__(self, api_version='1.24'):
        self.api_version = api_version
        self.docker_client = docker.from_env(version=self.api_version)

    def get_docker_images(self):
        """
        This method gets a list of Docker images.
        :return: List of Docker images.
        """
        list_of_docker_images = list()
        docker_images = self.docker_client.images.list(all=True)
        for image in docker_images:
            for image_tag in image.tags:
                list_of_docker_images.append(image_tag)
        return list_of_docker_images

    def get_docker_containers(self):
        """
        This method gets a list of Docker containers.
        :return: List of Docker containers.
        """
        list_of_docker_containers = list()
        docker_containers = self.docker_client.containers.list(all=True)
        for container in docker_containers:
            list_of_docker_containers.append(container.name)
        return list_of_docker_containers

    def stop_container(self, container_name):
        """
        This method stops a Docker container by the given container name.
        :param container_name: The Docker container to stop.
        :return: True if container was stopped; false otherwise.
        """
        ret_val = False
        for container in self.docker_client.containers.list(all=True):
            if container.name == container_name:
                try:
                    container.stop()
                    ret_val = True
                except Exception as stop_exception:
                    raise StandardError(stop_exception)
        return ret_val

    def restart_container(self, container_name):
        """
        This method restarts a Docker container by the given container name.
        :param container_name: The Docker container to restarts.
        :return: True if container was stopped; false otherwise.
        """
        ret_val = False
        for container in self.docker_client.containers.list(all=True):
            if container.name == container_name:
                try:
                    container.restart()
                    ret_val = True
                except Exception as restart_exception:
                    raise StandardError(restart_exception)
        return ret_val