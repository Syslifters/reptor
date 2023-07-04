from core.modules.Base import Base


class Dummy(Base):
    """
    Just a dummy module inheriting from Base.
    """

    def __init__(self):
        print("init")


loader = Dummy
