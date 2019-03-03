import re

import mypy.api
import traitlets

from .annotator import IPythonAnnotator

_re_mypy = (
    r"(?P<type>.*):(?P<line>\d+):(?P<col>\d+):\s*(?P<severity>.*)\s*:(?P<message>.*)"
)


class MyPy(IPythonAnnotator):
    args = traitlets.List(
        ["--show-column-numbers", "--show-error-context", "--follow-imports", "silent"]
    )

    entry_point = traitlets.Unicode(default_value=mypy.__name__)

    def run(self, cell_id, code, metadata, shell, *args, **kwargs):
        code, line_offsets = self.transform_for_annotation(code, shell)
        args = list(args) + self.args + ["-c", code]

        out, err, count = mypy.api.run(args)

        matches = [re.match(_re_mypy, line) for line in out.strip().split("\n")]
        matches = [match.groupdict() for match in matches if match]
        for anno in matches:
            line = int(anno["line"]) - line_offsets[cell_id]
            col = int(anno["col"])
            msg = f"""{anno["message"].strip()} [{self.entry_point}]"""
            yield {
                "message": msg,
                "severity": anno["severity"],
                "from": dict(line=line - 1, col=col - 1),
                "to": dict(line=line - 1, col=col),
            }
