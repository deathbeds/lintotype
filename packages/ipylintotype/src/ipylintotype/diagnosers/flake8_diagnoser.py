import contextlib
import inspect
import io
import os
import re
import tempfile
import typing as typ

import traitlets
from flake8.api import legacy
from IPython.core.interactiveshell import InteractiveShell

from .. import shapes
from .diagnoser import IPythonDiagnoser

_re_flake8 = r"^(.*):\s*(?P<line>\d+)\s*:\s*(?P<col>\d+)\s*:\s*(?P<code>.*?)\s(?P<message>.*)\s*$"


class Flake8Diagnoser(IPythonDiagnoser):
    entry_point = traitlets.Unicode(default_value="flake8")

    ignore = traitlets.List(traitlets.Unicode())
    select = traitlets.List(traitlets.Unicode())

    @traitlets.default("ignore")
    def _default_ignore(self) -> typ.List[typ.Text]:
        d: typ.List[typ.Text] = []
        return d

    @traitlets.default("select")
    def _default_select(self) -> typ.List[typ.Text]:
        d: typ.List[typ.Text] = []
        return d

    def run(
        self,
        cell_id: typ.Text,
        code: typ.List[shapes.Cell],
        metadata: typ.Dict[str, typ.Dict[str, typ.Any]],
        shell: InteractiveShell,
        *args,
        **kwargs
    ) -> shapes.Annotations:
        code_str, line_offsets = self.transform_for_diagnostics(code, shell)

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            file = tempfile.NamedTemporaryFile(delete=False)
            file.write(code_str.encode("utf-8"))
            file.close()
            style_guide = legacy.get_style_guide(ignore=self.ignore, select=self.select)
            report = style_guide.check_files([file.name])
            os.unlink(file.name)

        matches = re.findall(_re_flake8, out.getvalue(), flags=re.M)

        diagnostics: typ.List[shapes.Diagnostic] = []
        for file, line, col, err_code, msg in matches:
            line = int(line) - line_offsets[cell_id]
            col = int(col)
            diagnostics.append(
                {
                    "message": msg,
                    "source": self.entry_point,
                    "severity": self.Severity.error,
                    "code": err_code,
                    "range": {
                        "start": dict(line=line - 1, character=col - 1),
                        "end": dict(line=line - 1, character=col),
                    },
                }
            )
        return {"diagnostics": diagnostics}


try:
    import ipywidgets as W, traitlets as T

    def show_flake8(diagnoser: Flake8Diagnoser) -> typ.List[W.DOMWidget]:
        ignore = W.Textarea(description="ignore")

        def ignore_to_diagnoser(value: typ.Text) -> typ.List[typ.Text]:
            return [i.strip() for i in value.split(" ")]

        T.dlink((ignore, "value"), (diagnoser, "ignore"), ignore_to_diagnoser)
        select = W.SelectMultiple(
            options=["E", "W", "F"], value=["E", "W", "F"], description="select"
        )

        T.dlink((select, "value"), (diagnoser, "select"))  # type: ignore
        return [ignore, select]


except ImportError:
    pass
