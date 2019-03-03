import IPython
import traitlets
from ipykernel.comm import Comm

from ._version import __comm__


class AnnotationFormatter(IPython.core.interactiveshell.InteractiveShell):
    annotators = traitlets.List()

    comm_name = traitlets.Unicode(default_value=__comm__)

    current_comm = traitlets.Any()

    @traitlets.default("annotators")
    def _default_annotators(self):
        annotators = []
        try:
            from .annotators.mypy_annotator import MyPy

            annotators += [MyPy()]
        except ImportError:
            self.log.warn("mypy could not be imported")

        try:
            from .annotators.pylint_annotator import PyLint

            annotators += [PyLint()]
        except ImportError:
            self.log.warn("pylint could not be imported")

        return annotators

    def init_user_ns(self):
        ...

    def __init__(self, *args, **kwargs):
        if "parent" in kwargs:
            kwargs = {**kwargs["parent"]._trait_values, **kwargs}
        super().__init__(*args, **kwargs)
        self.init_comm()

    def init_comm(self):
        self.close()
        self.current_comm = Comm(target_name=self.comm_name)
        self.current_comm.on_msg(self.on_msg)

    def __call__(self, cell_id, code=None, metadata=None, *args):
        result = dict()
        for annotator in self.annotators:
            annotator_code = code.get(annotator.mimetype)
            if not annotator_code:
                continue
            try:
                annotations = annotator(
                    cell_id=cell_id,
                    code=code[annotator.mimetype],
                    metadata=metadata.get(annotator.mimetype, {}),
                    shell=self,
                )
                result.setdefault(annotator.mimetype, []).extend(annotations)
            except Exception as err:
                self.log.error(f"{annotator}: {err}\n{code}")
                self.log.exception(f"{annotator} failed")

        return result

    def close(self):
        if self.current_comm:
            self.current_comm.close()
        self.current_comm = None

    def on_msg(self, msg):
        data = msg["content"]["data"]
        request_id = data.get("request_id")
        cell_id = data.get("cell_id")

        if not request_id:
            return

        annotations = self(
            cell_id=cell_id,
            code=data.get("code", {}),
            metadata=data.get("metadata", {}),
        )
        self.current_comm.send(
            dict(cell_id=cell_id, request_id=request_id, annotations=annotations)
        )
