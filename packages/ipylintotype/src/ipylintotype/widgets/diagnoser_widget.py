from ipywidgets import HTML, Box, HBox, Textarea, ToggleButton, VBox
from traitlets import dlink, link

from ..diagnosers.diagnoser import Diagnoser
from ..formatter import AnnotationFormatter


def show_enabled(diagnoser):
    btn = ToggleButton(
        description=f"""{diagnoser.entry_point}""",
        tooltip=f"Toggle {diagnoser.entry_point}",
        icon="no-icon",
    )

    link((diagnoser, "enabled"), (btn, "value"))

    dlink(
        (btn, "value"),
        (btn, "description"),
        lambda x: f"""{diagnoser.entry_point} {"enabled" if x else "disabled"}""",
    )

    return btn


def show_args(diagnoser, container=VBox):
    text = Textarea(" ".join(diagnoser.args), rows=3)
    dlink((text, "value"), (diagnoser, "args"), lambda x: x.split(" "))
    help_text = diagnoser.traits()["args"].help
    help = HTML(f"""<a href="{help_text}" target="_blank">more...</a>""")
    return container([text, help])


visibility = {True: "visible", False: "hidden"}


def show_diagnoser(diagnoser: Diagnoser, container=VBox) -> Box:
    enabled = show_enabled(diagnoser)
    widgets = []
    if hasattr(diagnoser, "args"):
        widgets += [show_args(diagnoser)]

    for widget in widgets:
        dlink((diagnoser, "enabled"), (widget.layout, "visibility"), visibility.get)

    return container([enabled] + widgets)


def show_formatter(formatter: AnnotationFormatter = None, container=HBox) -> HBox:
    if formatter is None:
        from .. import get_ipylintotype

        formatter = get_ipylintotype()
    return container(list(map(show_diagnoser, formatter.diagnosers)))
