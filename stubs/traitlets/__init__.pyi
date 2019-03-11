import typing as typ

_T = typ.TypeVar("_T")
_U = typ.TypeVar("_U")

# the traitlets
def Unicode(
    default_value: typ.Text = None, help: typ.Text = None, allow_none: bool = False
) -> typ.Text: ...
def Bool(
    default_value: bool = None, help: typ.Text = None, allow_none: bool = False
) -> bool: ...
def Integer(
    default_value: int = None, help: typ.Text = None, allow_none: bool = False
) -> int: ...
def Instance(
    klass: typ.Callable[..., _T],
    default_value: _T = None,
    help: typ.Text = None,
    allow_none: bool = False,
) -> _T: ...
def Any(
    default_value: typ.Any = None, help: typ.Text = None, allow_none: bool = False
) -> typ.Any: ...
def List(
    klass: _T = None, default_value: typ.List[_T] = [], help: typ.Text = None
) -> typ.List[_T]: ...

# traitful things
class HasTraits(object):
    def traits(self) -> typ.Dict[typ.Text, typ.Any]: ...

# linking
class _link_base(object):
    def link(self) -> None: ...
    def unlink(self) -> None: ...

class link(_link_base):
    def __init__(
        self,
        source: typ.Tuple[HasTraits, str],
        target: typ.Tuple[HasTraits, str],
        transform: typ.Tuple[typ.Callable[[_T], _U], typ.Callable[[_U], _T]] = None,
    ): ...

class directional_link(_link_base):
    def __init__(
        self,
        source: typ.Tuple[HasTraits, str],
        target: typ.Tuple[HasTraits, str],
        transform: typ.Callable[[_U], _T] = ...,
    ): ...

dlink = directional_link

class BaseDescriptor: ...
class TraitType(BaseDescriptor): ...
class EventHandler(BaseDescriptor): ...
class ObserveHandler(EventHandler): ...
class ValidateHandler(EventHandler): ...

class DefaultHandler(EventHandler):
    def __init__(self, name: typ.Text): ...
    def __call__(self, decorated: typ.Callable[[_U], _T]): ...

# sugar
def default(name: typ.Text) -> DefaultHandler: ...
