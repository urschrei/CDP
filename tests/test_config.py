from pathlib import Path

import pytest

from cdpp import create_app


def app_config(tmp_path: Path) -> dict[str, object]:
    config = {"SQLALCHEMY_DATABASE_URI": "sqlite://", "MEDIA_ROOT": str(tmp_path)}
    return create_app(config).config


@pytest.mark.parametrize(
    ("variable", "key", "value"),
    [
        ("CDPP_COMMIT", "COMMIT", "1234567"),
        ("CDPP_COMMIT", "COMMIT", "1234567e8"),
        ("CDPP_COMMIT", "COMMIT", "f82b7447f17d"),
        ("CDPP_CHANGE", "CHANGE", "null"),
        ("CDPP_CHANGE", "CHANGE", "qqspxxrnkskv"),
    ],
)
def test_versions_are_the_text_of_the_environment_variables(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, variable: str, key: str, value: str
) -> None:
    monkeypatch.setenv(variable, value)

    assert app_config(tmp_path)[key] == value


@pytest.mark.parametrize(
    ("variable", "key"), [("CDPP_COMMIT", "COMMIT"), ("CDPP_CHANGE", "CHANGE")]
)
def test_versions_are_none_without_the_environment_variables(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, variable: str, key: str
) -> None:
    monkeypatch.setenv(variable, "")

    assert app_config(tmp_path)[key] is None
