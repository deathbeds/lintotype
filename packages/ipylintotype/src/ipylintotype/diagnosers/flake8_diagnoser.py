import contextlib
import inspect
import io
import os
import re
import tempfile

import traitlets
from flake8.api import legacy

from .diagnoser import IPythonDiagnoser

_re_flake8 = r"^(.*):\s*(?P<line>\d+)\s*:\s*(?P<col>\d+)\s*:\s*(?P<code>.*?)\s(?P<message>.*)\s*$"


class Flake8Diagnoser(IPythonDiagnoser):
    entry_point = traitlets.Unicode(default_value="flake8")

    ignore = traitlets.List(traitlets.Unicode)
    select = traitlets.List(traitlets.Unicode)

    @traitlets.default("ignore")
    def _default_ignore(self):
        return []

    @traitlets.default("select")
    def _default_ignore(self):
        return []

    def run(self, cell_id, code, metadata, shell, *args, **kwargs):
        code, line_offsets = self.transform_for_diagnostics(code, shell)

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            file = tempfile.NamedTemporaryFile(delete=False)
            file.write(code.encode("utf-8"))
            file.close()
            style_guide = legacy.get_style_guide(ignore=self.ignore, select=self.select)
            report = style_guide.check_files([file.name])
            os.unlink(file.name)

        matches = re.findall(_re_flake8, out.getvalue(), flags=re.M)

        diagnostics = []
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
