from ipywidgets import (
    HTML,
    Box,
    HBox,
    IntSlider,
    SelectMultiple,
    Textarea,
    ToggleButton,
    VBox,
)
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


def show_line_length(diagnoser):
    slider = IntSlider(description="line length", max=200, min=11)
    link((diagnoser, "line_length"), (slider, "value"))
    return slider


def show_flake8(diagnoser):
    ignore = Textarea(description="ignore")
    dlink(
        (ignore, "value"),
        (diagnoser, "ignore"),
        lambda i: [i.strip() for i in i.split(" ")],
    )
    select = SelectMultiple(
        options=["E", "W", "F"], value=["E", "W", "F"], description="select"
    )
    dlink((select, "value"), (diagnoser, "select"))
    return [ignore, select]


visibility = {True: "visible", False: "hidden"}


def show_diagnoser(diagnoser: Diagnoser, container=HBox) -> Box:
    enabled = show_enabled(diagnoser)
    widgets = []
    if hasattr(diagnoser, "args"):
        widgets += [show_args(diagnoser)]
    if hasattr(diagnoser, "line_length"):
        widgets += [show_line_length(diagnoser)]

    is_flake8 = False
    try:
        from ipylintotype.diagnosers.flake8_diagnoser import Flake8Diagnoser

        is_flake8 = isinstance(diagnoser, Flake8Diagnoser)
    except:
        pass
    if is_flake8:
        widgets += show_flake8(diagnoser)

    for widget in widgets:
        dlink((diagnoser, "enabled"), (widget.layout, "visibility"), visibility.get)

    return container([enabled] + widgets)


def show_formatter(formatter: AnnotationFormatter = None, container=VBox) -> HBox:
    if formatter is None:
        from .. import get_ipylintotype

        formatter = get_ipylintotype()
    return container(list(map(show_diagnoser, formatter.diagnosers)))
