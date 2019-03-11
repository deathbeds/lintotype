import typing as typ

import traitlets
from IPython.core.interactiveshell import InteractiveShell

from .. import shapes


class Diagnoser(traitlets.HasTraits):
    mimetype = traitlets.Unicode()
    entry_point = traitlets.Unicode()
    enabled = traitlets.Bool(True)
    args = traitlets.List(traitlets.Unicode())  # type: typ.List[typ.Text]

    class Severity:
        error = 1
        warning = 2
        info = 3
        hint = 4

    def run(
        self,
        cell_id: typ.Text,
        code: typ.List[shapes.Cell],
        metadata: shapes.Metadata,
        shell: InteractiveShell,
        *args,
        **kwargs
    ) -> shapes.Annotations:
        raise NotImplementedError()

    @traitlets.default("entry_point")
    def _default_entry_point(self):
        return self.__name__


class IPythonDiagnoser(Diagnoser):
    mimetype = traitlets.Unicode("text/x-ipython")

    cell_separator = traitlets.Unicode("\n")

    def transform_for_diagnostics(
        self, cells: typ.List[shapes.Cell], shell: InteractiveShell
    ) -> typ.Tuple[typ.Text, typ.Dict[str, int]]:
        code: typ.List[str] = []
        line_offsets: typ.Dict[typ.Text, int] = {}
        for cell in cells:
            line_offsets[cell["cell_id"]] = len(code)
            code += shell.transform_cell(cell["code"]).split("\n")

        return self.cell_separator.join(code), line_offsets
