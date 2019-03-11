import pytest
from IPython import get_ipython

import ipylintotype

from .. import get_ipylintotype, load_ipython_extension, unload_ipython_extension


def test_extension() -> None:
    load_ipython_extension(get_ipython())
    lt = ipylintotype.LINTOTYPE
    assert lt
    assert lt == get_ipylintotype()
    unload_ipython_extension(get_ipython())
    assert not lt.current_comm
    lt2 = ipylintotype.LINTOTYPE
    assert not lt2
    assert lt2 == get_ipylintotype()
