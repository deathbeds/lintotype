import re

import mypy.api

MYPY_ARGS = ["--show-column-numbers", "--show-error-context"]

# TODO: figure out some JSON output
_re_mypy = (
    r"(?P<type>.*):(?P<line>\d+):(?P<col>\d+):\s*(?P<severity>.*)\s*:(?P<message>.*)"
)


def mypy_linter(code, *args):
    args = args or MYPY_ARGS
    out, err, count = mypy.api.run(["-c", code, *args])
    matches = [re.match(_re_mypy, line) for line in out.strip().split("\n")]
    matches = [match.groupdict() for match in matches if match]
    return [
        {
            "message": f"""{err["message"]} [mypy]""",
            "severity": err["severity"],
            "from": dict(line=int(err["line"]), col=int(err["col"])),
            "to": dict(line=int(err["line"]), col=int(err["col"]) + 1),
        }
        for err in matches
    ]
