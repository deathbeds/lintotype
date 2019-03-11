import typing as typ

from ipywidgets import (
    HTML,
    Box,
    DOMWidget,
    HBox,
    IntSlider,
    SelectMultiple,
    Textarea,
    ToggleButton,
    VBox,
    Widget,
)
from traitlets import dlink, link

from ..diagnosers.diagnoser import Diagnoser
from ..formatter import AnnotationFormatter

if typ.TYPE_CHECKING:  # pragma: no cover
    from ..diagnosers.flake8_diagnoser import Flake8Diagnoser


def show_enabled(diagnoser: Diagnoser) -> DOMWidget:
    btn = ToggleButton(
        description=f"""{diagnoser.entry_point}""",
        tooltip=f"Toggle {diagnoser.entry_point}",
        icon="no-icon",
    )

    link((diagnoser, "enabled"), (btn, "value"))

    def value_to_desc(value: bool) -> typ.Text:
        return f"""{diagnoser.entry_point} {"enabled" if value else "disabled"}"""

    dlink((btn, "value"), (btn, "description"), value_to_desc)

    return btn


def show_args(diagnoser: Diagnoser, container: typ.Callable[..., Box] = VBox) -> Box:
    text = Textarea(" ".join(diagnoser.args), rows=3)
    dlink((text, "value"), (diagnoser, "args"), lambda x: x.split(" "))  # type: ignore
    help_text = diagnoser.traits()["args"].help
    help = HTML(f"""<a href="{help_text}" target="_blank">more...</a>""")
    return container([text, help])


def show_line_length(diagnoser: Diagnoser) -> DOMWidget:
    slider = IntSlider(description="line length", max=200, min=11)
    link((diagnoser, "line_length"), (slider, "value"))
    return slider


visibility = {True: "visible", False: "hidden"}


def show_diagnoser(
    diagnoser: Diagnoser, container: typ.Callable[..., Box] = VBox
) -> Box:
    enabled = show_enabled(diagnoser)
    widgets: typ.List[DOMWidget] = []
    if hasattr(diagnoser, "args"):
        widgets += [show_args(diagnoser)]
    if hasattr(diagnoser, "line_length"):
        widgets += [show_line_length(diagnoser)]

    is_flake8 = False
    try:
        from ipylintotype.diagnosers.flake8_diagnoser import (
            show_flake8,
            Flake8Diagnoser,
        )

        show_flake8(typ.cast(Flake8Diagnoser, diagnoser))
    except:
        pass

    for widget in widgets:
        dlink(
            (diagnoser, "enabled"), (widget.layout, "visibility"), visibility.get
        )  # type: ignore

    return container([enabled] + widgets)


def show_formatter(
    formatter: AnnotationFormatter = None, container: typ.Callable[..., Box] = VBox
) -> Box:
    if formatter is None:
        from .. import get_ipylintotype

        formatter = get_ipylintotype()
    return container(list(map(show_diagnoser, formatter.diagnosers)))
