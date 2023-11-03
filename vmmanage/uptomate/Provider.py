LOCALHOST = "127.0.0.1"


class GenericProvider:
    name = ""
    port_forwarding = True

    @staticmethod
    def get_accessible_address(hostname):
        return LOCALHOST

    def __str__(self):
        # easier, since there is no need to differentiate between instances
        return self.__class__.__name__


class DockerComposeProvider(GenericProvider):
    pass


dc_provider = DockerComposeProvider()

ALLOWED_PROVIDERS = {
    "docker-compose": dc_provider,
}
