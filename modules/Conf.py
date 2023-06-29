from classes.ConfBase import ConfBase
from utils.conf import get_config_from_user


class Conf(ConfBase):
    """
    enter config interactively and store to file
    """

    def run(self):
        get_config_from_user()


loader = Conf
