"""The type and the pixel size of sign photographs, read from their files.

The photographs have the extension .jpg, but most of them are GIF images.
"""

import struct
from pathlib import Path

GIF_SIGNATURES = (b"GIF87a", b"GIF89a")
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
JPEG_SIGNATURE = b"\xff\xd8\xff"
# JPEG markers that start a frame and give its size.
JPEG_FRAME_MARKERS = frozenset(
    {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
)
# JPEG markers without a length field.
JPEG_STANDALONE_MARKERS = frozenset({0x01, *range(0xD0, 0xD9)})


def image_type(data: bytes) -> str | None:
    """Return the MIME type of an image from its first bytes, or None."""
    if data.startswith(GIF_SIGNATURES):
        return "image/gif"
    if data.startswith(PNG_SIGNATURE):
        return "image/png"
    if data.startswith(JPEG_SIGNATURE):
        return "image/jpeg"
    return None


def file_type(path: Path) -> str | None:
    """Return the MIME type of the image file at ``path``, or None."""
    with path.open("rb") as file:
        return image_type(file.read(len(PNG_SIGNATURE)))


def image_size(data: bytes) -> tuple[int, int] | None:
    """Return the width and the height of a GIF, PNG or JPEG image, or None."""
    kind = image_type(data)
    if kind == "image/gif" and len(data) >= 10:
        width, height = struct.unpack("<HH", data[6:10])
        return width, height
    if kind == "image/png" and len(data) >= 24:
        width, height = struct.unpack(">II", data[16:24])
        return width, height
    if kind == "image/jpeg":
        return jpeg_size(data)
    return None


def jpeg_size(data: bytes) -> tuple[int, int] | None:
    index = 2
    while index + 4 <= len(data):
        if data[index] != 0xFF:
            return None
        marker = data[index + 1]
        if marker == 0xFF:
            index += 1
            continue
        if marker in JPEG_STANDALONE_MARKERS:
            index += 2
            continue
        (length,) = struct.unpack(">H", data[index + 2 : index + 4])
        if marker in JPEG_FRAME_MARKERS and index + 9 <= len(data):
            height, width = struct.unpack(">HH", data[index + 5 : index + 9])
            return width, height
        index += 2 + length
    return None
