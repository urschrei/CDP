from pathlib import Path

import pytest
from flask import request

from cdpp import create_app


@pytest.mark.parametrize(("proxies", "scheme"), [(0, "http"), (1, "https")])
def test_forwarded_scheme_is_used_only_behind_trusted_proxies(
    tmp_path: Path, proxies: int, scheme: str
) -> None:
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "MEDIA_ROOT": str(tmp_path),
            "TRUSTED_PROXIES": proxies,
        }
    )
    app.add_url_rule("/scheme", "scheme", lambda: request.scheme)

    response = app.test_client().get("/scheme", headers={"X-Forwarded-Proto": "https"})

    assert response.get_data(as_text=True) == scheme
