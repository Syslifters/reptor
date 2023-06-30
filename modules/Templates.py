from classes.Base import Base
from api.TemplatesAPI import TemplatesAPI


class Templates(Base):
    """
    Queries Server for Finding Templates


    Sample commands:
        reptor templates
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.arg_search = kwargs.get('search')

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)
        templates_parsers = parser.add_argument_group()
        templates_parsers.add_argument("--search",
                                        help="Search for term",
                                        action="store",
                                        default=None)

    def run(self):
        template_api : TemplatesAPI = TemplatesAPI()
        if not self.arg_search:
            templates = template_api.get_templates()
        else:
            templates = template_api.search(self.arg_search)

        print(f"{'Title':<30} ID")
        print(f"{'_':_<80}")
        for template in templates:
            data = template['data']
            print(
                f"{data['title']:<30} {template['id']}")
            print(f"{'_':_<80}")


loader = Templates
