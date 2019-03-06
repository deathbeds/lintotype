import contextlib
import io
import re
from pathlib import Path
from tempfile import TemporaryDirectory

import pylint.lint
import traitlets

from .diagnoser import Diagnoser, IPythonDiagnoser

_re_pylint = r"^(.):\s*(\d+),\s(\d+):\s*(.*?)\s*\((.*)\)$"


_help_pylint_args = (
    f"https://docs.pylint.org/en/{pylint.__version__}/run.html#command-line-options"
)

_pylint_severity = {
    "W": Diagnoser.Severity.warning,
    "E": Diagnoser.Severity.error,
    "C": Diagnoser.Severity.info,
    "R": Diagnoser.Severity.hint,
}


class PyLintDiagnoser(IPythonDiagnoser):
    entry_point = traitlets.Unicode(default_value=pylint.__name__)
    args = traitlets.List(traitlets.Unicode(), help=_help_pylint_args)

    @traitlets.default("args")
    def _default_ignore(self):
        rules = ["trailing-newlines"]
        return [f"""--disable={",".join(rules)}"""]

    def run(self, cell_id, code, metadata, shell, *args, **kwargs):
        out = io.StringIO()
        err = io.StringIO()
        code, line_offsets = self.transform_for_diagnostics(code, shell)

        with TemporaryDirectory() as td:
            tdp = Path(td)
            code_file = tdp / "code.py"
            code_file.write_text(code)
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                try:
                    res = pylint.lint.Run(list(self.args) + [str(code_file)])
                except:
                    pass
        outs = out.getvalue()
        errs = err.getvalue()

        matches = re.findall(_re_pylint, outs, flags=re.M)

        diagnostics = []

        for severity, line, col, msg, rule in matches:
            line = int(line) - line_offsets[cell_id]
            col = int(col)
            msg = msg.strip()
            diagnostics.append(
                {
                    "message": msg,
                    "source": self.entry_point,
                    "code": rule,
                    "severity": _pylint_severity.get(severity, self.Severity.error),
                    "range": {
                        "start": dict(line=line - 1, character=col - 1),
                        "end": dict(line=line - 1, character=col),
                    },
                }
            )

        return dict(diagnostics=diagnostics) if diagnostics else {}
