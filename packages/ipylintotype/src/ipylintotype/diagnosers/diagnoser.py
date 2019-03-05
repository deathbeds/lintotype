import abc

import traitlets


class Diagnoser(traitlets.HasTraits):
    mimetype = traitlets.Unicode()
    entry_point = traitlets.Unicode()
    enabled = traitlets.Bool(default_value=True)

    class Severity:
        error = 1
        warning = 2
        info = 3
        hint = 4

    def __call__(self, cell_id, code, metadata, shell, *args, **kwargs):
        return self.run(cell_id, code, metadata, shell, *args, **kwargs)

    @traitlets.default("entry_point")
    def _default_entry_point(self):
        return self.__name__

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError()


class IPythonDiagnoser(Diagnoser):
    mimetype = traitlets.Unicode(default_value="text/x-ipython")

    def transform_for_diagnostics(self, cells, shell):
        code = []
        line_offsets = {}
        for cell in cells:
            line_offsets[cell["cell_id"]] = len(code)
            code += shell.transform_cell(cell["code"]).split("\n")

        return "\n".join(code), line_offsets
