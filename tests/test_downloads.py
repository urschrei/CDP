import io
from pathlib import Path

from flask import Flask
from flask.testing import FlaskClient
from PIL import Image
from sqlalchemy import select

from cdpp.db import db
from cdpp.downloads import download_name
from cdpp.editing import fingerprint, save
from cdpp.models import Instance, Sign, Tablet
from tests.conftest import Sample


def instance_id(filename: str) -> int:
    found = db.session.scalar(select(Instance.id).where(Instance.filename == filename))
    assert found is not None
    return found


def write_photograph(app: Flask, filename: str) -> bytes:
    image = Image.new("P", (3, 2))
    image.putpalette([value for index in range(256) for value in (index, 9, 9)])
    image.putdata([0, 1, 2, 3, 4, 5])
    buffer = io.BytesIO()
    image.save(buffer, "PNG")
    data = buffer.getvalue()
    (Path(app.config["MEDIA_ROOT"]) / "instance" / f"{filename}.png").write_bytes(data)
    return data


def pixels(data: bytes) -> bytes:
    with Image.open(io.BytesIO(data)) as image:
        return image.tobytes()


def xmp(data: bytes) -> str:
    with Image.open(io.BytesIO(data)) as image:
        return image.info["XML:com.adobe.xmp"]


def test_download_contains_the_current_record(
    app: Flask, client: FlaskClient, sample: Sample
) -> None:
    original = write_photograph(app, "I_1")
    identifier = instance_id("I_1")
    url = f"/instances/{identifier}/photograph.png"
    unversioned = xmp(client.get(url).data)
    assert "<cdp:applicationCommit>" not in unversioned
    assert "<cdp:databaseRevision>" not in unversioned
    app.config["COMMIT"] = "f82b7447f17d249e1e7bc75065e8855094b37337"
    # The test database has no migrations. Give it the table of a migrated one.
    connection = db.session.connection()
    connection.exec_driver_sql("CREATE TABLE alembic_version (version_num TEXT)")
    connection.exec_driver_sql("INSERT INTO alembic_version VALUES ('f6c2a8e4d913')")
    db.session.commit()

    response = client.get(url)

    assert response.status_code == 200
    assert response.content_type == "image/png"
    disposition = response.headers["Content-Disposition"]
    assert disposition.startswith("attachment;")
    assert f"filename*=UTF-8''A.1_A%C5%A0_{identifier}.png" in disposition
    cache_control = response.headers["Cache-Control"]
    assert "no-cache" in cache_control
    assert "public" not in cache_control
    assert "max-age=0" in cache_control
    assert pixels(response.data) == pixels(original)
    page = f"http://localhost/instances/{identifier}"
    assert f"<dc:identifier>{page}</dc:identifier>" in xmp(response.data)
    assert "<cdp:line>1</cdp:line>" in xmp(response.data)
    commit = "<cdp:applicationCommit>f82b7447f17d249e1e7bc75065e8855094b37337<"
    assert commit in xmp(response.data)
    revision = "<cdp:databaseRevision>f6c2a8e4d913</cdp:databaseRevision>"
    assert revision in xmp(response.data)
    etag = response.headers["ETag"]
    assert client.get(url, headers={"If-None-Match": etag}).status_code == 304

    instance = db.session.get_one(Instance, identifier)
    save(instance, {"line": "2"}, author="Editor", seen=fingerprint(instance, ["line"]))
    changed = client.get(url)

    assert changed.headers["ETag"] != etag
    assert "<cdp:line>2</cdp:line>" in xmp(changed.data)
    assert "<cdp:lastChangeSet>" in xmp(changed.data)


def test_download_needs_an_instance_with_a_photograph(
    client: FlaskClient, sample: Sample
) -> None:
    assert (
        client.get(f"/instances/{instance_id('I_2')}/photograph.png").status_code == 404
    )
    assert client.get("/instances/999/photograph.png").status_code == 404


def test_instance_page_links_to_the_download_of_its_photograph(
    app: Flask, client: FlaskClient, sample: Sample
) -> None:
    write_photograph(app, "I_1")
    with_file, without_file = instance_id("I_1"), instance_id("I_2")

    html = client.get(f"/instances/{with_file}").get_data(as_text=True)
    other = client.get(f"/instances/{without_file}").get_data(as_text=True)

    assert f'href="/instances/{with_file}/photograph.png"' in html
    assert 'hx-boost="false"' in html
    assert "photograph.png" not in other


def test_download_names_omit_characters_that_file_systems_refuse() -> None:
    instance = Instance(
        id=7,
        tablet=Tablet(museum_number="UET_6/3_378"),
        sign=Sign(sign_ref="|NINDA₂×GUD|"),
    )

    assert download_name(instance) == "UET_6-3_378_NINDA₂×GUD_7.png"


def test_export_writes_the_photographs_with_their_records(
    app: Flask, sample: Sample, tmp_path: Path
) -> None:
    original = write_photograph(app, "I_1")
    target = tmp_path / "export"

    result = app.test_cli_runner().invoke(
        args=["export-photographs", str(target), "--site-url", "https://cdpp.example"]
    )

    assert result.exit_code == 0, result.output
    assert result.output.splitlines() == [
        f"Wrote 1 photograph to {target}.",
        "Instances without a photograph file: 1.",
    ]
    assert [path.name for path in target.iterdir()] == ["I_1.png"]
    data = (target / "I_1.png").read_bytes()
    assert pixels(data) == pixels(original)
    page = f"https://cdpp.example/instances/{instance_id('I_1')}"
    assert f"<dc:identifier>{page}</dc:identifier>" in xmp(data)


def test_export_refuses_the_directory_of_the_photographs(
    app: Flask, sample: Sample
) -> None:
    original = write_photograph(app, "I_1")
    photographs = Path(app.config["MEDIA_ROOT"]) / "instance"

    result = app.test_cli_runner().invoke(args=["export-photographs", str(photographs)])

    assert result.exit_code != 0
    assert "DIRECTORY is the directory of the photographs" in result.output
    assert (photographs / "I_1.png").read_bytes() == original
