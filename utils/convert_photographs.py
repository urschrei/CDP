"""Convert the sign photographs to PNG, without a change to their pixels.

The photographs have the extension .jpg, but most of them are GIF images. A GIF
image becomes an 8-bit PNG image with the same palette, palette indices and
transparent colour. A JPEG image becomes a 24-bit PNG image with the pixels
that Pillow decodes.

The script compares each PNG image with its source image. If one image is
different, the script stops and removes no source file. If all images are the
same, it removes the source files, and writes the size and the SHA-256 of each
source file and each PNG file to media/photograph-conversion.csv. The source
files stay in the version history.

Run it from the project directory:

    uv run utils/convert_photographs.py
"""

import csv
import hashlib
import io
from concurrent.futures import ProcessPoolExecutor
from dataclasses import astuple, dataclass, fields
from pathlib import Path

from PIL import Image

PHOTOGRAPHS = Path("media/instance")
MANIFEST = Path("media/photograph-conversion.csv")
SOURCE_SUFFIX = ".jpg"
SOURCE_FORMATS = frozenset({"GIF", "JPEG"})
SOURCE_MODES = frozenset({"P", "L", "RGB"})
ORIENTATION_TAG = 0x0112


class ConversionError(Exception):
    """A photograph cannot become a PNG image with the same pixels."""


@dataclass(frozen=True)
class Conversion:
    filename: str
    source_type: str
    source_bytes: int
    source_sha256: str
    png_bytes: int
    png_sha256: str


def differences(source: Image.Image, copy: Image.Image) -> list[str]:
    """Return the properties of ``copy`` that are not the same in ``source``."""
    found = []
    if copy.mode != source.mode or copy.size != source.size:
        found.append("mode or size")
    elif copy.tobytes() != source.tobytes():
        found.append("pixel values")
    if source.mode == "P":
        palette = source.getpalette() or []
        if (copy.getpalette() or [])[: len(palette)] != palette:
            found.append("palette")
    for key in ("transparency", "icc_profile"):
        if copy.info.get(key) != source.info.get(key):
            found.append(key)
    if copy.convert("RGBA").tobytes() != source.convert("RGBA").tobytes():
        found.append("colours")
    return found


def png_data(path: Path) -> tuple[Conversion, bytes]:
    """Return the PNG image of the photograph at ``path``, after a comparison."""
    data = path.read_bytes()
    with Image.open(io.BytesIO(data)) as source:
        kind = source.format
        if kind not in SOURCE_FORMATS or source.mode not in SOURCE_MODES:
            raise ConversionError(f"{path.name}: {kind} image in mode {source.mode}")
        if getattr(source, "n_frames", 1) != 1:
            raise ConversionError(f"{path.name}: the image has more than one frame")
        if source.getexif().get(ORIENTATION_TAG, 1) != 1:
            raise ConversionError(f"{path.name}: the image has an EXIF orientation")
        source.load()
        buffer = io.BytesIO()
        source.save(buffer, "PNG", optimize=True)
        png = buffer.getvalue()
        with Image.open(io.BytesIO(png)) as copy:
            copy.load()
            if found := differences(source, copy):
                raise ConversionError(
                    f"{path.name}: the PNG image has other {', '.join(found)}"
                )
    conversion = Conversion(
        filename=path.stem,
        source_type=kind,
        source_bytes=len(data),
        source_sha256=hashlib.sha256(data).hexdigest(),
        png_bytes=len(png),
        png_sha256=hashlib.sha256(png).hexdigest(),
    )
    return conversion, png


def write_png(path: Path) -> Conversion:
    conversion, png = png_data(path)
    path.with_suffix(".png").write_bytes(png)
    return conversion


def convert_all(directory: Path, manifest: Path) -> list[Conversion]:
    """Convert the photographs in ``directory``, and add them to ``manifest``.

    Return the conversions of this run. A file that the manifest already has
    stays in it.
    """
    sources = sorted(directory.glob(f"*{SOURCE_SUFFIX}"))
    with ProcessPoolExecutor() as executor:
        conversions = list(executor.map(write_png, sources, chunksize=64))
    rows = read_manifest(manifest) | {
        conversion.filename: astuple(conversion) for conversion in conversions
    }
    with manifest.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(field.name for field in fields(Conversion))
        writer.writerows(rows[filename] for filename in sorted(rows))
    for source in sources:
        source.unlink()
    return conversions


def read_manifest(manifest: Path) -> dict[str, tuple[str, ...]]:
    if not manifest.is_file():
        return {}
    with manifest.open(encoding="utf-8", newline="") as file:
        rows = list(csv.reader(file))
    return {row[0]: tuple(row) for row in rows[1:]}


def megabytes(count: int) -> str:
    return f"{count / 1_000_000:.1f} MB"


def main() -> None:
    conversions = convert_all(PHOTOGRAPHS, MANIFEST)
    for kind in sorted(SOURCE_FORMATS):
        converted = [item for item in conversions if item.source_type == kind]
        before = sum(item.source_bytes for item in converted)
        after = sum(item.png_bytes for item in converted)
        print(
            f"{kind}: {len(converted)} photographs, "
            f"{megabytes(before)} before, {megabytes(after)} after."
        )


if __name__ == "__main__":
    main()
