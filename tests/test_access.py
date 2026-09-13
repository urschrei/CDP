import base64

from flask import Flask
from flask.testing import FlaskClient

from tests.conftest import Sample

PASSWORD = "clay tablet"


def credentials(user: str, password: str) -> dict[str, str]:
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def test_site_without_a_password_is_open(client: FlaskClient, sample: Sample) -> None:
    assert client.get("/").status_code == 200


def test_request_without_the_password_is_refused(
    app: Flask, client: FlaskClient, sample: Sample
) -> None:
    app.config["PASSWORD"] = PASSWORD

    for response in (
        client.get("/"),
        client.get("/", headers=credentials("jjt", "clay")),
        client.post("/changes/1/undo"),
    ):
        assert response.status_code == 401
        assert response.headers["WWW-Authenticate"].startswith('Basic realm="CDPP"')


def test_request_with_the_password_continues(
    app: Flask, client: FlaskClient, sample: Sample
) -> None:
    app.config["PASSWORD"] = PASSWORD

    assert client.get("/", headers=credentials("jjt", PASSWORD)).status_code == 200
    assert client.get("/", headers=credentials("", PASSWORD)).status_code == 200
