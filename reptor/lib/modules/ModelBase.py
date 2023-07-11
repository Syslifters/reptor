import json


class ModelBase:
    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return json.dumps(
            self.__dict__,
            indent=2,
            default=str,
        )

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)
