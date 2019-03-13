import io
import os
import typing as typ
from base64 import b64encode
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote

from IPython.core.interactiveshell import InteractiveShell
from IPython.display import HTML, SVG, Image, Markdown
from IPython.utils.capture import capture_output
from pygraphviz import AGraph
from pylint.config import ConfigurationMixIn
from pylint.graph import DotBackend
from pylint.pyreverse import writer
from pylint.pyreverse.diadefslib import DiadefsHandler
from pylint.pyreverse.inspector import Linker, project_from_files
from pylint.pyreverse.utils import insert_default_options
from pylint.pyreverse.writer import DotWriter
from traitlets.utils.bunch import Bunch

from ipylintotype import shapes
from ipylintotype.diagnosers.diagnoser import IPythonDiagnoser


def pyreverse(code_str: typ.Text) -> typ.Iterator[typ.Text]:
    with TemporaryDirectory() as td:
        tdp = Path(td)
        source = tdp / "source.py"
        source.write_text(code_str)
        default_config = dict(
            module_names="source",
            classes=[],
            mode="PUB_ONLY",  # or "ALL"
            all_ancestors=True,
            all_associated=True,
            show_ancestors=True,
            show_associated=True,
            only_classnames=True,
            output_format="dot",
            show_builtin=False,
        )

        config = dict()
        config.update(default_config)
        config_bunch = Bunch(config)

        with capture_output(display=False):
            project = project_from_files([str(source)])
        linker = Linker(project, tag=True)
        handler = DiadefsHandler(config_bunch)
        diadefs = handler.get_diadefs(project, linker)
        old_cwd = os.getcwd()
        os.chdir(td)
        try:
            writer.DotWriter(config_bunch).write(diadefs)
        finally:
            os.chdir(old_cwd)
        for path in sorted(Path(td).glob("*.dot")):
            yield path.read_text().replace(f"{td}/source.py.", "")


class PyReverseDiagnoser(IPythonDiagnoser):
    def run(
        self,
        cell_id: typ.Text,
        code: typ.List[shapes.Cell],
        metadata: shapes.Metadata,
        shell: InteractiveShell,
        *args,
        **kwargs,
    ) -> shapes.Annotations:
        transformed_code, line_offsets = self.transform_for_diagnostics(code, shell)
        graphs = list(pyreverse(transformed_code))
        if not graphs:
            return {}

        dot = AGraph(graphs[0])
        s = io.BytesIO()
        dot.draw(s, "svg", prog="dot")
        md = f"""![svg image](data:image/svg+xml,{quote(s.getvalue())})"""

        return dict(
            markup_contexts=[
                {
                    "title": f"Class Diagram",
                    "range": {
                        "start": dict(line=0, character=0),
                        "end": dict(line=0, character=1),
                    },
                    "content": {"kind": "markdown", "value": md},
                }
            ]
        )
        return {}
