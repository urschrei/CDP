"""The pixel size of sign photographs, read from the header of their PNG files."""

import struct

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
# The width and the height of the image, in the IHDR chunk after the signature.
PNG_SIZE = slice(16, 24)


def image_size(data: bytes) -> tuple[int, int] | None:
    """Return the width and the height of a PNG image, or None."""
    if not data.startswith(PNG_SIGNATURE) or len(data) < PNG_SIZE.stop:
        return None
    width, height = struct.unpack(">II", data[PNG_SIZE])
    return width, height
