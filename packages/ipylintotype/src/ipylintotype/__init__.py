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
        """ A description of the current wire format (subject to change)

            Receive format:

                id: 1234  # client id, pretty opaque from the backend
                code: "x = 1\nx + 1"
                all_code:
                    application/python:
                        - "x = 1\nx + 1"
                metadata:
                    mypy:
                        foo: bar
            Send format:

                id: 1234
                annotations:
                - message: bad type thing
                  severity: error
                  from:
                    line: 1
                    col: 1
                  to:
                    line: 1
                    col: 2
        """
        data = msg["content"]["data"]
        annotations = sum([linter(data["code"]) for linter in LINTERS], [])
        COMM.send(dict(id=data["id"], annotations=annotations))


def unload_ipython_extension(ipython):
    global COMM
    if COMM:
        COMM.close()
        COMM = None
