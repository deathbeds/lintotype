from ipywidgets import HTML, Box, HBox, Textarea, ToggleButton, VBox
from traitlets import dlink, link

from ..annotators.annotator import Annotator
from ..formatter import AnnotationFormatter


def show_enabled(annotator):
    btn = ToggleButton(
        description=f"""{annotator.entry_point}""",
        tooltip=f"Toggle {annotator.entry_point}",
        icon="no-icon",
    )

    link((annotator, "enabled"), (btn, "value"))

    dlink(
        (btn, "value"),
        (btn, "description"),
        lambda x: f"""{annotator.entry_point} {"enabled" if x else "disabled"}""",
    )

    return btn


def show_args(annotator, container=VBox):
    text = Textarea(" ".join(annotator.args), rows=3)
    dlink((text, "value"), (annotator, "args"), lambda x: x.split(" "))
    help_text = annotator.traits()["args"].help
    help = HTML(f"""<a href="{help_text}" target="_blank">more...</a>""")
    return container([text, help])


visibility = {True: "visible", False: "hidden"}


def show_annotator(annotator: Annotator, container=VBox) -> Box:
    enabled = show_enabled(annotator)
    widgets = []
    if hasattr(annotator, "args"):
        widgets += [show_args(annotator)]

    for widget in widgets:
        dlink((annotator, "enabled"), (widget.layout, "visibility"), visibility.get)

    return container([enabled] + widgets)


def show_formatter(formatter: AnnotationFormatter = None, container=HBox) -> HBox:
    if formatter is None:
        from .. import get_ipylintotype

        formatter = get_ipylintotype()
    return container(list(map(show_annotator, formatter.annotators)))
