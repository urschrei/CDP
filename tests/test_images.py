import struct
from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient

from cdpp.images import PNG_SIGNATURE, Chunk, chunks, image_size, with_chunks

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


def png_file(*items: Chunk) -> bytes:
    return PNG_SIGNATURE + b"".join(item.to_bytes() for item in items)


def test_added_chunks_go_before_the_image_data_and_replace_chunks() -> None:
    header, data, end = Chunk(b"IHDR", b"h"), Chunk(b"IDAT", b"d"), Chunk(b"IEND", b"")
    png = png_file(header, Chunk(b"tEXt", b"old"), data, data, end)

    result = with_chunks(
        png, [Chunk(b"tEXt", b"new")], replaces=lambda chunk: chunk.kind == b"tEXt"
    )

    assert list(chunks(result)) == [header, Chunk(b"tEXt", b"new"), data, data, end]


def test_chunks_need_a_complete_png_file_with_image_data() -> None:
    header, end = Chunk(b"IHDR", b"h"), Chunk(b"IEND", b"")

    with pytest.raises(ValueError, match="no image data"):
        with_chunks(png_file(header, end), [], replaces=lambda _: False)
    with pytest.raises(ValueError, match="not complete"):
        list(chunks(png_file(header, end)[:-2]))
    with pytest.raises(ValueError, match="not a PNG file"):
        list(chunks(GIF))


def test_photographs_are_sent_as_png_images(app: Flask, client: FlaskClient) -> None:
    (Path(app.config["MEDIA_ROOT"]) / "instance" / "I_7.png").write_bytes(PNG)

    response = client.get("/media/instance/I_7.png")

    assert response.status_code == 200
    assert response.content_type == "image/png"
    assert response.data == PNG


def test_missing_photograph_is_not_found(client: FlaskClient) -> None:
    assert client.get("/media/instance/I_8.png").status_code == 404
