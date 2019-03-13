from traitlets.utils.bunch import Bunch

from .diadefslib import DiaDefs

class DotWriter:
    def __init__(self, config: Bunch): ...
    def write(self, diadefs: DiaDefs) -> None: ...
