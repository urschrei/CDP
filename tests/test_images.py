import struct
from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient

from cdpp.images import image_size, image_type

GIF = b"GIF89a" + struct.pack("<HH", 221, 156) + b"\x00" * 10
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + struct.pack(">II", 300, 200)
JPEG = (
    b"\xff\xd8"
    + b"\xff\xe0"
    + struct.pack(">H", 16)
    + b"JFIF\x00"
    + b"\x00" * 9
    + b"\xff\xc0"
    + struct.pack(">HBHH", 17, 8, 120, 640)
    + b"\x00" * 10
)


@pytest.mark.parametrize(
    ("data", "kind", "size"),
    [
        (GIF, "image/gif", (221, 156)),
        (PNG, "image/png", (300, 200)),
        (JPEG, "image/jpeg", (640, 120)),
        (b"jpeg", None, None),
    ],
)
def test_images_have_the_type_and_size_of_their_header(
    data: bytes, kind: str | None, size: tuple[int, int] | None
) -> None:
    assert image_type(data) == kind
    assert image_size(data) == size


@pytest.mark.parametrize(
    ("data", "content_type"),
    [(GIF, "image/gif"), (PNG, "image/png"), (JPEG, "image/jpeg")],
)
def test_photographs_are_sent_with_the_type_of_their_content(
    app: Flask, client: FlaskClient, data: bytes, content_type: str
) -> None:
    (Path(app.config["MEDIA_ROOT"]) / "instance" / "I_7.jpg").write_bytes(data)

    response = client.get("/media/instance/I_7.jpg")

    assert response.status_code == 200
    assert response.content_type == content_type


def test_missing_photograph_is_not_found(client: FlaskClient) -> None:
    assert client.get("/media/instance/I_8.jpg").status_code == 404
