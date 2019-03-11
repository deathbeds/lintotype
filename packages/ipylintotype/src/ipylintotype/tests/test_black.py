import typing as typ

import IPython
import pytest

from .. import shapes
from ..diagnosers.black_diagnoser import BlackDiagnoser, InteractiveShell


@pytest.fixture
def diagnoser() -> BlackDiagnoser:
    return BlackDiagnoser()


@pytest.fixture
def shell() -> InteractiveShell:
    return IPython.get_ipython()


@pytest.fixture
def minimal_black_code() -> typ.List[shapes.Cell]:
    return [dict(cell_id="1", code="x = 1")]


@pytest.fixture
def minimal_not_black_code() -> typ.List[shapes.Cell]:
    return [dict(cell_id="1", code="x = (\n1\n)")]


def test_diagnoser(
    diagnoser: BlackDiagnoser,
    shell: InteractiveShell,
    minimal_black_code: typ.List[shapes.Cell],
    minimal_not_black_code: typ.List[shapes.Cell],
) -> None:
    result = diagnoser.run(
        cell_id="1", code=minimal_black_code, metadata={}, shell=shell
    )
    assert not result
    result = diagnoser.run(
        cell_id="1", code=minimal_not_black_code, metadata={}, shell=shell
    )
    observed = result["code_actions"][0]["edit"]["changes"]["1"][0]["newText"]
    assert observed == minimal_black_code[0]["code"]
