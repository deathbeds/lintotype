import typing as typ

from mypy_extensions import TypedDict

Cell = TypedDict("Cell", {"code": typ.Text, "cell_id": typ.Text})

MIME = typ.Text

Metadata = typ.Dict[MIME, typ.Dict[typ.Text, typ.Any]]

MIMECode = typ.Dict[MIME, typ.List[Cell]]

Request = TypedDict(
    "Request",
    {"request_id": int, "cell_id": typ.Text, "metadata": Metadata, "code": MIMECode},
    total=False,
)

MessageData = TypedDict("MessageData", {"data": Request})


Message = TypedDict("Message", {"content": MessageData})

Pos = TypedDict("Pos", {"line": int, "character": int})

Range = TypedDict("Range", {"start": Pos, "end": Pos})

Diagnostic = TypedDict(
    "Diagnostic",
    {
        "code": typ.Text,
        "message": typ.Text,
        "range": Range,
        "severity": int,
        "source": typ.Text,
    },
    total=False,
)

TextEdit = TypedDict("TextEdit", {"newText": typ.Text, "range": Range})

WorkspaceEdit = TypedDict(
    "WorkspaceEdit", {"changes": typ.Dict[typ.Text, typ.List[TextEdit]]}
)

CodeAction = TypedDict(
    "CodeAction",
    {
        "diagnostics": typ.List[Diagnostic],
        "edit": WorkspaceEdit,
        "kind": typ.Text,
        "title": typ.Text,
    },
    total=False,
)

Annotations = TypedDict(
    "Annotations",
    {"code_actions": typ.List[CodeAction], "diagnostics": typ.List[Diagnostic]},
    total=False,
)

MIMEAnnotations = typ.Dict[MIME, Annotations]

Response = TypedDict(
    "Response",
    {
        "request_id": int,
        "cell_id": typ.Text,
        "annotations": MIMEAnnotations,
        "metadata": Metadata,
    },
    total=False,
)
