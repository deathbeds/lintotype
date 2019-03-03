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
                # TODO: implement this
                all_code:
                    text/x-ipython:
                        - id: abc1234
                        - code: |-
                            x = 1
                            x + 1
                metadata:
                    mypy:
                        foo: bar
            Send format:

                id: 1234
                annotations:
                    text/x-ipython:
                    - message: bad type thing
                      severity: error
                      from:
                        line: 1
                        col: 1
                      to:
                        line: 1
                        col: 2

            # DISCUSS
            - should these just be embedded Language Server Protocol schema?

              > https://microsoft.github.io/language-server-protocol/specification#textDocument_publishDiagnostics

                id: 4567
                codeActions:
                    text/python:
                    - {} # schema-enforced thing


        """
        data = msg["content"]["data"]
        annotation_results = [
            linter(
                code=data["code"],
                all_code=data.get("all_code", {}),
                metadata=data.get("metadata", {}),
            )
            for linter in LINTERS
        ]

        anno_bundle = {}

        for result in annotation_results:
            for mimetype, results in result.items():
                anno_bundle.setdefault(mimetype, []).extend(results)

        COMM.send(dict(id=data["id"], annotations=anno_bundle))


def unload_ipython_extension(ipython):
    global COMM
    if COMM:
        COMM.close()
        COMM = None
