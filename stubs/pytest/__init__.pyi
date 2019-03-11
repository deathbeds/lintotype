import typing as typ
from contextlib import ContextManager

from . import mark

_T = typ.TypeVar("_T")

def fixture(*args, **kwargs) -> typ.Any: ...
def raises(exception: typ.Callable[[], _T]) -> ContextManager[_T]: ...
