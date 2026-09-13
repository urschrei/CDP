"""Correct the periods of four sub-periods and one tablet, remove the period ED,
and give two tablets the locality of their city

Revision ID: d4e6b1a9c285
Revises: c9b4e2a7d613
Create Date: 2026-09-13 20:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d4e6b1a9c285"
down_revision = "c9b4e2a7d613"
branch_labels = None
depends_on = None

# Each sub-period, with its former period and its correct period. The reigns in
# each sub-period have the correct period.
SUB_PERIODS = (
    ("Sargonid", "Late Third Millennium", "Neo-Assyrian"),
    ("ED I", "ED", "Early Dynastic"),
    ("ED IIIa", "ED", "Early Dynastic"),
    ("ED IIIb", "ED", "Early Dynastic"),
)
# The tablet, with its former period and its correct period. Its year, 581 BC,
# and its ruler, Nebuchadnezzar II, are Neo-Babylonian.
TABLET_PERIODS = (("Wx17", "Late Babylonian", "Neo-Babylonian"),)
# These tablets have a city with a locality, but no locality of their own. No
# tablet has a locality that is different from the locality of its city.
TABLETS_WITHOUT_LOCALITY = ("BM_91071", "K_12032")
# The period ED before its removal.
ED = {"name": "ED", "from_date": "5000 BC", "to_date": "5000 BC"}

period = sa.table(
    "period",
    sa.column("id"),
    sa.column("name"),
    sa.column("from_date"),
    sa.column("to_date"),
)
sub_period = sa.table("sub_period", sa.column("name"), sa.column("period_id"))
tablet = sa.table(
    "tablet",
    sa.column("museum_number"),
    sa.column("period_id"),
    sa.column("city_id"),
    sa.column("locality_id"),
)
city = sa.table("city", sa.column("id"), sa.column("locality_id"))


def period_id(name):
    return sa.select(period.c.id).where(period.c.name == name).scalar_subquery()


def change_periods(direction):
    """Give each sub-period and tablet its correct period (1) or its former one (-1)."""
    for name, *periods in SUB_PERIODS:
        old, new = periods[::direction]
        op.execute(
            sub_period.update()
            .where(sub_period.c.name == name, sub_period.c.period_id == period_id(old))
            .values(period_id=period_id(new))
        )
    for museum_number, *periods in TABLET_PERIODS:
        old, new = periods[::direction]
        op.execute(
            tablet.update()
            .where(
                tablet.c.museum_number == museum_number,
                tablet.c.period_id == period_id(old),
            )
            .values(period_id=period_id(new))
        )


def upgrade():
    change_periods(1)
    # The foreign key check after the migrations fails if a row still refers to
    # the period ED.
    op.execute(period.delete().where(period.c.name == ED["name"]))

    city_locality = (
        sa.select(city.c.locality_id)
        .where(city.c.id == tablet.c.city_id)
        .scalar_subquery()
    )
    op.execute(
        tablet.update()
        .where(
            tablet.c.museum_number.in_(TABLETS_WITHOUT_LOCALITY),
            tablet.c.locality_id.is_(None),
        )
        .values(locality_id=city_locality)
    )


def downgrade():
    bind = op.get_bind()
    early_dynastic = bind.execute(sa.select(period_id("Early Dynastic"))).scalar()
    if early_dynastic is not None:
        op.execute(period.insert().values(**ED))
    change_periods(-1)

    op.execute(
        tablet.update()
        .where(tablet.c.museum_number.in_(TABLETS_WITHOUT_LOCALITY))
        .values(locality_id=None)
    )
