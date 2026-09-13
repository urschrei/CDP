import os
import uuid
from collections.abc import Iterator

import pytest

from cdpp.search import (
    SIGNS,
    TABLETS,
    SearchIndex,
    SearchUnavailable,
    sign_documents,
    tablet_documents,
)
from tests.conftest import Sample


@pytest.fixture
def live_index() -> Iterator[SearchIndex]:
    url = os.environ.get("CDPP_TEST_MEILISEARCH_URL")
    if not url:
        pytest.skip("set CDPP_TEST_MEILISEARCH_URL to test against Meilisearch")
    api_key = os.environ.get("CDPP_TEST_MEILISEARCH_API_KEY")
    index = SearchIndex(url, api_key, prefix=f"test_{uuid.uuid4().hex}_")
    yield index
    index.delete_indexes()


def test_sign_documents_include_names_from_other_sign_lists(sample: Sample) -> None:
    documents = sign_documents()

    assert {
        "id": sample.sign.id,
        "sign_ref": "AŠ",
        "references": ["horizontal wedge"],
    } in documents
    assert {
        "id": sample.sign_without_records.id,
        "sign_ref": "ZA",
        "references": [],
    } in documents


def test_tablet_documents_name_the_related_records(sample: Sample) -> None:
    documents = {doc["id"]: doc for doc in tablet_documents()}

    document = documents[sample.tablet.id]
    assert document["museum_number"] == "A.1"
    assert document["rulers"] == ["Zimri-Lim"]
    assert document["city"] == "Mari"
    assert document["locality"] == "Syria"
    assert document["period"] == "Old Babylonian"
    assert document["sub_period"] is None
    assert documents[sample.tablet_without_instances.id]["rulers"] == []


def test_search_reports_an_unreachable_server() -> None:
    index = SearchIndex("http://127.0.0.1:9", None, prefix="test_")
    with pytest.raises(SearchUnavailable):
        index.search("AŠ")


def test_replace_documents_then_search(sample: Sample, live_index: SearchIndex) -> None:
    # The second pass swaps the staging index with an existing live index.
    for _ in range(2):
        live_index.replace_documents(SIGNS, sign_documents())
        live_index.replace_documents(TABLETS, tablet_documents())

    by_ruler = live_index.search("zimri")
    assert by_ruler.tablet_ids == [sample.tablet.id]
    assert by_ruler.sign_ids == []
    assert live_index.search("horizontal wedge").sign_ids == [sample.sign.id]
