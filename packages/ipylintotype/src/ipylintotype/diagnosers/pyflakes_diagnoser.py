import difflib
import io
import re
import typing as typ

import pyflakes.api
import pyflakes.reporter
import traitlets

from .. import shapes
from .diagnoser import Diagnoser, InteractiveShell, IPythonDiagnoser

# TODO: better
_help_pyflakes_args = "https://github.com/PyCQA/pyflakes/blob/master/pyflakes/api.py"
# "source.py:7:10: EOL while scanning string literal\n    'pass\n         ^\n"
_re_pyflakes = r"^(.*?):(\d+):(\d+)?:?\s*(.*?)$"


class PyFlakesDiagnoser(IPythonDiagnoser):
    entry_point = traitlets.Unicode(default_value=pyflakes.__name__)

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
        errors, warnings = io.StringIO(), io.StringIO()
        reporter = pyflakes.reporter.Reporter(errors, warnings)
        count = pyflakes.api.check(transformed_code, "source.py", reporter=reporter)
        if not count:
            return {}
        error_lines = errors.getvalue() + "\n" + warnings.getvalue()
        matches = re.findall(_re_pyflakes, error_lines, flags=re.M)

        diagnostics = []  # type: typ.List[shapes.Diagnostic]

        for fname, line, col, msg in matches:
            line = int(line) - line_offsets[cell_id]
            try:
                col = int(col)
            except:
                col = 2
            diagnostics.append(
                {
                    "message": msg.strip(),
                    "source": self.entry_point,
                    "code": "",
                    "severity": 1,
                    "range": {
                        "start": dict(line=line - 1, character=col - 1),
                        "end": dict(line=line - 1, character=col),
                    },
                }
            )
        return dict(diagnostics=diagnostics)
