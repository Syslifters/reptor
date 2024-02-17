import typing


class UserConfig:
    name: str
    friendly_name: str
    type: typing.Type
    callback: typing.Optional[typing.Callable]
    redact_current_value: bool = False

    def __init__(
        self,
        name: str,
        friendly_name: str,
        callback: typing.Optional[typing.Callable] = None,
        redact_current_value: bool = False,
    ):
        self.name = name
        self.friendly_name = friendly_name
        self.callback = callback
        self.redact_current_value = redact_current_value

    @staticmethod
    def split(value: str, separator=",") -> typing.List[str]:
        return list(filter(None, value.split(separator)))
