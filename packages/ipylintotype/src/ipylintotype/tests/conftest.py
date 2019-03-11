# type: ignore
import typing as typ

import pytest
from ipykernel.comm import Comm
from ipywidgets import Widget

LogArgs = typ.List[typ.Tuple[typ.List[typ.Any], typ.Dict[typ.Text, typ.Any]]]


class MockComm(Comm):
    """A mock Comm object.

    Can be used to inspect calls to Comm's open/send/close methods.
    """

    comm_id = "a-b-c-d"
    kernel = "Truthy"
    log_open: LogArgs
    log_send: LogArgs
    log_close: LogArgs

    def __init__(self, target_name: typ.Text = ""):
        self.log_open = []
        self.log_send = []
        self.log_close = []
        super(MockComm, self).__init__(target_name)

    def open(self, *args, **kwargs):
        self.log_open.append((args, kwargs))

    def send(self, *args, **kwargs):
        self.log_send.append((args, kwargs))

    def close(self, *args, **kwargs):
        self.log_close.append((args, kwargs))


_widget_attrs = {}
undefined = object()


@pytest.fixture
def mock_comm() -> typ.Iterator[Comm]:
    _widget_attrs["_comm_default"] = getattr(Widget, "_comm_default", undefined)
    Widget._comm_default = lambda self: MockComm()  # type: ignore
    _widget_attrs["_ipython_display_"] = Widget._ipython_display_

    def raise_not_implemented(*args, **kwargs):
        raise NotImplementedError()

    Widget._ipython_display_ = raise_not_implemented

    yield MockComm()

    for attr, value in _widget_attrs.items():
        if value is undefined:
            delattr(Widget, attr)
        else:
            setattr(Widget, attr, value)
