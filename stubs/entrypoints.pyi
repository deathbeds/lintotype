import typing as typ

_T = typ.TypeVar("_T")

class EntryPoint(typ.Generic[_T]):
    def load(self) -> _T: ...

def get_group_named(
    group: typ.Text, path: typ.Optional[typ.Text] = None
) -> typ.Dict[typ.Text, EntryPoint[_T]]: ...
