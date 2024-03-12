from reptor.lib.plugins.UploadBase import UploadBase


class DeleteProjects(UploadBase):
    meta = {
        "name": "DeleteProjects",
        "summary": "Deletes projects by title",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title_contains = kwargs.get("title_contains") or ""
        self.exclude_title_contains = kwargs.get("exclude_title_contains") or ""
        self.no_dry_run = kwargs.get("no_dry_run")

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath=plugin_filepath)
        parser.add_argument(
            "--title-contains",
            metavar="SEARCHTERM",
            action="store",
            dest="title_contains",
            help="Match string in title",
        )
        parser.add_argument(
            "--exclude-title-contains",
            metavar="SEARCHTERM",
            action="store",
            dest="exclude_title_contains",
            help="Matched strings in title are not deleted",
        )
        parser.add_argument(
            "--no-dry-run",
            help="Do delete projects, default is dry-run",
            action="store_true",
        )

    def run(self):
        projects = self.reptor.api.projects.search(search_term=self.title_contains)
        matched = False
        for project in projects:
            if self.title_contains.lower() in project.name.lower():
                if (
                    self.exclude_title_contains
                    and self.exclude_title_contains.lower()
                    in project.name.lower()
                ):
                    continue
                matched = True
                if not self.no_dry_run:
                    self.display(f'Would delete project "{project.name}"')
                else:
                    self.reptor.api.projects.delete_project(project_id=project.id)
                    self.display(f"Deleted project {project.name}")

        if not matched:
            self.display("No projects matched.")
        elif not self.no_dry_run:
            self.display('\nDry-run, delete with "--no-dry-run".')


loader = DeleteProjects
