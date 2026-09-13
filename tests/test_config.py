from pathlib import Path

import pytest

from cdpp import create_app


def app_config(tmp_path: Path) -> dict[str, object]:
    config = {"SQLALCHEMY_DATABASE_URI": "sqlite://", "MEDIA_ROOT": str(tmp_path)}
    return create_app(config).config


@pytest.mark.parametrize("commit", ["1234567", "1234567e8", "f82b7447f17d"])
def test_commit_is_the_text_of_the_environment_variable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, commit: str
) -> None:
    monkeypatch.setenv("CDPP_COMMIT", commit)

    assert app_config(tmp_path)["COMMIT"] == commit


def test_commit_is_none_without_the_environment_variable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("CDPP_COMMIT", raising=False)

    assert app_config(tmp_path)["COMMIT"] is None
