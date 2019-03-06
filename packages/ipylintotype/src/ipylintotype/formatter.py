import json
from collections import defaultdict
from pathlib import Path

import IPython
import traitlets
from entrypoints import get_group_named
from ipykernel.comm import Comm
from jsonschema.validators import Draft4Validator

from ._version import __comm__, __ep__

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
        for name, ep in get_group_named(__ep__).items():
            try:
                diagnosers.append(ep.load()())
            except Exception as err:
                self.log.warn("%s Load error %s", name, err)

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
        # TODO type this or something
        result = {}

        for diagnoser in self.diagnosers:
            if not diagnoser.enabled:
                continue

            mime = diagnoser.mimetype
            mime_code = code.get(mime)
            mime_meta = metadata.get(mime, {})

            if not mime_code:
                continue
            try:
                annotations = diagnoser(
                    cell_id=cell_id, code=mime_code, metadata=mime_meta, shell=self
                )
                for anno_type, annos in annotations.items():
                    result.setdefault(mime, {}).setdefault(anno_type, []).extend(annos)
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
            except Exception as err:
                self.log.warn("Request Validation Error:\n%s", err)

        request_id = data.get("request_id")
        cell_id = data.get("cell_id")

        if not request_id:
            return

        annotations = self(
            cell_id=cell_id,
            code=data.get("code", {}),
            metadata=data.get("metadata", {}),
        )
        msg = dict(cell_id=cell_id, request_id=request_id, annotations=annotations)

        if self.validate:
            try:
                response.validate(msg)
            except Exception as err:
                self.log.warn("Response Validation Error:\n%s", err)

        self.current_comm.send(msg)
