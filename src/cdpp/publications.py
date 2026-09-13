"""The parts of the publication of a tablet, and a citation in one form.

The publications in the data have many forms, as in SAA 8, 70, RIME.4.3.6.12,
MSL 14 p. 19: Bk and Jeyes (1989) no. 11. The data keep the original text. A
part that the parser does not identify stays in ``rest``.
"""

import re
from dataclasses import dataclass

RIM = re.compile(r"(?P<series>RIM[AE])\.(?P<number>\d+(?:/\d+)?(?:\.\d+)+)")
AUTHOR_YEAR = re.compile(r"(?P<series>[A-Z][a-z]+ \(\d{4}\))(?P<rest>.*)")
AUTHOR_SERIES = re.compile(r"(?P<series>[A-Z][a-z]+, [A-Z][A-Za-z]+)(?P<rest>.*)")
SERIES = re.compile(
    r"(?P<series>[A-Z][A-Za-z]*(?: SS)?) (?P<volume>\d+(?:,\d+)?)"
    r"(?: \((?P<year>\d{4})\))?(?P<rest>.*)"
)
# The locators that can follow a series or a volume, in any order.
LOCATORS = (
    re.compile(r",?\s*pp?\.\s*(?P<page>\d+(?:-\d+)?(?: f\.)?)"),
    re.compile(r"\s*(?P<page>\d+)(?= no\.)"),
    re.compile(r",?\s*no\.\s*(?P<number>\d+)"),
    re.compile(r",\s*(?P<number>[A-Z]?\d+)$"),
    re.compile(r"\s*\((?P<number>\d+)\)"),
    re.compile(r":\s*(?P<siglum>[A-Z][a-z]{0,2})$"),
)


@dataclass(frozen=True)
class Publication:
    """The parts of a publication. A part that the text does not give is None."""

    original: str
    series: str | None = None
    volume: str | None = None
    year: str | None = None
    page: str | None = None
    number: str | None = None
    siglum: str | None = None
    rest: str | None = None

    @property
    def citation(self) -> str:
        """Return the publication in one form, as in "MSL 14, p. 19, Bk"."""
        if self.series is None:
            return self.original
        head = " ".join(
            part
            for part in (self.series, self.volume, self.year and f"({self.year})")
            if part
        )
        page = self.page and (
            f"pp. {self.page}" if "-" in self.page else f"p. {self.page}"
        )
        number = self.number and f"no. {self.number}"
        citation = ", ".join(part for part in (head, page, number, self.siglum) if part)
        if not self.rest:
            return citation
        separator = "" if self.rest[0] in ",:" else " "
        return f"{citation}{separator}{self.rest}"


def parse_publication(text: str) -> Publication:
    """Return the parts of the publication of a tablet."""
    text = text.strip()
    if match := RIM.fullmatch(text):
        return rim_publication(text, match["series"], match["number"])
    for pattern in (AUTHOR_YEAR, AUTHOR_SERIES):
        if match := pattern.fullmatch(text):
            return with_locators(
                Publication(text, series=match["series"]), match["rest"]
            )
    if match := SERIES.fullmatch(text):
        # A number without a locator after the series, as in AAT 27, can be a
        # volume, a text or a plate.
        if not match["rest"] and not match["year"]:
            return Publication(text, series=match["series"], rest=match["volume"])
        publication = Publication(
            text, series=match["series"], volume=match["volume"], year=match["year"]
        )
        return with_locators(publication, match["rest"])
    return Publication(text)


def rim_publication(text: str, series: str, number: str) -> Publication:
    """Return the parts of a number of the Royal Inscriptions of Mesopotamia.

    RIME.4.3.6.12 is RIME 4, E4.3.6.12. RIMA.0.76.1 is A.0.76.1, with no
    volume. RIMA.1.0.60.1 is RIMA 1, A.0.60.1.
    """
    parts = number.split(".")
    if series == "RIME":
        return Publication(text, series, volume=parts[0], number=f"E{number}")
    if len(parts) == 4:
        return Publication(
            text, series, volume=parts[0], number="A." + ".".join(parts[1:])
        )
    return Publication(text, series, number=f"A.{number}")


def with_locators(publication: Publication, rest: str) -> Publication:
    """Return the publication with the page, number and siglum found in ``rest``."""
    found: dict[str, str] = {}
    rest = rest.strip() if not rest.startswith((",", ":")) else rest
    while rest:
        for pattern in LOCATORS:
            match = pattern.match(rest)
            if match is None:
                continue
            ((name, value),) = match.groupdict().items()
            if name in found:
                continue
            found[name] = value
            rest = rest[match.end() :].lstrip(" ") if match.end() else rest
            break
        else:
            break
    return Publication(
        publication.original,
        series=publication.series,
        volume=publication.volume,
        year=publication.year,
        page=found.get("page"),
        number=found.get("number"),
        siglum=found.get("siglum"),
        rest=rest.strip() or None,
    )
