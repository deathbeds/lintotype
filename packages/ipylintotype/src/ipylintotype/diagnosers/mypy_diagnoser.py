import re
import typing as typ

import mypy.api
import traitlets

from .. import shapes
from .diagnoser import Diagnoser, InteractiveShell, IPythonDiagnoser

_re_mypy = (
    r"(?P<source>.*):(?P<line>\d+):(?P<col>\d+):\s*(?P<severity>.*?)\s*:(?P<message>.*)"
)

_help_mypy_args = "https://mypy.readthedocs.io/en/latest/command_line.html"

_mypy_severity = {
    "error": Diagnoser.Severity.error,
    "warning": Diagnoser.Severity.warning,
    "note": Diagnoser.Severity.info,
}

_default_mypy_args = [
    "--show-column-numbers",
    "--show-error-context",
    "--follow-imports",
    "silent",
]


class MyPyDiagnoser(IPythonDiagnoser):
    args = traitlets.List(_default_mypy_args, help=_help_mypy_args)  # type: ignore

    entry_point = traitlets.Unicode(default_value=mypy.__name__)

    def run(
        self,
        cell_id: typ.Text,
        code: typ.List[shapes.Cell],
        metadata: shapes.Metadata,
        shell: InteractiveShell,
        *args,
        **kwargs
    ) -> shapes.Annotations:
        transformed_code, line_offsets = self.transform_for_diagnostics(code, shell)
        mypy_args = (
            list(args) + self.args + ["-c", transformed_code]
        )  # type: typ.List[typ.Text]

        out, err, count = mypy.api.run(mypy_args)

        matches = [re.match(_re_mypy, line) for line in out.strip().split("\n")]
        raw_items = [match.groupdict() for match in matches if match]

        diagnostics = []  # type: typ.List[shapes.Diagnostic]

        for diag in raw_items:
            line = int(diag["line"]) - line_offsets[cell_id]
            col = int(diag["col"])
            msg = diag["message"].strip()

            diagnostics.append(
                {
                    "message": msg,
                    "severity": _mypy_severity.get(
                        diag["severity"], self.Severity.error
                    ),
                    "source": self.entry_point,
                    "range": {
                        "start": dict(line=line - 1, character=col - 1),
                        "end": dict(line=line - 1, character=col),
                    },
                }
            )

        return dict(diagnostics=diagnostics)
