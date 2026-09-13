import io
from xml.etree import ElementTree

from flask import Flask
from PIL import Image
from sqlalchemy import select

from cdpp.db import db
from cdpp.models import Instance
from cdpp.photograph_metadata import (
    NAMESPACES,
    PhotographRecord,
    load_instance,
    photograph_record,
    photograph_with_metadata,
    property_name,
)
from tests.conftest import Sample

XML_NAMESPACES = NAMESPACES | {"rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"}
USER_COMMENT = 0x9286
COMMIT = "f82b7447f17d249e1e7bc75065e8855094b37337"
REVISION = "f6c2a8e4d913"


def png_data() -> bytes:
    image = Image.new("P", (3, 2))
    image.putpalette([value for index in range(256) for value in (index, 9, 9)])
    image.putdata([0, 1, 2, 3, 4, 5])
    buffer = io.BytesIO()
    image.save(buffer, "PNG", transparency=5)
    return buffer.getvalue()


def sample_instance(sample: Sample) -> Instance:
    instance_id = db.session.scalar(
        select(Instance.id).where(
            Instance.tablet_id == sample.tablet.id, Instance.filename == "I_1"
        )
    )
    assert instance_id is not None
    instance = load_instance(instance_id)
    assert instance is not None
    return instance


def sample_record(instance: Instance) -> PhotographRecord:
    return photograph_record(
        instance,
        f"https://cdpp.example/instances/{instance.id}",
        f"https://cdpp.example/tablets/{instance.tablet_id}",
        commit=COMMIT,
        revision=REVISION,
    )


def xmp_values(xmp: str) -> dict[str, list[str]]:
    """Return the text of each property, or of each item of a property."""
    root = ElementTree.fromstring(xmp)
    description = root.find("rdf:RDF/rdf:Description", XML_NAMESPACES)
    assert description is not None
    prefixes = {f"{{{uri}}}": prefix for prefix, uri in XML_NAMESPACES.items()}
    values = {}
    for element in description:
        uri, local = element.tag.split("}")
        items = element.findall(".//rdf:li", XML_NAMESPACES)
        texts = [item.text or "" for item in items] if items else [element.text or ""]
        values[f"{prefixes[uri + '}']}:{local}"] = texts
    return values


def test_metadata_contains_the_records_and_keeps_the_image(
    app: Flask, sample: Sample
) -> None:
    instance = sample_instance(sample)
    png = png_data()

    tagged = photograph_with_metadata(png, sample_record(instance))

    with (
        Image.open(io.BytesIO(png)) as original,
        Image.open(io.BytesIO(tagged)) as image,
    ):
        image.load()
        assert image.tobytes() == original.tobytes()
        assert image.getpalette() == original.getpalette()
        assert image.info["transparency"] == 5
        values = xmp_values(image.info["XML:com.adobe.xmp"])
        exif = image.getexif()
    page = f"https://cdpp.example/instances/{instance.id}"
    assert values["dc:title"] == ["Instance of AŠ on A.1"]
    assert values["dc:identifier"] == [page]
    assert values["dc:subject"] == ["AŠ", "horizontal wedge"]
    assert values["dc:language"] == ["akk"]
    assert values["dc:creator"] == ["CDP Project"]
    assert values["photoshop:Credit"] == ["CDP Project"]
    assert values["cdp:sign"] == ["AŠ"]
    assert values["cdp:signListEntries"] == ["MesZL 1", "LAK 2"]
    assert values["cdp:position"] == ["Obverse, line 1"]
    assert values["cdp:surface"] == ["obverse"]
    assert values["cdp:line"] == ["1"]
    assert values["cdp:language"] == ["Akkadian"]
    assert values["cdp:museumNumber"] == ["A.1"]
    assert values["cdp:rulers"] == ["Zimri-Lim"]
    assert values["cdp:period"] == ["Old Babylonian"]
    assert values["cdp:city"] == ["Mari"]
    assert values["cdp:locality"] == ["Syria"]
    assert values["cdp:sentFrom"] == ["Zimri-Lim"]
    assert values["cdp:languages"] == ["Akkadian"]
    assert values["cdp:tabletNotes"] == ["Letter about barley"]
    assert "cdp:lastChangeSet" not in values
    assert values["cdp:applicationCommit"] == [COMMIT]
    assert values["cdp:databaseRevision"] == [REVISION]
    assert (
        exif[0x010E]
        == f"Photograph of sign instance {instance.id} on tablet A.1: {page}"
    )
    assert exif[0x013B] == "CDP Project"
    comment = exif.get_ifd(0x8769)[USER_COMMENT]
    assert comment.removeprefix(b"UNICODE\x00").decode("utf-16-le") == (
        "Photograph of the sign AŠ on the tablet A.1: Obverse, line 1."
    )


def test_new_metadata_replaces_the_metadata_of_the_file(
    app: Flask, sample: Sample
) -> None:
    instance = sample_instance(sample)
    tagged = photograph_with_metadata(png_data(), sample_record(instance))
    instance.line = "2"

    retagged = photograph_with_metadata(tagged, sample_record(instance))

    assert retagged.count(b"XML:com.adobe.xmp") == 1
    assert retagged.count(b"eXIf") == 1
    with Image.open(io.BytesIO(retagged)) as image:
        assert xmp_values(image.info["XML:com.adobe.xmp"])["cdp:line"] == ["2"]


def test_metadata_escapes_text_and_omits_characters_that_xml_does_not_allow(
    app: Flask, sample: Sample
) -> None:
    instance = sample_instance(sample)
    instance.tablet.notes = "Barley & <wheat>\x0b"

    tagged = photograph_with_metadata(png_data(), sample_record(instance))

    with Image.open(io.BytesIO(tagged)) as image:
        values = xmp_values(image.info["XML:com.adobe.xmp"])
    assert values["cdp:tabletNotes"] == ["Barley & <wheat>"]


def test_property_names_come_from_labels() -> None:
    assert property_name("Sub-period") == "subPeriod"
    assert property_name("Script type") == "scriptType"
    assert property_name("City") == "city"
