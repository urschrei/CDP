"""Full-text search of signs and tablets, using Meilisearch.

The database is the source of record. ``cdpp reindex`` builds each index from
the database in a staging index, then swaps the staging index with the live
index, so searches continue to work during a rebuild.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from flask import Flask, current_app
from meilisearch import Client
from meilisearch.errors import MeilisearchError
from meilisearch.models.task import TaskInfo
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from cdpp.db import db
from cdpp.models import Cdp, Sign, Tablet

SIGNS = "signs"
TABLETS = "tablets"
EXTENSION_KEY = "cdpp.search"
TASK_TIMEOUT_MS = 120_000

# Searchable attributes are in order of ranking weight.
SETTINGS: dict[str, dict[str, Any]] = {
    SIGNS: {"searchableAttributes": ["sign_ref", "references"]},
    TABLETS: {
        "searchableAttributes": [
            "museum_number",
            "rulers",
            "city",
            "locality",
            "period",
            "sub_period",
            "dynasty",
            "genre",
            "text_vehicle",
            "medium",
            "method",
            "publication",
            "notes",
        ]
    },
}


class SearchUnavailable(Exception):
    """Meilisearch cannot be reached, or it did not complete a request."""


@dataclass(frozen=True)
class SearchResults:
    """Record IDs in rank order, with the estimated number of all matches."""

    sign_ids: list[int]
    tablet_ids: list[int]
    estimated_signs: int
    estimated_tablets: int


class SearchIndex:
    def __init__(self, url: str, api_key: str | None, prefix: str) -> None:
        self.client = Client(url, api_key, timeout=10)
        self.prefix = prefix

    def search(self, query: str, limit: int = 50) -> SearchResults:
        queries = [
            {
                "indexUid": self._uid(name),
                "q": query,
                "limit": limit,
                "attributesToRetrieve": ["id"],
            }
            for name in (SIGNS, TABLETS)
        ]
        try:
            signs, tablets = self.client.multi_search(queries)["results"]
        except MeilisearchError as error:
            raise SearchUnavailable(str(error)) from error
        return SearchResults(
            sign_ids=[hit["id"] for hit in signs["hits"]],
            tablet_ids=[hit["id"] for hit in tablets["hits"]],
            estimated_signs=signs["estimatedTotalHits"],
            estimated_tablets=tablets["estimatedTotalHits"],
        )

    def replace_documents(
        self, name: str, documents: Sequence[Mapping[str, Any]]
    ) -> None:
        """Make ``documents`` the complete contents of the index ``name``."""
        live = self._uid(name)
        staging = f"{live}_staging"
        try:
            self._wait(self.client.delete_index(staging), ignore="index_not_found")
            self._wait(self.client.create_index(staging, {"primaryKey": "id"}))
            index = self.client.index(staging)
            self._wait(index.update_settings(SETTINGS[name]))
            self._wait(index.add_documents(documents, primary_key="id"))
            self._wait(
                self.client.create_index(live, {"primaryKey": "id"}),
                ignore="index_already_exists",
            )
            self._wait(self.client.swap_indexes([{"indexes": [live, staging]}]))
            self._wait(self.client.delete_index(staging))
        except MeilisearchError as error:
            raise SearchUnavailable(str(error)) from error

    def delete_indexes(self) -> None:
        try:
            for name in (SIGNS, TABLETS):
                for uid in (self._uid(name), f"{self._uid(name)}_staging"):
                    self._wait(self.client.delete_index(uid), ignore="index_not_found")
        except MeilisearchError as error:
            raise SearchUnavailable(str(error)) from error

    def _uid(self, name: str) -> str:
        return f"{self.prefix}{name}"

    def _wait(self, task: TaskInfo, ignore: str | None = None) -> None:
        """Wait for a task. Raise if it fails, unless its error code is ``ignore``."""
        result = self.client.wait_for_task(task.task_uid, timeout_in_ms=TASK_TIMEOUT_MS)
        if result.status == "succeeded":
            return
        error = result.error or {}
        if ignore is None or error.get("code") != ignore:
            message = error.get("message", "no message")
            raise SearchUnavailable(f"task {result.uid} {result.status}: {message}")


def init_app(app: Flask) -> None:
    app.extensions[EXTENSION_KEY] = SearchIndex(
        app.config["MEILISEARCH_URL"],
        app.config["MEILISEARCH_API_KEY"],
        app.config["MEILISEARCH_INDEX_PREFIX"],
    )


def search_index() -> SearchIndex:
    return current_app.extensions[EXTENSION_KEY]


def sign_documents() -> list[dict[str, Any]]:
    statement = (
        select(Sign)
        .order_by(Sign.id)
        .options(selectinload(Sign.cdp_records).selectinload(Cdp.names))
    )
    return [sign_document(sign) for sign in db.session.scalars(statement)]


def sign_document(sign: Sign) -> dict[str, Any]:
    """Describe a sign by its CDP name and its names in other sign lists."""
    names = {name.name for record in sign.cdp_records for name in record.names}
    names.discard(sign.sign_ref)
    return {"id": sign.id, "sign_ref": sign.sign_ref, "references": sorted(names)}


def tablet_documents() -> list[dict[str, Any]]:
    statement = select(Tablet).order_by(Tablet.id).options(selectinload(Tablet.rulers))
    return [tablet_document(tablet) for tablet in db.session.scalars(statement)]


def tablet_document(tablet: Tablet) -> dict[str, Any]:
    return {
        "id": tablet.id,
        "museum_number": tablet.museum_number,
        "rulers": [ruler.name for ruler in tablet.rulers],
        "city": tablet.city.name if tablet.city else None,
        "locality": tablet.locality.area if tablet.locality else None,
        "period": tablet.period.name,
        "sub_period": tablet.sub_period.name if tablet.sub_period else None,
        "dynasty": tablet.dynasty.name if tablet.dynasty else None,
        "genre": tablet.genre.name if tablet.genre else None,
        "text_vehicle": tablet.text_vehicle.name if tablet.text_vehicle else None,
        "medium": tablet.medium.name,
        "method": tablet.method.name if tablet.method else None,
        "publication": tablet.publication,
        "notes": tablet.notes,
    }
