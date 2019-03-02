import re

import mypy.api

MYPY_ARGS = [
    "--show-column-numbers",
    "--show-error-context",
    "--follow-imports",
    "silent",
]

# TODO: figure out some JSON output
_re_mypy = (
    r"(?P<type>.*):(?P<line>\d+):(?P<col>\d+):\s*(?P<severity>.*)\s*:(?P<message>.*)"
)


def mypy_linter(code, *args):
    """ > ### mypy
    Show type warnings from `mypy` (must be installed in your kernel environment)

    You may customize MYPY_ARGS with any option to the `mypy` CLI:

        https://mypy.readthedocs.io/en/latest/command_line.html

    """
    the_args = [*args, *MYPY_ARGS, "-c", code]
    out, err, count = mypy.api.run(the_args)
    lines = [line for line in out.strip().split("\n")]
    matches = [re.match(_re_mypy, line) for line in out.strip().split("\n")]
    matches = [match.groupdict() for match in matches if match]

    return [
        {
            "message": f"""{err["message"]} [mypy]""",
            "severity": err["severity"],
            "from": dict(line=int(err["line"]) - 1, col=int(err["col"]) - 1),
            "to": dict(line=int(err["line"]) - 1, col=int(err["col"])),
        }
        for err in matches
    ]
