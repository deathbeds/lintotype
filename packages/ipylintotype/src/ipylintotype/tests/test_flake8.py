import typing as typ

import IPython
import pytest

from .. import shapes
from ..diagnosers.flake8_diagnoser import Flake8Diagnoser, InteractiveShell


@pytest.fixture
def diagnoser() -> Flake8Diagnoser:
    return Flake8Diagnoser()


@pytest.fixture
def shell() -> InteractiveShell:
    return IPython.get_ipython()


@pytest.fixture
def minimal_unflaked_code() -> typ.List[shapes.Cell]:
    return [dict(cell_id="1", code="x = 1")]


@pytest.fixture
def minimal_flaked_code() -> typ.List[shapes.Cell]:
    return [dict(cell_id="1", code="x + y")]


def test_black_diagnoser(
    diagnoser: Flake8Diagnoser,
    shell: InteractiveShell,
    minimal_unflaked_code: typ.List[shapes.Cell],
    minimal_flaked_code: typ.List[shapes.Cell],
) -> None:
    result = diagnoser.run(
        cell_id="1", code=minimal_unflaked_code, metadata={}, shell=shell
    )
    assert not result["diagnostics"]
    result = diagnoser.run(
        cell_id="1", code=minimal_flaked_code, metadata={}, shell=shell
    )
    assert result["diagnostics"]
