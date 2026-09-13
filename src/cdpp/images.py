"""The pixel size and the chunks of sign photographs, which are PNG files."""

import struct
import zlib
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
# The width and the height of the image, in the IHDR chunk after the signature.
PNG_SIZE = slice(16, 24)
# The length and the type at the start of a chunk, and the CRC at its end.
CHUNK_START = struct.Struct(">I4s")
CHUNK_CRC = struct.Struct(">I")


@dataclass(frozen=True)
class Chunk:
    kind: bytes
    data: bytes

    def to_bytes(self) -> bytes:
        crc = zlib.crc32(self.kind + self.data)
        return (
            CHUNK_START.pack(len(self.data), self.kind)
            + self.data
            + CHUNK_CRC.pack(crc)
        )


def image_size(data: bytes) -> tuple[int, int] | None:
    """Return the width and the height of a PNG image, or None."""
    if not data.startswith(PNG_SIGNATURE) or len(data) < PNG_SIZE.stop:
        return None
    width, height = struct.unpack(">II", data[PNG_SIZE])
    return width, height


def chunks(png: bytes) -> Iterator[Chunk]:
    """Return the chunks of a PNG file, in order.

    Raise ValueError if the data is not a complete PNG file.
    """
    if not png.startswith(PNG_SIGNATURE):
        raise ValueError("The data is not a PNG file")
    index = len(PNG_SIGNATURE)
    while index < len(png):
        if index + CHUNK_START.size > len(png):
            raise ValueError("The PNG file is not complete")
        length, kind = CHUNK_START.unpack_from(png, index)
        start = index + CHUNK_START.size
        end = start + length
        if end + CHUNK_CRC.size > len(png):
            raise ValueError("The PNG file is not complete")
        yield Chunk(kind, png[start:end])
        index = end + CHUNK_CRC.size


def with_chunks(
    png: bytes, added: Sequence[Chunk], replaces: Callable[[Chunk], bool]
) -> bytes:
    """Return ``png`` with ``added`` before its image data.

    Remove the chunks for which ``replaces`` is true. The image data does not
    change.
    """
    parts = [PNG_SIGNATURE]
    inserted = False
    for chunk in chunks(png):
        if replaces(chunk):
            continue
        if chunk.kind == b"IDAT" and not inserted:
            parts.extend(item.to_bytes() for item in added)
            inserted = True
        parts.append(chunk.to_bytes())
    if not inserted:
        raise ValueError("The PNG file has no image data")
    return b"".join(parts)
