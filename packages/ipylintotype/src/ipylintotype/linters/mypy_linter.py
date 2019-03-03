import re

import mypy.api

MYPY_ARGS = [
    "--show-column-numbers",
    "--show-error-context",
    "--incremental",
    "--follow-imports",
    "silent",
]

# TODO: figure out some JSON output
_re_mypy = (
    r"(?P<type>.*):(?P<line>\d+):(?P<col>\d+):\s*(?P<severity>.*)\s*:(?P<message>.*)"
)

IPYMIME = "text/x-ipython"


def mypy_linter(code, all_code, metadata, *args):
    """ > ### mypy
    Show type warnings from `mypy` (must be installed in your kernel environment)

    You may customize MYPY_ARGS with any option to the `mypy` CLI:

        https://mypy.readthedocs.io/en/latest/command_line.html

    """
    ipython_cells = all_code.get(IPYMIME, [])
    if ipython_cells:
        # a list of strings
        ipython_code = []
        line_offsets = {}
        for cell in ipython_cells:
            line_offsets[cell["id"]] = len(ipython_code)
            if code == cell["code"]:
                code_id = cell["id"]
            ipython_code += cell["code"].split("\n")
        code = "\n".join(ipython_code)
    the_args = [*args, *MYPY_ARGS, "-c", code]
    out, err, count = mypy.api.run(the_args)
    lines = [line for line in out.strip().split("\n")]
    matches = [re.match(_re_mypy, line) for line in out.strip().split("\n")]
    matches = [match.groupdict() for match in matches if match]

    annotations = {
        IPYMIME: [
            {
                "message": f"""{err["message"]} [mypy]""",
                "severity": err["severity"],
                "from": dict(line=int(err["line"]) - 1, col=int(err["col"]) - 1),
                "to": dict(line=int(err["line"]) - 1, col=int(err["col"])),
            }
            for err in matches
        ]
    }

    return annotations
