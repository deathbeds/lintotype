import typing as typ

import IPython
from IPython.core.interactiveshell import InteractiveShell

from ._version import __comm__
from .diagnosers.diagnoser import Diagnoser  # noqa
from .formatter import AnnotationFormatter

LINTOTYPE = typ.cast(AnnotationFormatter, None)


def load_ipython_extension(shell: InteractiveShell) -> None:
    global LINTOTYPE
    unload_ipython_extension(shell)
    LINTOTYPE = AnnotationFormatter(parent=IPython.get_ipython())


def unload_ipython_extension(shell: InteractiveShell) -> None:
    global LINTOTYPE
    if LINTOTYPE:
        LINTOTYPE.close()
    LINTOTYPE = typ.cast(AnnotationFormatter, None)


def get_ipylintotype() -> AnnotationFormatter:
    return LINTOTYPE


if __name__ == "__main__":
    load_ipython_extension(IPython.get_ipython())
