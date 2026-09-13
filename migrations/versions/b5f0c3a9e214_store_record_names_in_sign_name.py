"""Store the description, ORACC and CDLI names of CDP records in sign_name

Revision ID: b5f0c3a9e214
Revises: 8d2e61b4c0a7
Create Date: 2026-09-13 13:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b5f0c3a9e214"
down_revision = "8d2e61b4c0a7"
branch_labels = None
depends_on = None

# The former name tables. Each table name is also a value of sign_name.source.
SOURCES = ("description", "oracc", "cdli")


def upgrade():
    op.create_table(
        "sign_name",
        sa.Column("cdp_id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "source IN ('description', 'oracc', 'cdli')",
            name=op.f("ck_sign_name_source"),
        ),
        sa.ForeignKeyConstraint(
            ["cdp_id"],
            ["cdp.id"],
            name=op.f("fk_sign_name_cdp_id_cdp"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sign_name")),
        sa.UniqueConstraint("cdp_id", "source", name=op.f("uq_sign_name_cdp_id")),
    )
    with op.batch_alter_table("sign_name", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_sign_name_cdp_id"), ["cdp_id"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_sign_name_name"), ["name"], unique=False)

    for source in SOURCES:
        op.execute(
            "INSERT INTO sign_name (cdp_id, source, name) "
            f"SELECT cdp.id, '{source}', {source}.sign_ref FROM cdp "
            f"JOIN {source} ON {source}.id = cdp.{source}_id"
        )

    with op.batch_alter_table("cdp", schema=None) as batch_op:
        for source in SOURCES:
            batch_op.drop_index(batch_op.f(f"ix_cdp_{source}_id"))
            batch_op.drop_constraint(
                batch_op.f(f"fk_cdp_{source}_id_{source}"), type_="foreignkey"
            )
            batch_op.drop_column(f"{source}_id")

    # No record uses the CDLI name "NA", so the upgrade does not copy it.
    for source in SOURCES:
        op.drop_table(source)


def downgrade():
    for source in SOURCES:
        op.create_table(
            source,
            sa.Column("sign_ref", sa.String(length=150), nullable=False),
            sa.Column("id", sa.Integer(), nullable=False),
            sa.PrimaryKeyConstraint("id", name=op.f(f"pk_{source}")),
        )
        with op.batch_alter_table(source, schema=None) as batch_op:
            batch_op.create_index(
                batch_op.f(f"ix_{source}_sign_ref"), ["sign_ref"], unique=True
            )
        op.execute(
            f"INSERT INTO {source} (sign_ref) SELECT DISTINCT name FROM sign_name "
            f"WHERE source = '{source}' ORDER BY name"
        )

    with op.batch_alter_table("cdp", schema=None) as batch_op:
        for source in SOURCES:
            batch_op.add_column(sa.Column(f"{source}_id", sa.Integer(), nullable=True))
            batch_op.create_index(
                batch_op.f(f"ix_cdp_{source}_id"), [f"{source}_id"], unique=False
            )
            batch_op.create_foreign_key(
                batch_op.f(f"fk_cdp_{source}_id_{source}"),
                source,
                [f"{source}_id"],
                ["id"],
                onupdate="CASCADE",
                ondelete="CASCADE",
            )

    for source in SOURCES:
        op.execute(
            f"UPDATE cdp SET {source}_id = (SELECT {source}.id FROM {source} "
            f"JOIN sign_name ON sign_name.name = {source}.sign_ref "
            f"WHERE sign_name.cdp_id = cdp.id AND sign_name.source = '{source}')"
        )

    with op.batch_alter_table("sign_name", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_sign_name_name"))
        batch_op.drop_index(batch_op.f("ix_sign_name_cdp_id"))

    op.drop_table("sign_name")
