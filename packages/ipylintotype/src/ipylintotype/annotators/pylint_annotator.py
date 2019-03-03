import contextlib
import io
import re
from pathlib import Path
from tempfile import TemporaryDirectory

import pylint.lint
import traitlets

from .annotator import IPythonAnnotator

_re_pylint = r"^(.):\s*(\d+),\s(\d+):\s*(.*?)\s*\((.*)\)$"


_help_pylint_args = (
    f"https://docs.pylint.org/en/{pylint.__version__}/run.html#command-line-options"
)


class PyLint(IPythonAnnotator):
    entry_point = traitlets.Unicode(default_value=pylint.__name__)
    args = traitlets.List(traitlets.Unicode(), help=_help_pylint_args)

    @traitlets.default("args")
    def _default_ignore(self):
        rules = ["trailing-newlines"]
        return [f"""--disable-rules={",".join(rules)}"""]

    def run(self, cell_id, code, metadata, shell, *args, **kwargs):
        s = io.StringIO()
        code, line_offsets = self.transform_for_annotation(code, shell)

        with TemporaryDirectory() as td:
            tdp = Path(td)
            code_file = tdp / "code.py"
            code_file.write_text(code)
            with contextlib.redirect_stdout(s), contextlib.redirect_stderr(
                io.StringIO()
            ):
                try:
                    res = pylint.lint.Run(list(self.args) + [str(code_file)])
                except:
                    pass
        matches = re.findall(_re_pylint, s.getvalue(), flags=re.M)

        for severity, line, col, msg, rule in matches:
            line = int(line) - line_offsets[cell_id]
            col = int(col)
            msg = (f"{msg.strip()}\t[{self.entry_point}:{rule}]",)
            yield {
                "message": msg,
                "severity": {
                    "W": "warning",
                    # "C": "convention"
                }.get(severity, "error"),
                "from": dict(line=line - 1, col=col - 1),
                "to": dict(line=line - 1, col=col),
            }
