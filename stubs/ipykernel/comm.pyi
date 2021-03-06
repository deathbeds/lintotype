import typing as typ

_T = typ.TypeVar("_T")
_U = typ.TypeVar("_U")

class Comm(typ.Generic[_T, _U]):
    def __init__(self, target_name: typ.Text): ...
    def on_msg(self, handler: typ.Callable[[_T], None]) -> None: ...
    def close(self) -> None: ...
    def send(self, msg: _U) -> None: ...
