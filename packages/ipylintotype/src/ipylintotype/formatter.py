import json
from pathlib import Path

import IPython
import traitlets
from ipykernel.comm import Comm
from jsonschema.validators import Draft4Validator

from ._version import __comm__

here = Path(__file__).parent
schemas = here / "schema"

request = Draft4Validator(
    json.loads((schemas / "lintotype.request.schema.json").read_text())
)
response = Draft4Validator(
    json.loads((schemas / "lintotype.response.schema.json").read_text())
)


class AnnotationFormatter(IPython.core.interactiveshell.InteractiveShell):
    diagnosers = traitlets.List()

    comm_name = traitlets.Unicode(default_value=__comm__)

    current_comm = traitlets.Any()

    validate = traitlets.Bool(True)

    @traitlets.default("diagnosers")
    def _default_diagnosers(self):
        """ TODO: need a cleaner way to add this... entry_points?
        """
        diagnosers = []
        try:
            from .diagnosers.mypy_diagnoser import MyPyDiagnoser

            diagnosers += [MyPyDiagnoser()]
        except ImportError:
            self.log.warn("mypy could not be imported")

        try:
            from .diagnosers.pylint_diagnoser import PyLintDiagnoser

            diagnosers += [PyLintDiagnoser()]
        except ImportError:
            self.log.warn("pylint could not be imported")

        return diagnosers

    def init_user_ns(self):
        ...

    def __init__(self, *args, **kwargs):
        if "parent" in kwargs:
            kwargs = {**kwargs["parent"]._trait_values, **kwargs}
        super().__init__(*args, **kwargs)
        self.init_comm()

    def init_comm(self):
        self.close()
        self.current_comm = Comm(target_name=self.comm_name)
        self.current_comm.on_msg(self.on_msg)
        __import__("atexit").register(AnnotationFormatter.close)

    def __call__(self, cell_id, code=None, metadata=None, *args):
        result = dict()
        for diagnoser in self.diagnosers:
            if not diagnoser.enabled:
                continue
            diagnoser_code = code.get(diagnoser.mimetype)
            if not diagnoser_code:
                continue
            try:
                diagnostics = diagnoser(
                    cell_id=cell_id,
                    code=code[diagnoser.mimetype],
                    metadata=metadata.get(diagnoser.mimetype, {}),
                    shell=self,
                )
                result.setdefault(diagnoser.mimetype, []).extend(diagnostics)
            except Exception as err:
                self.log.error(f"{diagnoser}: {err}\n{code}")
                self.log.exception(f"{diagnoser} failed")

        return result

    def close(self):
        if self.current_comm:
            self.current_comm.close()
        self.current_comm = None

    def on_msg(self, msg):
        data = msg["content"]["data"]

        if self.validate:
            try:
                request.validate(data)
                self.log.error("request ok")
            except Exception as err:
                self.log.error(err)

        request_id = data.get("request_id")
        cell_id = data.get("cell_id")

        if not request_id:
            return

        diagnostics = self(
            cell_id=cell_id,
            code=data.get("code", {}),
            metadata=data.get("metadata", {}),
        )
        msg = dict(cell_id=cell_id, request_id=request_id, diagnostics=diagnostics)

        if self.validate:
            try:
                response.validate(msg)
                self.log.error("msg ok")
            except Exception as err:
                self.log.warn(err)

        self.current_comm.send(msg)
