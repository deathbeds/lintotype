import atexit
import json
import typing as typ
from collections import defaultdict
from pathlib import Path

import IPython
import traitlets
from entrypoints import EntryPoint, get_group_named
from ipykernel.comm import Comm
from jsonschema.validators import Draft4Validator

from . import shapes
from ._version import __comm__, __ep__
from .diagnosers.diagnoser import Diagnoser

here = Path(__file__).parent
schemas = here / "schema"

REQUEST = Draft4Validator(
    json.loads((schemas / "lintotype.request.schema.json").read_text())
)
RESPONSE = Draft4Validator(
    json.loads((schemas / "lintotype.response.schema.json").read_text())
)

if typ.TYPE_CHECKING:  # pragma: no cover
    LintotypeComm = Comm[shapes.Message, shapes.Response]


class AnnotationFormatter(IPython.core.interactiveshell.InteractiveShell):
    diagnosers = traitlets.List(traitlets.Instance(Diagnoser))
    comm_name = traitlets.Unicode(__comm__)
    current_comm = traitlets.Instance(Comm, allow_none=True)  # type: LintotypeComm
    validate = traitlets.Bool(True)

    @traitlets.default("diagnosers")
    def _default_diagnosers(self) -> typ.List[Diagnoser]:
        """ TODO: need a cleaner way to add this... entry_points?
        """
        diagnosers: typ.List[Diagnoser] = []
        eps = get_group_named(
            __ep__
        )  # type: typ.Dict[typ.Text, EntryPoint[typ.Callable[[], Diagnoser]]]

        for name, ep in eps.items():
            try:
                diagnosers.append(ep.load()())
            except Exception as err:
                self.log.warning("%s Load error %s", name, err)

        return diagnosers

    def init_user_ns(self) -> None:
        ...

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_comm()

    def init_comm(self) -> None:
        self.close()
        self.current_comm = Comm(target_name=self.comm_name)
        self.current_comm.on_msg(self.on_msg)
        atexit.register(lambda: self.close())

    def __call__(
        self, cell_id: typ.Text, code: shapes.MIMECode, metadata: shapes.Metadata, *args
    ) -> shapes.MIMEAnnotations:
        result: shapes.MIMEAnnotations = typ.cast(
            shapes.MIMEAnnotations, defaultdict(dict)
        )

        for diagnoser in self.diagnosers:
            if not diagnoser.enabled:
                continue

            mime = diagnoser.mimetype
            mime_code = code.get(mime)

            if not mime_code:
                continue

            mime_meta = metadata.get(mime, {})

            try:
                annotations = diagnoser.run(
                    cell_id=cell_id, code=mime_code, metadata=mime_meta, shell=self
                )
                for anno_type, annos in annotations.items():
                    mime_result = result.setdefault(
                        mime,
                        {"diagnostics": [], "code_actions": [], "markup_contexts": []},
                    )
                    if anno_type == "diagnostics":
                        mime_result["diagnostics"].extend(annos)  # type: ignore
                    elif anno_type == "code_actions":
                        mime_result["code_actions"].extend(annos)  # type: ignore
                    elif anno_type == "markup_contexts":
                        mime_result["markup_contexts"].extend(annos)  # type: ignore
            except Exception as err:
                self.log.error(f"{diagnoser}: {err}\n{code}")
                self.log.exception(f"{diagnoser} failed")

        return result

    def close(self) -> None:
        if self.current_comm:
            self.current_comm.close()
        self.current_comm = None  # type: ignore

    def on_msg(self, msg: shapes.Message) -> None:
        request = msg["content"]["data"]

        self.validate_request(request)

        try:
            request_id = request["request_id"]
            cell_id = request["cell_id"]
        except:
            return

        code = request.get("code", {})
        metadata = request.get("metadata", {})

        annotations = self(cell_id=cell_id, code=code, metadata=metadata)

        response: shapes.Response = dict(
            cell_id=cell_id, request_id=request_id, annotations=annotations, metadata={}
        )

        self.validate_response(response)

        if self.current_comm:
            self.current_comm.send(response)

    def validate_request(
        self, request: shapes.Request, raise_on_error: bool = False
    ) -> None:
        if self.validate:
            try:
                REQUEST.validate(request)
            except Exception as err:
                self.log.warning("Request Validation Error:\n%s", err)
                if raise_on_error:
                    raise err

    def validate_response(
        self, response: shapes.Response, raise_on_error: bool = False
    ) -> None:
        if self.validate:
            try:
                RESPONSE.validate(response)
            except Exception as err:
                self.log.warning("Response Validation Error:\n%s", err)
                if raise_on_error:
                    raise err
