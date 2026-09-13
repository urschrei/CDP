import struct
from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient

from cdpp.images import image_size

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + struct.pack(">II", 300, 200)
GIF = b"GIF89a" + struct.pack("<HH", 221, 156) + b"\x00" * 10


@pytest.mark.parametrize(
    ("data", "size"),
    [(PNG, (300, 200)), (PNG[:20], None), (GIF, None), (b"png", None)],
)
def test_images_have_the_size_of_their_png_header(
    data: bytes, size: tuple[int, int] | None
) -> None:
    assert image_size(data) == size


def test_photographs_are_sent_as_png_images(app: Flask, client: FlaskClient) -> None:
    (Path(app.config["MEDIA_ROOT"]) / "instance" / "I_7.png").write_bytes(PNG)

    response = client.get("/media/instance/I_7.png")

    assert response.status_code == 200
    assert response.content_type == "image/png"
    assert response.data == PNG


def test_missing_photograph_is_not_found(client: FlaskClient) -> None:
    assert client.get("/media/instance/I_8.png").status_code == 404
