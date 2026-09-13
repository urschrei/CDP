import csv
import io
from pathlib import Path

import pytest
from PIL import Image

from utils.convert_photographs import ConversionError, convert_all


def gif_data(frames: int = 1) -> bytes:
    image = Image.new("P", (4, 3))
    image.putpalette([value for index in range(256) for value in (index, 0, 255)])
    image.putdata([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 200])
    others = []
    for frame in range(1, frames):
        other = image.copy()
        other.putpixel((0, 0), frame + 20)
        others.append(other)
    buffer = io.BytesIO()
    # Keep the palette indices, so that index 200 stays the transparent colour.
    image.save(
        buffer,
        "GIF",
        optimize=False,
        transparency=200,
        save_all=frames > 1,
        append_images=others,
    )
    return buffer.getvalue()


def jpeg_data() -> bytes:
    image = Image.new("RGB", (8, 8))
    image.putdata([(x * 30, y * 30, 128) for y in range(8) for x in range(8)])
    buffer = io.BytesIO()
    image.save(buffer, "JPEG")
    return buffer.getvalue()


def pixels(data: bytes) -> tuple[str, bytes, bytes]:
    with Image.open(io.BytesIO(data)) as image:
        return image.mode, image.tobytes(), image.convert("RGBA").tobytes()


def test_photographs_become_png_images_with_the_same_pixels(tmp_path: Path) -> None:
    sources = {"I_1": gif_data(), "I_2": jpeg_data()}
    for name, data in sources.items():
        (tmp_path / f"{name}.jpg").write_bytes(data)
    manifest = tmp_path / "manifest.csv"

    conversions = convert_all(tmp_path, manifest)

    assert [item.source_type for item in conversions] == ["GIF", "JPEG"]
    assert sorted(path.name for path in tmp_path.glob("I_*")) == ["I_1.png", "I_2.png"]
    for name, data in sources.items():
        png = (tmp_path / f"{name}.png").read_bytes()
        assert png.startswith(b"\x89PNG")
        assert pixels(png) == pixels(data)
    with Image.open(tmp_path / "I_1.png") as image:
        assert image.mode == "P"
        assert image.info["transparency"] == 200
    with manifest.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    assert [(row["filename"], row["source_type"]) for row in rows] == [
        ("I_1", "GIF"),
        ("I_2", "JPEG"),
    ]
    assert rows[0]["source_bytes"] == str(len(sources["I_1"]))


def test_a_second_run_keeps_the_manifest(tmp_path: Path) -> None:
    (tmp_path / "I_1.jpg").write_bytes(gif_data())
    manifest = tmp_path / "manifest.csv"
    convert_all(tmp_path, manifest)
    text = manifest.read_text(encoding="utf-8")

    assert convert_all(tmp_path, manifest) == []
    assert manifest.read_text(encoding="utf-8") == text


def test_an_animated_image_stops_the_conversion(tmp_path: Path) -> None:
    (tmp_path / "I_1.jpg").write_bytes(gif_data())
    (tmp_path / "I_2.jpg").write_bytes(gif_data(frames=2))
    manifest = tmp_path / "manifest.csv"

    with pytest.raises(ConversionError, match=r"I_2\.jpg: the image has more than one"):
        convert_all(tmp_path, manifest)

    assert (tmp_path / "I_1.jpg").is_file()
    assert (tmp_path / "I_2.jpg").is_file()
    assert not manifest.exists()
