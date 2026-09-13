"""Years in astronomical numbering, and their text on pages.

Astronomical numbering has a year 0: 1 BC is 0, 2 BC is -1, and 1 AD is 1.
"""

import re

YEAR_PATTERN = re.compile(r"(\d+)\s*(BC|AD)", re.IGNORECASE)


def year_number(text: str) -> int:
    """Return the number of a year, as in -1243 for "1244 BC" and 75 for "75 AD".

    Raise ValueError if the text is not a year.
    """
    match = YEAR_PATTERN.fullmatch(text.strip())
    if match is None or int(match[1]) == 0:
        raise ValueError(f"Not a year: {text!r}")
    number = int(match[1])
    return 1 - number if match[2].upper() == "BC" else number


def year_text(number: int) -> str:
    """Return a year as pages show it, as in "1244 BC" for -1243."""
    return f"{1 - number} BC" if number <= 0 else f"{number} AD"
