import typing as typ

import ipywidgets as W
import pytest

from .. import Diagnoser
from ..diagnosers.black_diagnoser import BlackDiagnoser
from ..diagnosers.flake8_diagnoser import Flake8Diagnoser
from ..diagnosers.mypy_diagnoser import MyPyDiagnoser
from ..diagnosers.pylint_diagnoser import PyLintDiagnoser
from ..widgets import show_diagnoser, show_formatter


@pytest.mark.parametrize("klazz", [MyPyDiagnoser, Flake8Diagnoser, BlackDiagnoser])
def test_example_creation_blank(klazz: typ.Callable[[], Diagnoser]) -> None:
    w = show_diagnoser(klazz())
    assert isinstance(w, W.DOMWidget)
