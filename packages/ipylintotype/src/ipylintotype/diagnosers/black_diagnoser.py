import difflib
import re

import black
import traitlets

from .diagnoser import Diagnoser, IPythonDiagnoser

_help_black_args = "https://black.readthedocs.io/en/stable/installation_and_usage.html#command-line-options"


class BlackDiagnoser(IPythonDiagnoser):
    line_length = traitlets.Integer(88, help=_help_black_args)

    entry_point = traitlets.Unicode(default_value=black.__name__)

    def run(self, cell_id, code, metadata, shell, *args, **kwargs):
        for cell in code:
            if cell["cell_id"] != cell_id:
                continue

            black_src = black.format_str(cell["code"], line_length=self.line_length)

            if black_src.strip() != cell["code"].strip():
                return dict(
                    code_actions=[
                        {
                            "title": "any color you like",
                            "edit": {
                                "changes": {
                                    cell_id: [
                                        {
                                            "range": {
                                                "start": dict(line=0, character=0),
                                                "end": dict(
                                                    line=len(cell["code"].split("\n"))
                                                    - 1,
                                                    character=1,
                                                ),
                                            },
                                            "newText": black_src,
                                        }
                                    ]
                                }
                            },
                        }
                    ]
                )
        return {}
