import logging


class InteractiveShell:
    log: logging.Logger

    def transform_cell(self, cell: str) -> str:
        ...
