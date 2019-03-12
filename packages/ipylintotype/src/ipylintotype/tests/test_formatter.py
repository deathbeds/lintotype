import typing as typ

import pytest
from jsonschema import ValidationError

from .. import AnnotationFormatter, shapes


@pytest.fixture
def formatter() -> AnnotationFormatter:
    return AnnotationFormatter()


@pytest.fixture
def empty_request() -> shapes.Request:
    return typ.cast(shapes.Request, {})


@pytest.fixture
def empty_response() -> shapes.Response:
    return typ.cast(shapes.Response, {})


@pytest.fixture
def minimal_request() -> shapes.Response:
    return typ.cast(shapes.Response, {"cell_id": "1", "request_id": 0})


def test_formatter_load(formatter: AnnotationFormatter) -> None:
    assert formatter.diagnosers


def test_formatter_validate(
    formatter: AnnotationFormatter,
    minimal_request: shapes.Request,
    empty_request: shapes.Request,
    empty_response: shapes.Response,
) -> None:
    formatter.validate_request(minimal_request, raise_on_error=True)

    with pytest.raises(ValidationError):
        formatter.validate_request(empty_request, raise_on_error=True)

    with pytest.raises(ValidationError):
        formatter.validate_response(empty_response, raise_on_error=True)


def test_formatter_validate_no_raise(
    formatter: AnnotationFormatter,
    empty_request: shapes.Request,
    empty_response: shapes.Response,
) -> None:
    formatter.validate = False
    formatter.validate_request(empty_request, raise_on_error=False)
    formatter.validate_response(empty_response, raise_on_error=False)


@pytest.fixture
def minimal_clean_code() -> shapes.MIMECode:
    return {"text/x-ipython": [{"cell_id": "1", "code": "x = 1"}]}


@pytest.fixture
def minimal_empty_response() -> shapes.MIMECode:
    return typ.cast(
        shapes.MIMECode, {"text/x-ipython": {"diagnostics": [], "code_actions": []}}
    )


@pytest.fixture
def minimal_annotations() -> shapes.MIMEAnnotations:
    return {
        "text/x-ipython": {
            "code_actions": [],
            "diagnostics": [
                {
                    "message": "invalid syntax",
                    "range": {
                        "end": {"character": 6, "line": 0},
                        "start": {"character": 5, "line": 0},
                    },
                    "severity": 1,
                    "source": "mypy",
                },
                {
                    "code": "",
                    "message": "invalid syntax",
                    "range": {
                        "end": {"character": 5, "line": 0},
                        "start": {"character": 4, "line": 0},
                    },
                    "severity": 1,
                    "source": "pyflakes",
                },
            ],
        }
    }


@pytest.fixture
def minimal_bad_code() -> shapes.MIMECode:
    return typ.cast(
        shapes.MIMECode, {"text/x-ipython": [{"cell_id": "1", "code": "x = \n(1\n)"}]}
    )


def test_formatter_call(
    formatter: AnnotationFormatter,
    minimal_clean_code: shapes.MIMECode,
    minimal_bad_code: shapes.MIMECode,
    minimal_empty_response: shapes.MIMEAnnotations,
    minimal_annotations: shapes.MIMEAnnotations,
) -> None:
    assert minimal_empty_response == formatter(
        cell_id="1", code=minimal_clean_code, metadata={}
    )

    observed = formatter(cell_id="1", code=minimal_bad_code, metadata={})
    assert minimal_annotations == observed, observed
