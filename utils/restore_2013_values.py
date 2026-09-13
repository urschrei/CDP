"""Write the CDP record values that the import of August 2014 did not copy.

The import read the spreadsheet clean_CDP.xlsx. Its column headings have spaces,
but the import used the names of the model attributes, which have underscores.
Thus it did not copy nine sign lists, the variant names or the form descriptions.

The MySQL dump of 22 May 2013 in commit 8f0d55e has these values. The dumps of
August 2014 have the same values, but in them Excel changed six values to dates.
The dump replaced each character that is not ASCII with an underscore.

The script writes the values to CSV files in migrations/data, for the migration
that restores them. Run it from the project directory, with a database at
revision 6c1e9d2f7a38 or later in instance/cdpp.sqlite3:

    uv run utils/restore_2013_values.py
"""

import csv
import re
import sqlite3
import subprocess
from collections import defaultdict
from collections.abc import Iterator
from contextlib import closing
from difflib import SequenceMatcher
from pathlib import Path

DUMP = "8f0d55e:db_dumps/latest_dump.sql"
DATABASE = Path("instance/cdpp.sqlite3")
OUTPUT = Path("migrations/data")
ENTRIES_FILE = OUTPUT / "2013_sign_list_entries.csv"
DETAILS_FILE = OUTPUT / "2013_record_details.csv"

# The import copied these sign lists. Their numbers align the rows of the dump
# with the CDP records.
COPIED_LISTS = (
    "MesZL",
    "ELLes",
    "ZATU",
    "LAK",
    "Hinke",
    "RSP",
    "Emar",
    "HZL",
    "HA",
    "aBZL",
    "REC",
    "Labat",
    "KWU",
)
# The import did not copy these sign lists. The name of each sign list is the
# column name, with spaces in place of underscores.
LOST_LISTS = (
    "UET_2",
    "ARM_XV",
    "Clay_BE_A_14",
    "Koenig_AfO_Bei_16",
    "Ranke_BE_A_61",
    "Schroeder_VS_12",
    "Clay_BE_A_10",
    "Schroder_VS_15",
    "Fossey_pp",
)
EXCEL_DATE = re.compile(r"\d{2}-[A-Z][a-z]{2}|[A-Z][a-z]{2}-\d{2}")
ESCAPES = {"0": "\0", "n": "\n", "r": "\r", "t": "\t"}

type Row = dict[str, str | None]


def parse_values(dump: str, start: int) -> Iterator[list[str | None]]:
    """Yield the tuples of the INSERT statement whose values start at start."""
    row: list[str | None] = []
    field: list[str] = []
    in_row = in_string = quoted = False
    index = start
    while True:
        char = dump[index]
        if in_string:
            if char == "\\":
                index += 1
                field.append(ESCAPES.get(dump[index], dump[index]))
            elif char == "'" and dump[index + 1] == "'":
                index += 1
                field.append("'")
            elif char == "'":
                in_string = False
            else:
                field.append(char)
        elif char == "'":
            in_string = quoted = True
        elif not in_row:
            if char == "(":
                in_row, row = True, []
            elif char == ";":
                return
        elif char in ",)":
            value = "".join(field)
            if quoted:
                row.append(value)
            else:
                row.append(None if value.strip() == "NULL" else value.strip())
            field, quoted = [], False
            if char == ")":
                in_row = False
                yield row
        else:
            field.append(char)
        index += 1


def insert_rows(dump: str, table: str) -> list[Row]:
    """Return the rows that the INSERT statements of a MySQL dump add to table."""
    rows = []
    statement = re.compile(rf"INSERT INTO `{table}` \(([^)]*)\)\s*VALUES\s*")
    for match in statement.finditer(dump):
        columns = re.findall(r"`(\w+)`", match.group(1))
        rows.extend(
            dict(zip(columns, values, strict=True))
            for values in parse_values(dump, match.end())
        )
    return rows


def text(row: Row, column: str) -> str:
    return (row[column] or "").strip()


def current_records(connection: sqlite3.Connection) -> list[tuple[int, tuple]]:
    """Return the ID and the numbers in COPIED_LISTS of each CDP record."""
    numbers: dict[int, dict[str, str]] = defaultdict(dict)
    for cdp_id, name, number in connection.execute(
        "SELECT e.cdp_id, l.name, e.number FROM sign_list_entry e "
        "JOIN sign_list l ON l.id = e.sign_list_id"
    ):
        numbers[cdp_id][name] = number
    return [
        (cdp_id, tuple(numbers[cdp_id].get(name, "") for name in COPIED_LISTS))
        for (cdp_id,) in connection.execute("SELECT id FROM cdp ORDER BY id")
    ]


def align(rows: list[Row], records: list[tuple[int, tuple]]) -> list[tuple[Row, int]]:
    """Pair each CDP record ID with its row in the dump.

    The rows and the records must be in the same order. A row can have no
    record. If a record has no row, raise ValueError.
    """
    matcher = SequenceMatcher(
        None,
        [tuple(text(row, name) for name in COPIED_LISTS) for row in rows],
        [numbers for _, numbers in records],
        autojunk=False,
    )
    pairs = []
    for tag, row_start, row_end, record_start, record_end in matcher.get_opcodes():
        if tag == "equal":
            ids = [cdp_id for cdp_id, _ in records[record_start:record_end]]
            pairs.extend(zip(rows[row_start:row_end], ids, strict=True))
        elif tag != "delete":
            first, last = records[record_start][0], records[record_end - 1][0]
            raise ValueError(f"CDP records {first} to {last} have no row in {DUMP}")
    return pairs


def ascii_form(name: str) -> str:
    """Return name as the dump has it: an underscore for each non-ASCII character."""
    return "".join(char if char.isascii() else "_" for char in name)


def known_names(connection: sqlite3.Connection) -> dict[str, set[str]]:
    """Map the ASCII form of each sign name in the database to the names."""
    names: dict[str, set[str]] = defaultdict(set)
    for (name,) in connection.execute(
        "SELECT name FROM sign_name UNION SELECT sign_ref FROM sign "
        "UNION SELECT name FROM oracc_sign"
    ):
        names[ascii_form(name)].add(name)
    return names


def restore_name(value: str, names: dict[str, set[str]]) -> str | None:
    """Return value with its characters restored, or None if that is not certain."""
    if "_" not in value:
        return value
    matches = names.get(value, set())
    return next(iter(matches)) if len(matches) == 1 else None


def write_csv(path: Path, header: tuple[str, ...], rows: list[tuple]) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def main() -> None:
    dump = subprocess.run(["git", "show", DUMP], capture_output=True, check=True)
    rows = insert_rows(dump.stdout.decode(), "cdp")
    rows.sort(key=lambda row: int(text(row, "id")))
    with closing(sqlite3.connect(DATABASE)) as connection:
        pairs = align(rows, current_records(connection))
        names = known_names(connection)

    entries = []
    details = []
    unrestored = []
    for row, cdp_id in pairs:
        for column in LOST_LISTS:
            if number := text(row, column):
                entries.append((cdp_id, column.replace("_", " "), number))
        variant_name = text(row, "variant_name")
        form_description = text(row, "form_description")
        restored = restore_name(form_description, names) if form_description else ""
        if restored is None:
            unrestored.append((cdp_id, form_description))
        if variant_name or restored:
            details.append((cdp_id, variant_name, restored or ""))

    dates = [entry for entry in entries if EXCEL_DATE.fullmatch(entry[2])]
    if dates:
        raise ValueError(f"values that Excel changed to dates: {dates}")

    OUTPUT.mkdir(exist_ok=True)
    write_csv(ENTRIES_FILE, ("cdp_id", "sign_list", "number"), entries)
    write_csv(DETAILS_FILE, ("cdp_id", "variant_name", "form_description"), details)
    print(f"{len(rows) - len(pairs)} rows of the dump have no CDP record.")
    print(f"Wrote {len(entries)} sign-list entries to {ENTRIES_FILE}.")
    print(
        f"Wrote {len(details)} variant names and form descriptions to {DETAILS_FILE}."
    )
    print(f"{len(unrestored)} form descriptions have characters that are not known:")
    for cdp_id, form_description in unrestored:
        print(f"  {cdp_id}\t{form_description}")


if __name__ == "__main__":
    main()
