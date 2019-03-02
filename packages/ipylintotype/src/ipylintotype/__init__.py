import IPython
from ipykernel.comm import Comm
from tornado import ioloop

from ._version import __comm__
from .linters import LINTERS

# TODO: make a manager
COMM = None


def load_ipython_extension(ipython):
    global COMM
    COMM = Comm(target_name=__comm__)

    @COMM.on_msg
    def _recv(msg):
        data = msg["content"]["data"]
        annotations = sum([linter(data["code"]) for linter in LINTERS], [])
        COMM.send(dict(id=data["id"], annotations=annotations))


def unload_ipython_extension(ipython):
    global COMM
    COMM.close()
    COMM = None
