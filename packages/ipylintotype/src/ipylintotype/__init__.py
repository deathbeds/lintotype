import IPython

from ._version import __comm__
from .annotators.annotator import Annotator  # noqa
from .formatter import AnnotationFormatter

LINTOTYPE = None


def load_ipython_extension(shell):
    global LINTOTYPE
    unload_ipython_extension(shell)
    LINTOTYPE = AnnotationFormatter(parent=IPython.get_ipython())


def unload_ipython_extension(shell):
    global LINTOTYPE
    if LINTOTYPE:
        LINTOTYPE.close()


def get_ipylintotype():
    return LINTOTYPE


if __name__ == "__main__":
    load_ipython_extension(IPython.get_ipython())
