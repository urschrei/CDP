"""ORM models for tablets, signs and sign instances.

Most table and column names are those of the original MySQL schema.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import (
    DDL,
    JSON,
    CheckConstraint,
    Column,
    ColumnElement,
    DateTime,
    ForeignKey,
    Index,
    String,
    Table,
    UniqueConstraint,
    event,
    func,
    select,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, MappedColumn, mapped_column, relationship

from cdpp.db import Base, db


def reference(
    target: str, *, name: str | None = None, **options: Any
) -> MappedColumn[Any]:
    """Return an indexed foreign key column that refers to ``target``.

    SQLite does not index foreign key columns. Without an index, a join on the
    column and a delete from the referenced table read the whole table.
    """
    foreign_key = ForeignKey(target, **options)
    if name is None:
        return mapped_column(foreign_key, index=True)
    return mapped_column(name, foreign_key, index=True)


class Entity(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)


# In each association table, the primary key indexes the first column, and a
# separate index covers the second column.

ruler_tablet = Table(
    "ruler_tablet",
    db.metadata,
    Column("ruler_id", ForeignKey("ruler.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "tablet_id",
        ForeignKey("tablet.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    ),
)

tablet_correspondent = Table(
    "tablet_correspondent",
    db.metadata,
    Column("tablet_id", ForeignKey("tablet.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "correspondent_id",
        ForeignKey("correspondent.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    ),
)

subperiod_dynasty = Table(
    "subperiod_dynasty",
    db.metadata,
    Column(
        "subperiod_id",
        ForeignKey("sub_period.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "dynasty_id",
        ForeignKey("dynasty.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    ),
)


# Tablet metadata


class Author(Entity):
    __tablename__ = "author"

    name: Mapped[str] = mapped_column(String(75), unique=True)


class Medium(Entity):
    __tablename__ = "medium"

    name: Mapped[str] = mapped_column(String(50), unique=True)


class Method(Entity):
    __tablename__ = "method"

    name: Mapped[str] = mapped_column(String(50), unique=True)


class Genre(Entity):
    __tablename__ = "genre"

    name: Mapped[str] = mapped_column(String(100), unique=True)


class Language(Entity):
    __tablename__ = "language"

    name: Mapped[str] = mapped_column(String(100), unique=True)


class Eponym(Entity):
    __tablename__ = "eponym"

    name: Mapped[str] = mapped_column(String(50), unique=True)


class Dynasty(Entity):
    __tablename__ = "dynasty"

    name: Mapped[str] = mapped_column(String(100), unique=True)


class Function(Entity):
    """The function of a tablet, or of a sign instance on a tablet."""

    __tablename__ = "function"

    name: Mapped[str] = mapped_column(String(50), unique=True)


class ScriptType(Entity):
    __tablename__ = "script_type"

    script: Mapped[str] = mapped_column(String(50), unique=True)


class TextVehicle(Entity):
    __tablename__ = "text_vehicle"

    name: Mapped[str] = mapped_column(String(100), unique=True)
    bm_catalogue: Mapped[str | None] = mapped_column(String(100))
    cdli: Mapped[str | None] = mapped_column(String(100))


class Locality(Entity):
    __tablename__ = "locality"

    area: Mapped[str] = mapped_column(String(100), unique=True)


class SubLocality(Entity):
    __tablename__ = "sub_locality"

    name: Mapped[str] = mapped_column(String(100), unique=True)
    locality_id: Mapped[int | None] = reference("locality.id")


class City(Entity):
    __tablename__ = "city"

    name: Mapped[str] = mapped_column(String(100), unique=True)
    locality_id: Mapped[int | None] = reference("locality.id")

    locality: Mapped[Locality | None] = relationship()


class CitySite(Entity):
    __tablename__ = "city_site"

    name: Mapped[str] = mapped_column(String(100), unique=True)
    city_id: Mapped[int] = reference("city.id")


class Year(Entity):
    __tablename__ = "year"

    year: Mapped[str] = mapped_column(String(14), unique=True)
    eponym_id: Mapped[int | None] = reference("eponym.id")

    eponym: Mapped[Eponym | None] = relationship()


class Period(Entity):
    __tablename__ = "period"

    name: Mapped[str] = mapped_column(String(150), unique=True)
    from_date: Mapped[str] = mapped_column(String(50))
    to_date: Mapped[str] = mapped_column(String(50))


class SubPeriod(Entity):
    __tablename__ = "sub_period"

    name: Mapped[str] = mapped_column(String(100), unique=True)
    period_id: Mapped[int] = reference("period.id")


class Ruler(Entity):
    __tablename__ = "ruler"

    name: Mapped[str] = mapped_column(String(100), unique=True)


class NonRulerCorrespondent(Entity):
    __tablename__ = "non_ruler_corresp"

    name: Mapped[str] = mapped_column(String(100), unique=True)


class Correspondent(Entity):
    """A ruler or a non-ruler who sent or received a tablet."""

    __tablename__ = "correspondent"
    __table_args__ = (
        CheckConstraint(
            "(ruler_id IS NULL) != (non_ruler_id IS NULL)", name="one_party"
        ),
    )

    ruler_id: Mapped[int | None] = reference("ruler.id")
    non_ruler_id: Mapped[int | None] = reference("non_ruler_corresp.id")

    ruler: Mapped[Ruler | None] = relationship()
    non_ruler: Mapped[NonRulerCorrespondent | None] = relationship()

    @hybrid_property
    def name(self) -> str | None:
        if self.ruler is not None:
            return self.ruler.name
        if self.non_ruler is not None:
            return self.non_ruler.name
        return None

    @name.inplace.expression
    @classmethod
    def _name_expression(cls) -> ColumnElement[str | None]:
        # Each subquery takes the correspondent row from the enclosing query. A
        # query that selects only the name must use select_from(Correspondent).
        return func.coalesce(
            select(Ruler.name)
            .where(Ruler.id == cls.ruler_id)
            .correlate_except(Ruler)
            .scalar_subquery(),
            select(NonRulerCorrespondent.name)
            .where(NonRulerCorrespondent.id == cls.non_ruler_id)
            .correlate_except(NonRulerCorrespondent)
            .scalar_subquery(),
        )


class Reign(Entity):
    __tablename__ = "reign"

    ruler_id: Mapped[int] = reference("ruler.id")
    rim_ref: Mapped[str] = mapped_column(String(50))
    city_id: Mapped[int | None] = reference("city.id")
    start_year_id: Mapped[int | None] = reference("year.id", name="start_date")
    end_year_id: Mapped[int | None] = reference("year.id", name="end_date")
    dynasty_id: Mapped[int | None] = reference("dynasty.id")
    period_id: Mapped[int] = reference("period.id")
    sub_period_id: Mapped[int | None] = reference("sub_period.id")


class Tablet(Entity):
    __tablename__ = "tablet"

    museum_number: Mapped[str] = mapped_column(String(75), unique=True)
    medium_id: Mapped[int] = reference("medium.id")
    script_type_id: Mapped[int | None] = reference("script_type.id")
    city_id: Mapped[int | None] = reference("city.id")
    city_site_id: Mapped[int | None] = reference("city_site.id")
    origin_city_id: Mapped[int | None] = reference("city.id")
    publication: Mapped[str | None] = mapped_column(String(200))
    period_id: Mapped[int] = reference("period.id")
    sub_period_id: Mapped[int | None] = reference("sub_period.id")
    from_id: Mapped[int | None] = reference("correspondent.id")
    to_id: Mapped[int | None] = reference("correspondent.id")
    language_id: Mapped[int | None] = reference("language.id")
    eponym_id: Mapped[int | None] = reference("eponym.id")
    year_id: Mapped[int | None] = reference("year.id")
    absolute_month: Mapped[str | None] = mapped_column(String(10))
    absolute_day: Mapped[str | None] = mapped_column(String(10))
    ancient_year: Mapped[str | None] = mapped_column(String(10))
    ancient_month: Mapped[str | None] = mapped_column(String(10))
    ancient_day: Mapped[str | None] = mapped_column(String(10))
    dynasty_id: Mapped[int | None] = reference("dynasty.id")
    text_vehicle_id: Mapped[int | None] = reference("text_vehicle.id")
    locality_id: Mapped[int | None] = reference("locality.id")
    sub_locality_id: Mapped[int | None] = reference("sub_locality.id")
    notes: Mapped[str | None] = mapped_column(String(500))
    method_id: Mapped[int | None] = reference("method.id")
    genre_id: Mapped[int | None] = reference("genre.id")
    function_id: Mapped[int | None] = reference("function.id")
    reign_id: Mapped[int | None] = reference("reign.id")
    author_id: Mapped[int | None] = reference("author.id")

    medium: Mapped[Medium] = relationship()
    script_type: Mapped[ScriptType | None] = relationship()
    city: Mapped[City | None] = relationship(foreign_keys=[city_id])
    city_site: Mapped[CitySite | None] = relationship()
    origin_city: Mapped[City | None] = relationship(foreign_keys=[origin_city_id])
    period: Mapped[Period] = relationship()
    sub_period: Mapped[SubPeriod | None] = relationship()
    sent_from: Mapped[Correspondent | None] = relationship(foreign_keys=[from_id])
    sent_to: Mapped[Correspondent | None] = relationship(foreign_keys=[to_id])
    recipients: Mapped[list[Correspondent]] = relationship(
        lazy="raise_on_sql",
        secondary=tablet_correspondent,
    )
    language: Mapped[Language | None] = relationship()
    eponym: Mapped[Eponym | None] = relationship()
    year: Mapped[Year | None] = relationship()
    dynasty: Mapped[Dynasty | None] = relationship()
    text_vehicle: Mapped[TextVehicle | None] = relationship()
    locality: Mapped[Locality | None] = relationship()
    sub_locality: Mapped[SubLocality | None] = relationship()
    method: Mapped[Method | None] = relationship()
    genre: Mapped[Genre | None] = relationship()
    function: Mapped[Function | None] = relationship()
    reign: Mapped[Reign | None] = relationship()
    author: Mapped[Author | None] = relationship()
    rulers: Mapped[list[Ruler]] = relationship(
        lazy="raise_on_sql",
        secondary=ruler_tablet,
        order_by=Ruler.name,
    )
    instances: Mapped[list[Instance]] = relationship(
        back_populates="tablet", lazy="raise_on_sql"
    )


# Signs and sign instances


class Sign(Entity):
    __tablename__ = "sign"

    sign_ref: Mapped[str] = mapped_column(String(150), unique=True, index=True)

    instances: Mapped[list[Instance]] = relationship(
        back_populates="sign", lazy="raise_on_sql"
    )
    cdp_records: Mapped[list[Cdp]] = relationship(
        lazy="raise_on_sql",
        back_populates="sign",
        cascade="all, delete-orphan",
        order_by="Cdp.id",
    )


# The values of SignName.source.
NAME_SOURCES = ("description", "oracc", "cdli")


class SignName(Entity):
    """The name of the sign of a CDP record in one of NAME_SOURCES.

    Each source was a separate table in the original schema.
    """

    __tablename__ = "sign_name"
    __table_args__ = (
        UniqueConstraint("cdp_id", "source"),
        CheckConstraint("source IN ('description', 'oracc', 'cdli')", name="source"),
    )

    cdp_id: Mapped[int] = reference("cdp.id", ondelete="CASCADE")
    source: Mapped[str] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(String(150), index=True)

    cdp: Mapped[Cdp] = relationship(back_populates="names")


class SignList(Entity):
    """A printed sign list, such as Borger's Mesopotamisches Zeichenlexikon."""

    __tablename__ = "sign_list"

    name: Mapped[str] = mapped_column(String(50), unique=True)
    # The order of the sign lists in tables.
    position: Mapped[int] = mapped_column(unique=True)
    # The abbreviation of the list in the Oracc Sign List, as in MZL, if the
    # Oracc Sign List records numbers of the list.
    oracc_list: Mapped[str | None] = mapped_column(String(20))


class Cdp(Entity):
    """A CDP sign form, with its names and numbers in other sign lists."""

    __tablename__ = "cdp"

    sign_id: Mapped[int] = reference("sign.id", onupdate="CASCADE", ondelete="CASCADE")
    form_name: Mapped[str | None] = mapped_column(String(5))
    variant_name: Mapped[str | None] = mapped_column(String(5))
    form_description: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(String(50))

    sign: Mapped[Sign] = relationship(back_populates="cdp_records")
    names: Mapped[list[SignName]] = relationship(
        lazy="raise_on_sql",
        back_populates="cdp",
        cascade="all, delete-orphan",
    )
    sign_list_entries: Mapped[list[SignListEntry]] = relationship(
        lazy="raise_on_sql",
        back_populates="cdp",
        cascade="all, delete-orphan",
        order_by="SignListEntry.sign_list_id",
    )

    def name_from(self, source: str) -> str | None:
        """Return the name of the sign in ``source``, or None."""
        return next((name.name for name in self.names if name.source == source), None)


class SignListEntry(Entity):
    """The number of a CDP record in a sign list."""

    __tablename__ = "sign_list_entry"
    __table_args__ = (UniqueConstraint("cdp_id", "sign_list_id"),)

    cdp_id: Mapped[int] = reference("cdp.id", ondelete="CASCADE")
    sign_list_id: Mapped[int] = reference("sign_list.id")
    # Text, because some numbers have suffixes, as in 556b.
    number: Mapped[str] = mapped_column(String(50))

    cdp: Mapped[Cdp] = relationship(back_populates="sign_list_entries")
    sign_list: Mapped[SignList] = relationship()


# A snapshot of the Oracc Sign List (OSL). See cdpp.oracc.


class OraccSign(Entity):
    """A sign or a sign form in the Oracc Sign List."""

    __tablename__ = "oracc_sign"

    oid: Mapped[str] = mapped_column(String(12), unique=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    ebl_url: Mapped[str | None] = mapped_column(String(500))

    list_numbers: Mapped[list[OraccListNumber]] = relationship(
        lazy="raise_on_sql",
        back_populates="oracc_sign",
        cascade="all, delete-orphan",
    )


class OraccListNumber(Entity):
    """The number of an Oracc Sign List sign or form in a printed sign list."""

    __tablename__ = "oracc_list_number"
    __table_args__ = (
        UniqueConstraint("oracc_sign_id", "list_name", "number"),
        Index("ix_oracc_list_number_list_name_number", "list_name", "number"),
    )

    oracc_sign_id: Mapped[int] = reference("oracc_sign.id", ondelete="CASCADE")
    list_name: Mapped[str] = mapped_column(String(20))
    number: Mapped[str] = mapped_column(String(50))

    oracc_sign: Mapped[OraccSign] = relationship(back_populates="list_numbers")


class Surface(Entity):
    __tablename__ = "surface"

    name: Mapped[str] = mapped_column(String(50), unique=True)


class TextColumn(Entity):
    """A column of text on a tablet surface."""

    __tablename__ = "column"

    number: Mapped[str] = mapped_column(String(5), unique=True)


class Line(Entity):
    __tablename__ = "line"

    number: Mapped[str] = mapped_column(String(5), unique=True)


class Iteration(Entity):
    __tablename__ = "iteration"

    number: Mapped[str] = mapped_column(String(5), unique=True)


class Instance(Entity):
    """One attestation of a sign on a tablet, with an image of it."""

    __tablename__ = "instance"

    tablet_id: Mapped[int] = reference(
        "tablet.id", onupdate="CASCADE", ondelete="CASCADE"
    )
    sign_id: Mapped[int] = reference("sign.id", onupdate="CASCADE", ondelete="CASCADE")
    surface_id: Mapped[int | None] = reference("surface.id")
    column_id: Mapped[int | None] = reference("column.id")
    line_id: Mapped[int | None] = reference("line.id")
    function_id: Mapped[int | None] = reference("function.id")
    iteration_id: Mapped[int | None] = reference("iteration.id")
    language_id: Mapped[int | None] = reference("language.id")
    notes: Mapped[str | None] = mapped_column(String(250))
    jjt_notes: Mapped[str | None] = mapped_column(String(250))
    filename: Mapped[str] = mapped_column(String(50), unique=True)

    tablet: Mapped[Tablet] = relationship(back_populates="instances")
    sign: Mapped[Sign] = relationship(back_populates="instances")
    surface: Mapped[Surface | None] = relationship()
    column: Mapped[TextColumn | None] = relationship()
    line: Mapped[Line | None] = relationship()
    function: Mapped[Function | None] = relationship()
    iteration: Mapped[Iteration | None] = relationship()
    language: Mapped[Language | None] = relationship()


# Edits


class ChangeSet(Entity):
    """The changes of one save: one editor, at one time, with an optional comment.

    Change sets are never changed or deleted. To undo a change set, a new
    change set sets the old values again and refers to it in ``reverts_id``.
    """

    __tablename__ = "change_set"

    author: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime)
    comment: Mapped[str | None] = mapped_column(String(500))
    reverts_id: Mapped[int | None] = reference("change_set.id")

    changes: Mapped[list[Change]] = relationship(
        back_populates="change_set", lazy="raise_on_sql", order_by="Change.id"
    )


class Change(Entity):
    """One value that a change set sets.

    ``kind`` is "update" for a changed field of a record, or "insert" for a
    field of a new lookup record, for example a new line number. The old and
    new values are JSON.
    """

    __tablename__ = "change"
    __table_args__ = (
        CheckConstraint("kind IN ('insert', 'update')", name="kind"),
        Index("ix_change_table_name_record_id", "table_name", "record_id"),
    )

    change_set_id: Mapped[int] = reference("change_set.id")
    kind: Mapped[str] = mapped_column(String(10))
    table_name: Mapped[str] = mapped_column(String(50))
    record_id: Mapped[int]
    field: Mapped[str] = mapped_column(String(50))
    old_value: Mapped[Any] = mapped_column(JSON)
    new_value: Mapped[Any] = mapped_column(JSON)

    change_set: Mapped[ChangeSet] = relationship(back_populates="changes")


def append_only(table_name: str) -> None:
    """Make a table refuse updates and deletes.

    The migration that creates the change tables creates the same triggers.
    """
    for action in ("UPDATE", "DELETE"):
        event.listen(
            db.metadata.tables[table_name],
            "after_create",
            DDL(
                f"CREATE TRIGGER {table_name}_no_{action.lower()} BEFORE {action} "
                f"ON {table_name} BEGIN SELECT RAISE(ABORT, "
                f"'{table_name} rows cannot be changed or deleted'); END"
            ).execute_if(dialect="sqlite"),
        )


append_only("change_set")
append_only("change")
