import re

import mypy.api
import traitlets

from .diagnoser import Diagnoser, IPythonDiagnoser

_re_mypy = (
    r"(?P<source>.*):(?P<line>\d+):(?P<col>\d+):\s*(?P<severity>.*?)\s*:(?P<message>.*)"
)

_help_mypy_args = "https://mypy.readthedocs.io/en/latest/command_line.html"

_mypy_severity = {
    "error": Diagnoser.Severity.error,
    "warning": Diagnoser.Severity.warning,
    "note": Diagnoser.Severity.info,
}


class MyPyDiagnoser(IPythonDiagnoser):
    args = traitlets.List(
        ["--show-column-numbers", "--show-error-context", "--follow-imports", "silent"],
        help=_help_mypy_args,
    )

    entry_point = traitlets.Unicode(default_value=mypy.__name__)

    def run(self, cell_id, code, metadata, shell, *args, **kwargs):
        code, line_offsets = self.transform_for_diagnostics(code, shell)
        args = list(args) + self.args + ["-c", code]

        out, err, count = mypy.api.run(args)

        matches = [re.match(_re_mypy, line) for line in out.strip().split("\n")]
        matches = [match.groupdict() for match in matches if match]

        diagnostics = []

        for diag in matches:
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

        return dict(diagnostics=diagnostics) if diagnostics else {}
