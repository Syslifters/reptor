from core.conf import Config


class Reptor:
    _config: Config

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Reptor, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self._load_config()

        self._load_system_modules()

        # if config[community_modules_enabled]
        self._load_community_modules()

        self._configure_global_arguments()

    def get_config(self) -> Config:
        return self._config

    def _load_config(self) -> None:
        """Load the config into Reptor"""
        ...

    def _load_system_modules(self) -> None:
        """Loads the official modules"""
        self._config = Config()

    def _load_community_modules(self) -> None:
        ...

    def _configure_global_arguments(self) -> None:
        """Enables the parameters
        - project_id
        - verbose
        - insecure
        """
        ...

    def run(self, *args, **kwargs) -> None:
        ...
