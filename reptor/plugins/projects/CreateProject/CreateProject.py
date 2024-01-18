from reptor.lib.plugins.Base import Base


class CreateProject(Base):
    """
    Create a new pentest project
    """

    meta = {
        "name": "CreateProject",
        "summary": "Create a new pentest project",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name: str = kwargs.get("name") or "New Project created with Reptor"
        self.design: str = kwargs.get("design") or ""
        self.tags: list = ["reptor"]
        tags = kwargs.get("tags")
        if tags:
            self.tags.extend(tags.split(","))
        self.no_update_config: bool = kwargs.get("no_update_config", False)

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath=plugin_filepath)
        parser.add_argument(
            "--name",
            "-n",
            metavar="PROJECT NAME",
            help="Project name",
            action="store",
            default=None,
        )
        parser.add_argument(
            "--design",
            "-d",
            metavar="DESIGN ID",
            help="Design UUID for the project",
            action="store",
            required=True,
        )
        parser.add_argument(
            "--tags",
            "-t",
            metavar="TAGS",
            help="Comma-separated project tags",
            action="store",
            default=None,
        )
        parser.add_argument(
            "--no-update-config",
            action="store_true",
            help="Do not update project ID in config file",
            dest="no_update_config",
        )

    def run(self):
        project = self.reptor.api.projects.create_project(
            name=self.name,
            project_design=self.design,
            tags=self.tags,
        )
        self.success(
            f'Successfully created "{self.name}" project with ID "{project.id}".'
        )

        if self.no_update_config:
            return
        config_from_file = self.reptor._config.load_config(return_only=True)
        config_from_file["project_id"] = project.id
        if config_from_file:
            self.reptor._config._write_to_file(config=config_from_file)
        self.display("Updated project ID in config file.")


loader = CreateProject
