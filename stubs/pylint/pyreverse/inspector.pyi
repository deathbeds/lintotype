import typing as typ

class Linker:
    def __init__(self, project: Project, *, tag: bool): ...

class Project: ...

def project_from_files(files: typ.List[typ.Text]) -> Project: ...
