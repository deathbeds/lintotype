import typing as typ

_T = typ.TypeVar("_T")
_U = typ.TypeVar("_U")

class Validator:
    def __init__(self, schema: _T): ...
    def validate(self, instance: _U) -> None: ...

class Draft4Validator(Validator): ...
