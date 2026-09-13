"""The record of a sign photograph, in the metadata of its PNG file.

A downloaded photograph contains the records of its instance, its sign and its
tablet, as the database has them at the time of the download. An XMP packet
contains all the values. EXIF contains a description. The image data does not
change.
"""

import re
import struct
from collections.abc import Sequence
from dataclasses import dataclass
from xml.sax.saxutils import escape

from sqlalchemy.orm import joinedload, selectinload

from cdpp.catalogues import catalogue_links
from cdpp.db import db
from cdpp.editing import last_change_set
from cdpp.images import Chunk, with_chunks
from cdpp.models import Cdp, Correspondent, Instance, Sign, SignListEntry, Tablet
from cdpp.views import instance_location, tablet_details

CREDIT = "CDP Project"
NAMESPACES = {
    "dc": "http://purl.org/dc/elements/1.1/",
    "photoshop": "http://ns.adobe.com/photoshop/1.0/",
    "Iptc4xmpExt": "http://iptc.org/std/Iptc4xmpExt/2008-02-29/",
    "cdp": "https://github.com/urschrei/CDP/ns/1.0/",
}
# ISO 639 codes of the languages of the instances.
LANGUAGE_CODES = {
    "Akkadian": "akk",
    "Elamite": "elx",
    "Hittite": "hit",
    "Hurrian": "xhu",
    "Sumerian": "sux",
}
# CDP property names of the tablet details whose label changes with the number
# of values, or whose label is also the label of an instance field.
DETAIL_PROPERTIES = {
    "Ruler": "rulers",
    "Rulers": "rulers",
    "Language": "languages",
    "Languages": "languages",
    "Function": "tabletFunction",
    "Notes": "tabletNotes",
}
# CDP properties that are lists, also when they have one value.
LIST_PROPERTIES = frozenset(
    {
        "signNames",
        "signListEntries",
        "rulers",
        "sentTo",
        "languages",
        "cdliEntries",
        "oraccTexts",
    }
)
INSTANCE_OPTIONS = (
    joinedload(Instance.surface),
    joinedload(Instance.function),
    joinedload(Instance.language),
    selectinload(Instance.sign)
    .selectinload(Sign.cdp_records)
    .options(
        selectinload(Cdp.names),
        selectinload(Cdp.sign_list_entries).joinedload(SignListEntry.sign_list),
    ),
    joinedload(Instance.tablet).options(
        selectinload(Tablet.rulers),
        selectinload(Tablet.recipients).options(
            joinedload(Correspondent.ruler),
            joinedload(Correspondent.non_ruler),
        ),
    ),
)
# XML 1.0 does not allow the characters outside these ranges.
XML_INVALID_RE = re.compile("[^\t\n\r\x20-\ud7ff\ue000-\ufffd\U00010000-\U0010ffff]")
# The keyword of an iTXt chunk with an XMP packet. The empty compression flag,
# compression method, language tag and translated keyword follow it.
XMP_KEYWORD = b"XML:com.adobe.xmp\x00"
XMP_HEADER = XMP_KEYWORD + b"\x00\x00\x00\x00"
# TIFF field types and the size of one value of each type, and the EXIF tags.
ASCII, LONG, UNDEFINED = 2, 4, 7
TYPE_SIZES = {ASCII: 1, LONG: 4, UNDEFINED: 1}
IMAGE_DESCRIPTION, ARTIST, EXIF_IFD, USER_COMMENT = 0x010E, 0x013B, 0x8769, 0x9286
TIFF_HEADER = b"II" + struct.pack("<HI", 42, 8)
IFD_COUNT = struct.Struct("<H")
IFD_ENTRY = struct.Struct("<HHI4s")
IFD_NEXT = struct.Struct("<I")
UNICODE_COMMENT = b"UNICODE\x00"

type Value = str | list[str]
type Properties = list[tuple[str, Value]]


@dataclass(frozen=True)
class PhotographRecord:
    """The values in the metadata of one photograph.

    ``summary`` is ASCII text for EXIF. ``properties`` are the CDP properties.
    """

    title: str
    description: str
    summary: str
    page_url: str
    museum_number: str
    date: str
    subjects: list[str]
    languages: list[str]
    properties: Properties


def load_instance(instance_id: int) -> Instance | None:
    """Return the instance with the records that its metadata contains."""
    # Load the related records again if the session already contains them.
    return db.session.get(
        Instance, instance_id, options=INSTANCE_OPTIONS, populate_existing=True
    )


def photograph_record(
    instance: Instance, instance_url: str, tablet_url: str
) -> PhotographRecord:
    sign, tablet = instance.sign, instance.tablet
    names = sign_names(sign)
    tablet_values = tablet_properties(tablet, tablet_url)
    dates = dict(tablet_values)
    location = instance_location(instance)
    description = f"Photograph of the sign {sign.sign_ref} on the tablet"
    description += f" {tablet.museum_number}"
    language = instance.language.name if instance.language else None
    return PhotographRecord(
        title=f"Instance of {sign.sign_ref} on {tablet.museum_number}",
        description=f"{description}: {location}." if location else f"{description}.",
        summary=(
            f"Photograph of sign instance {instance.id}"
            f" on tablet {tablet.museum_number}: {instance_url}"
        ),
        page_url=instance_url,
        museum_number=tablet.museum_number,
        date=", ".join(
            value
            for name in ("period", "subPeriod", "year")
            if isinstance(value := dates.get(name), str)
        ),
        subjects=[sign.sign_ref, *names],
        languages=[LANGUAGE_CODES[language]] if language in LANGUAGE_CODES else [],
        properties=instance_properties(instance, instance_url, names) + tablet_values,
    )


def sign_names(sign: Sign) -> list[str]:
    """Return the names of ``sign`` in the sign lists, other than its CDP name."""
    names = {name.name for record in sign.cdp_records for name in record.names}
    return sorted(names - {sign.sign_ref})


def instance_properties(
    instance: Instance, instance_url: str, names: list[str]
) -> Properties:
    entries = sorted(
        {
            (entry.sign_list.position, entry.sign_list.name, entry.number)
            for record in instance.sign.cdp_records
            for entry in record.sign_list_entries
        }
    )
    change_set = last_change_set("instance", instance.id)
    values: list[tuple[str, Value | None]] = [
        ("instanceId", str(instance.id)),
        ("instancePage", instance_url),
        ("filename", instance.filename),
        ("sign", instance.sign.sign_ref),
        ("signNames", names),
        ("signListEntries", [f"{name} {number}" for _, name, number in entries]),
        ("position", instance_location(instance)),
        ("surface", instance.surface.name if instance.surface else None),
        ("column", instance.column),
        ("line", instance.line),
        ("iteration", instance.iteration),
        ("function", instance.function.name if instance.function else None),
        ("language", instance.language.name if instance.language else None),
        ("notes", instance.notes),
        ("jjtNotes", instance.jjt_notes),
        ("lastChangeSet", str(change_set.id) if change_set else None),
        (
            "lastChanged",
            f"{change_set.created_at.isoformat()}Z" if change_set else None,
        ),
    ]
    return [(name, value) for name, value in values if value]


def tablet_properties(tablet: Tablet, tablet_url: str) -> Properties:
    """Return the tablet details that the tablet page shows, and its catalogue links."""
    properties: Properties = [
        ("tabletId", str(tablet.id)),
        ("tabletPage", tablet_url),
        ("museumNumber", tablet.museum_number),
    ]
    for detail in tablet_details(tablet):
        name = DETAIL_PROPERTIES.get(detail.label) or property_name(detail.label)
        texts = [text for text, _ in detail.values]
        properties.append(
            (name, texts if name in LIST_PROPERTIES else ", ".join(texts))
        )
    links = catalogue_links(tablet.id)
    cdli = [url for label, urls in links if label == "CDLI" for _, url in urls]
    oracc = [url for label, urls in links if label != "CDLI" for _, url in urls]
    properties += [
        (name, urls)
        for name, urls in (("cdliEntries", cdli), ("oraccTexts", oracc))
        if urls
    ]
    return properties


def property_name(label: str) -> str:
    """Return the XMP property name of a label, as in "subPeriod" for "Sub-period"."""
    first, *others = re.split(r"[\s-]+", label)
    return first.lower() + "".join(word.capitalize() for word in others)


def photograph_with_metadata(png: bytes, record: PhotographRecord) -> bytes:
    """Return ``png`` with the metadata of ``record`` in place of its XMP and EXIF."""
    added = [
        Chunk(b"eXIf", exif_data(record)),
        Chunk(b"iTXt", XMP_HEADER + xmp_packet(record).encode()),
    ]
    return with_chunks(png, added, replaces=is_metadata)


def is_metadata(chunk: Chunk) -> bool:
    return chunk.kind == b"eXIf" or (
        chunk.kind == b"iTXt" and chunk.data.startswith(XMP_KEYWORD)
    )


# XMP


def xmp_packet(record: PhotographRecord) -> str:
    artwork = (
        alternative("Iptc4xmpExt:AOTitle", record.museum_number)
        + simple("Iptc4xmpExt:AOSourceInvNo", record.museum_number)
        + (simple("Iptc4xmpExt:AOCircaDateCreated", record.date) if record.date else "")
    )
    elements = [
        alternative("dc:title", record.title),
        alternative("dc:description", record.description),
        simple("dc:identifier", record.page_url),
        simple("dc:source", record.museum_number),
        simple("dc:format", "image/png"),
        array("dc:creator", "Seq", [CREDIT]),
        array("dc:subject", "Bag", record.subjects),
        *([array("dc:language", "Bag", record.languages)] if record.languages else []),
        simple("photoshop:Credit", CREDIT),
        "<Iptc4xmpExt:ArtworkOrObject><rdf:Bag>"
        f'<rdf:li rdf:parseType="Resource">{artwork}</rdf:li>'
        "</rdf:Bag></Iptc4xmpExt:ArtworkOrObject>",
        *(
            array(f"cdp:{name}", "Bag", value)
            if isinstance(value, list)
            else simple(f"cdp:{name}", value)
            for name, value in record.properties
        ),
    ]
    namespaces = "".join(
        f' xmlns:{prefix}="{uri}"' for prefix, uri in NAMESPACES.items()
    )
    body = "".join(f"   {element}\n" for element in elements)
    return (
        '<?xpacket begin="\ufeff" id="W5M0MpCehiHzreSzNTczkc9d"?>\n'
        '<x:xmpmeta xmlns:x="adobe:ns:meta/">\n'
        ' <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">\n'
        f'  <rdf:Description rdf:about=""{namespaces}>\n'
        f"{body}"
        "  </rdf:Description>\n"
        " </rdf:RDF>\n"
        "</x:xmpmeta>\n"
        '<?xpacket end="r"?>'
    )


def xml_text(value: str) -> str:
    return escape(XML_INVALID_RE.sub("", value))


def simple(name: str, value: str) -> str:
    return f"<{name}>{xml_text(value)}</{name}>"


def alternative(name: str, value: str) -> str:
    item = f'<rdf:li xml:lang="x-default">{xml_text(value)}</rdf:li>'
    return f"<{name}><rdf:Alt>{item}</rdf:Alt></{name}>"


def array(name: str, kind: str, values: Sequence[str]) -> str:
    items = "".join(f"<rdf:li>{xml_text(value)}</rdf:li>" for value in values)
    return f"<{name}><rdf:{kind}>{items}</rdf:{kind}></{name}>"


# EXIF


def exif_data(record: PhotographRecord) -> bytes:
    """Return the TIFF structure of the EXIF data of a photograph.

    ImageDescription is ASCII, so it contains the ASCII summary. UserComment
    contains the description in UTF-16.
    """
    first = [
        (IMAGE_DESCRIPTION, ASCII, ascii_value(record.summary)),
        (ARTIST, ASCII, ascii_value(CREDIT)),
    ]
    comment = UNICODE_COMMENT + record.description.encode("utf-16-le")
    placeholder = ifd([*first, (EXIF_IFD, LONG, bytes(4))], len(TIFF_HEADER))
    exif_offset = len(TIFF_HEADER) + len(placeholder)
    pointer = (EXIF_IFD, LONG, struct.pack("<I", exif_offset))
    return (
        TIFF_HEADER
        + ifd([*first, pointer], len(TIFF_HEADER))
        + ifd([(USER_COMMENT, UNDEFINED, comment)], exif_offset)
    )


def ascii_value(text: str) -> bytes:
    return text.encode("ascii", "replace") + b"\x00"


def ifd(entries: list[tuple[int, int, bytes]], offset: int) -> bytes:
    """Return a TIFF image file directory at ``offset``, followed by its values."""
    size = IFD_COUNT.size + IFD_ENTRY.size * len(entries) + IFD_NEXT.size
    fields = IFD_COUNT.pack(len(entries))
    values = b""
    for tag, kind, data in sorted(entries):
        if len(data) <= 4:
            location = data.ljust(4, b"\x00")
        else:
            location = struct.pack("<I", offset + size + len(values))
            # A value starts at an even offset.
            values += data + b"\x00" * (len(data) % 2)
        fields += IFD_ENTRY.pack(tag, kind, len(data) // TYPE_SIZES[kind], location)
    return fields + IFD_NEXT.pack(0) + values
