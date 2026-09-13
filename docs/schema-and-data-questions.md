# Schema and data questions

This document tracks the questions about the database schema and the data that need a decision before the schema can change. The numbers are those of the review of the models. When you make a decision, record it with its date in the section of the question, and update the status table.

Unless a section says otherwise, the findings describe the data in `db_dumps/cdpp.sql` on 13 September 2026, after the changes that the sections record.

## Status

The rank orders the open questions by importance. Questions whose answers change the data, the links or the positions that pages show come first, and questions about the schema come after them. Rank 1 is the most important.

| Rank | Question | Status |
| --- | --- | --- |
| 1 | [Values that the 2014 import did not copy](#values-that-the-2014-import-did-not-copy) | Done; questions open |
| 2 | [9. Duplicate sign-list entries](#9-duplicate-sign-list-entries) | Partly done; 8 groups open |
| 3 | [Links to online sign lists](#links-to-online-sign-lists) | Partly done; questions open |
| 4 | [Links to catalogues](#links-to-catalogues) | Partly done; questions open |
| 5 | [10. Lookup tables for plain values](#10-lookup-tables-for-plain-values) | Partly done; questions open |
| 6 | [8. Two records of one fact](#8-two-records-of-one-fact) | Partly done; questions open |
| 7 | [Rulers, reigns and cities](#rulers-reigns-and-cities) | Done; questions open |
| 8 | [7. Values that contradict each other](#7-values-that-contradict-each-other) | Done; one question open |
| 9 | [11. Dates stored as text](#11-dates-stored-as-text) | Partly done; questions open |
| 10 | [6. Empty columns and tables](#6-empty-columns-and-tables) | Open |
| 11 | [12. Sign lists and sign names](#12-sign-lists-and-sign-names) | Done; one question open |

## Decisions made

13 September 2026:

- The SQLite dump in `db_dumps/cdpp.sql` is the source of record. The MySQL dump and its importer are removed.
- Every foreign key column has an index.
- A correspondent has exactly one of a ruler and a non-ruler.
- `Correspondent.name` is available in SQL queries.
- A read of an unloaded collection raises an error instead of querying the database.
- `tablet.timestamp` is removed. It held only the two times of the import in 2012.
- The sign-list numbers of CDP records are in the tables `sign_list` and `sign_list_entry`, and the description, ORACC and CDLI names are in the table `sign_name`. See [question 12](#12-sign-lists-and-sign-names).
- A snapshot of the Oracc Sign List gives links from sign pages. See [Links to online sign lists](#links-to-online-sign-lists).
- The sign-list numbers, variant names and form descriptions that the import of August 2014 did not copy are restored from a MySQL dump of May 2013. See [Values that the 2014 import did not copy](#values-that-the-2014-import-did-not-copy).
- Dynasty B.20 has the reigns of the four kings of Alalakh. The city Alalah is merged into Alalakh. Ruler names have no spaces at the ends. See [Rulers, reigns and cities](#rulers-reigns-and-cities).
- `surface` holds the surfaces of an object and the parts of a text. Default column, iteration and surface values are for display only: the database does not store them. See [question 10](#10-lookup-tables-for-plain-values).
- The sub-periods Sargonid, ED I, ED IIIa and ED IIIb, and the tablet `Wx17`, have their correct periods. The period ED is removed, because it is the same period as Early Dynastic. Two tablets have the locality of their city. See [question 7](#7-values-that-contradict-each-other).
- Tables of instances show defaults in italics. Pages show primes as `′`, and line and column numbers without zeros in front. See [question 10](#10-lookup-tables-for-plain-values).
- The JJT notes stay in the database, and tablet pages show them. A link hides or shows them. See [question 10](#10-lookup-tables-for-plain-values).
- An instance has one language at most, in the column `instance.language_id`. See [question 8](#8-two-records-of-one-fact).
- [Questions for the editors](questions-for-the-editors.md) lists the questions that need the tablets, the photographs or the sign lists.

14 September 2026:

- Search uses SQLite FTS5 tables, not Meilisearch.
- Editors can change the surface, column, line, iteration, function and language of a sign instance. Each save records a change set in the append-only tables `change_set` and `change`, with the editor's name from a cookie. Undo records a new change set. There is no sign-in.
- When editors use the site, the database is the source of record. The dump in `db_dumps/cdpp.sql` is a snapshot, and `cdpp backup` copies the database.
- A snapshot of CDLI catalogue entries gives links from tablet pages. The publications in the data do not change. See [Links to catalogues](#links-to-catalogues).

## 6. Empty columns and tables

### Findings

- These `tablet` columns are empty in all 228 rows: `city_site_id`, `to_id`, `language_id`, `dynasty_id`, `sub_locality_id`, `function_id` and `reign_id`.
- The tables `city_site`, `sub_locality` and `subperiod_dynasty` have no rows.
- The table `reign` has 591 rows. No tablet refers to a reign, and the application does not read the table.
- A ruler can have more than one reign. For example, Ashurbanipal has the Assyrian reign `A.0.113` and the Babylonian reign `B.6.32`. The notes that came with `csvs/ruler_name_matching.xlsx` say that the tablets of Esarhaddon and Ashurbanipal belong to the Assyrian reign. Only `tablet.reign_id` can record this.
- The `cdp` columns `form_name` and `notes` are empty in all 4,776 rows. They are also empty in the MySQL dumps of 2013 and 2014.
- The `cdp` column `variant_name` has 2 values, and `form_description` has 144. Before the restoration, both were empty.
- Every sign list has entries. Before the restoration, nine sign lists had none, because the import of 2014 did not copy them.
- The application does not read `period.from_date`, `period.to_date`, `text_vehicle.bm_catalogue`, `text_vehicle.cdli` or `reign.rim_ref`.

### Questions

- Will anyone enter data into these columns and tables?
- Is the reign data needed, for example to show the reign of the ruler of a tablet? Must a tablet refer to a reign, so that it can have the Assyrian reign of Esarhaddon or Ashurbanipal?

### Options

- Remove the empty columns and tables. The filters and the tablet details become shorter.
- Keep those that are for future data entry, and remove the others.

### Decision

Open.

## 7. Values that contradict each other

### Findings

- Before the correction, 39 tablets had a sub-period that belonged to a different period from the period of the tablet:
  - 38 Neo-Assyrian tablets from Nineveh had the sub-period Sargonid, whose period was Late Third Millennium. The 8 reigns in Sargonid, from Sargon II (`A.0.110`) to Assur-uballit (`A.0.117`), have the period Neo-Assyrian. The period of the sub-period was wrong.
  - `Wx17` had the period Late Babylonian and the sub-period Chaldean. Its year is 581 BC, and its ruler is Nebuchadnezzar II, whose reign `B.7.2` is Neo-Babylonian. The table `period` dates Late Babylonian from 540 BC. The period of the tablet was wrong.
- Before the correction, 42 reigns had the period Early Dynastic and one of the sub-periods ED I, ED IIIa and ED IIIb, whose period was ED. No tablet referred to ED or to Early Dynastic.
- Before the correction, `K_12032` (Nineveh) and `BM_91071` (Sippar) had a city with a locality, but no locality of their own. No tablet has a locality that is different from the locality of its city.
- Five tablets have a year with an eponym and a different eponym, or no eponym, of their own. Four have no eponym of their own, and the tablet page shows the eponym of the year. `83-1-18_287` has the eponym Labasi, but its year, 658 BC, has the eponym Sha-Nabu-shu.

### Questions

- For `83-1-18_287`, which is correct: the year 658 BC or the eponym Labasi?
- For new data: must the period of a tablet always be the period of its sub-period, and its locality the locality of its city?

### Options

- Derive: store the sub-period, and derive the period from it when a tablet has a sub-period. Do the same for the locality and the eponym.
- Validate: keep both values, and reject a change that makes them contradict each other.

### Decision

13 September 2026: migration d4e6b1a9c285 corrects the data. Its downgrade restores the former values.

- The sub-period Sargonid has the period Neo-Assyrian.
- The sub-periods ED I, ED IIIa and ED IIIb have the period Early Dynastic, and the period ED is removed.
- `Wx17` has the period Neo-Babylonian.
- `K_12032` and `BM_91071` have the locality of their city.

After the correction, no tablet or reign has a sub-period of a different period, and no tablet has a city with a locality but no locality of its own. The eponym of `83-1-18_287`, and the choice between the options, are open.

## 8. Two records of one fact

### Findings

- A tablet can record its recipient in `tablet.to_id` (0 rows) or in the association table `tablet_correspondent` (1 row).
- Before the change, the association table `instance_language` had 11,039 rows, and no instance had more than one language. 365 instances have no language. `tablet.language_id` is empty.
- The import of the instances in 2014 filled `instance_language` from the spreadsheet `csvs/corrected_instances_forimport.xlsx`. Its column `lang` has one value in each row: 8,368 `Akkadian`, 2,671 `Sumerian` and 365 empty.
- 265 of the 365 instances without a language are on Old Babylonian school tablets from Nippur, for example `CBS_11387` (62 instances), `CBS_7072` (46) and `CBS_7086` (42). MSL 14 publishes the tablets of 246 of them.
- All 800 instances on `BM_130738` have the import note `lang autoset to akk`. Their language was set for the whole tablet, not for each instance.

### Questions

- Can a tablet have more than one recipient?
- Do the instances without a language have no language, or is the value missing?

### Options

- Keep `tablet_correspondent`, and remove `tablet.to_id`.

### Decision

13 September 2026: an instance has one language at most. Migration f7a1c3e5b920 stores it in the column `instance.language_id` and removes `instance_language`. Its downgrade restores the table. The recipients and the instances without a language are open: see [Questions for the editors](questions-for-the-editors.md).

## 9. Duplicate sign-list entries

### Findings

- Before the restoration, 227 of the 4,776 `cdp` rows were copies of another row, in all columns except `id`, in 169 groups. The IDs of the records in a group are at most three apart.
- The import of 2014 did not copy nine sign lists. With their numbers, the records of 161 groups are all different. For example, records 14 and 15 have the Schroder VS 15 numbers 211 and 212.
- The records of 8 groups are still the same in all columns except `id`:

| Sign | Records |
| --- | --- |
| ADDU₂ | 1196, 1197 |
| ALIMₓ | 1277, 1278 |
| DUBAL₃ | 1782, 1783 |
| DUBAL₄ | 1784, 1785 |
| DUL | 1808, 1809, 1810 |
| DUN₃ | 1823, 1824 |
| GALAM | 2143, 2144 |
| GIDIM₄ | 2272, 2273 |

### Questions

- Do the records of the 8 groups record different forms of a sign? If they do, which values make them different? The spreadsheet of the 2014 import can have them. See [Values that the 2014 import did not copy](#values-that-the-2014-import-did-not-copy).

### Options

- Remove the 9 copies, and add a constraint that prevents new copies.
- Keep the copies, and add the information that makes them different.

### Decision

13 September 2026: the restored values make the records of 161 groups different, so these groups need no change. The 8 other groups are open.

## 10. Lookup tables for plain values

### Findings

- The tables `column` (22 rows, for example `ii'`), `line` (561 rows, for example `10'`) and `iteration` (15 rows, `1` to `15`) each hold one text value. To show the position of an instance, a page joins five tables.
- The table `function` holds sign functions: `syllable`, `logogram`, `determinative` and `gloss`. 11,072 of the 11,404 sign instances have a function. The other 332 have none in the import spreadsheet either. No tablet uses the table.
- The table `surface` has 12 values, including the abbreviations `obv`, `rev`, `a`, `be` and `aas`. The pages show the values as they are.
- `surface` holds parts of the text as well as surfaces of the object: `colophon` (107 instances in the import spreadsheet), `seal` (49) and `catchline` (4). Before the import, three instances on `BM_68332` changed from `rev` to `catchline`.
- `be` occurs only on `BM_113352`, which also has `obv` and `rev`. It is probably the bottom edge.
- `a` is the only surface of the instances on three fragments: `BM_40127` and `K_14895` (MSL 16 p. 49), and `W_18202_25` (AUWE 5, 129). It is possibly side A of a fragment whose obverse and reverse are not known.
- `aas` occurs once, on `K_39`. The data do not show its meaning.
- 7,719 instances have no column, 10,968 have no iteration and 2,736 have no surface.
- 81 instances have no line. 49 of them are on seal impressions, on 5 tablets. The other 32 are on `82_5-22_130` (1, no surface), `BM_113352` (7, `be`), `BM_38120` (1, no surface), `BM_38622` (1, `rev`), `BM_68332` (3, `catchline`), `K_12032` (1, `catchline`), `K_14895` (3, `a`), `K_197` (9, `rev`) and `K_39` (6: 4 `rev`, 1 `colophon`, 1 `aas`).
- Line and column values write the prime as an ASCII apostrophe, for example `10'`: 161 line values and 12 column values.
- Single-digit line numbers have a zero in front, for example `01` and `01'`, on 200 tablets. The import spreadsheet added 4,366 of these zeros. In the spreadsheet of the editor, only 1,000 values had a zero, all of the form `01'` to `09'`. No line number is `0` or `0'`.

### Notes that came with the instance spreadsheet

The notes of the editor of the instance data say:

- The spreadsheet has separate fields for the surface, the column, the line and the iteration. Not every instance has all of them.
- `obv`, `rev`, `seal`, `colophon`, `head`, `shaft` and similar values all belong in the surface.
- `i` can be the default column, and `1` the default iteration. `obv` is the usual default surface when it is not clear whether the preserved surface is the obverse or the reverse.
- Only seal impressions can have no line, because an incomplete impression does not always show the line of a sign.
- Brackets, spaces and underscores are removed from the positions. Only the prime remains, and it must be possible to show it and to enter it.
- Some surface values and line numbers could not be interpreted without the tablets.
- The sign number field of the instances is not necessary. The instance table has had no such field since 2013.
- The field `jjt note 2012` is for temporary working notes. It is `instance.jjt_notes`, with 834 values.

### Questions

- Do column, line and iteration values need records of their own, for example for sorting or for notes?
- Can a tablet have a function, as the column `tablet.function_id` suggests?
- What do the surface values `a`, `be` and `aas` mean?
- What are the lines of the 32 instances that are not on seal impressions?

### Options

- Store the column, the line and the iteration as text columns of `instance`, and remove the three tables.
- Use `function` for sign instances only, and give it a name that shows that it holds sign functions.

### Decision

13 September 2026:

- `surface` holds the surfaces of an object and the parts of a text, as the notes say.
- When the source gives no column, iteration or surface, the database stores no value.
- The table of instances on a tablet page shows the default `obv`, `i` or `1` in place of an empty surface, column or iteration. A default is in italics, and screen readers read "(default)" after it. A note above the table explains the italics. The table does not show a column whose values are all defaults.
- The position under a photograph, for example "Rev, column iii, line 6′", contains only recorded values.
- Pages show each apostrophe in a line or column number as a prime (`′`, U+2032), and remove the zeros in front of a number, for example `1′` for `01'`. The database keeps the values as they are, so data entry can use the apostrophe.
- The working notes in `instance.jjt_notes` stay in the database. The editors of the data are the users of the site, so the table of instances on a tablet page shows the notes in the column "JJT notes (2012)". A link above the table hides or shows the column. The address of the page without the column has `notes=hide`.

The other questions are open.

## 11. Dates stored as text

### Findings

- `year.year` holds values such as `1244 BC`. `period.from_date` and `period.to_date` hold values such as `1800 BC`. Text values do not sort or compare as dates.
- The periods Archaic, Late Third Millennium and Early Dynastic all have the dates `5000 BC` to `5000 BC`.
- Until the correction of [question 7](#7-values-that-contradict-each-other), there was also a period named `ED`, with the same dates. The reigns in its sub-periods had the period Early Dynastic.
- Tablets and reigns refer to 320 of the 2,600 rows in `year`.
- The ancient date columns of `tablet` hold values such as `1Bb`, which are not numbers.

### Questions

- Are the `5000 BC` dates placeholders for unknown dates?
- Are the 2,280 years that nothing refers to needed?

### Options

- Store years as integers in astronomical year numbering, for example -1243 for 1244 BC, and show them as text on the pages. Store unknown dates as null. Pages can then filter and sort tablets by date.
- Keep the ancient date columns as text.

### Decision

13 September 2026: `ED` and `Early Dynastic` are one period. See [question 7](#7-values-that-contradict-each-other). The other questions are open.

## 12. Sign lists and sign names

### Findings before the change

- `cdp` had one column for each of 22 sign lists. To add a sign list, a migration had to add a column, and the code had to change.
- Sign-list references are not always numbers, for example `556b` and `10+127`.
- The tables `description`, `oracc` and `cdli` had the same structure: an ID and a `sign_ref`.
- 1,891 names were in both `description` and `oracc`.
- In 2,359 `cdp` rows, the `description` name was the same as the sign name. In 1,000 rows, the `oracc` name was the same as the sign name.

### Decision

13 September 2026: normalise both.

- `sign_list` has one row for each of the 22 sign lists, with its name and its position in tables. `sign_list_entry` has one row for each number of a CDP record in a sign list. The number is text. The normalisation copied 16,989 numbers. With the restored numbers, the table has 25,061 rows.
- `sign_name` has one row for each name of a CDP record, with the source of the name: `description`, `oracc` or `cdli`. It has 10,549 rows. A record has one name from each source at most.
- Both migrations have a downgrade that restores the former columns and tables.

The migrations changed three things in the data:

- They removed the spaces at the ends of three KWU numbers.
- They did not copy the KWU value of record 3099 (sign MAŠMIN), which held only three spaces.
- They did not copy the CDLI name `NA`, which no record used. pandas reads the text `NA` as a missing value. Thus the import notebook sets the sign, description and ORACC names of records 3224 to 3227 to `NA` itself, and a comment in the notebook says to add `NA` to the sign, ORACC and CDLI tables. The unused CDLI name is probably that addition. The four records have the CDLI names `NA~a` to `NA~d`.

### Question still open

- What does the source `description` hold? Its values look like sign names, for example `ILIMMU`, not like descriptions. The column of the import spreadsheet had the heading `Description`. If the values are sign names, rename the source.

## Values that the 2014 import did not copy

### Findings

- The import notebook `utils/CDP_import.ipynb` read the CDP records from `csvs/cdp_signs_modified.csv` until 14 August 2014, and from `csvs/clean_CDP.xlsx` after that date. Neither file is in the repository.
- The column headings of the spreadsheet have spaces, for example `Schroder VS 15` and `form description`. The notebook read each column with the name of the model attribute, for example `Schroder_VS_15`. For a heading with spaces, it got no value and gave no error. The saved output of the notebook shows the headings.
- Thus the import did not copy the columns `variant_name` and `form_description`, or these nine sign lists: UET 2, ARM XV, Clay BE A 14, Koenig AfO Bei 16, Ranke BE A 61, Schroeder VS 12, Clay BE A 10, Schroder VS 15 and Fossey pp.
- The notebook did not read two columns of the spreadsheet that have no heading. Its output names them `Unnamed: 8` and `Unnamed: 31`.
- The MySQL dumps of 22 May 2013 (`db_dumps/latest_dump.sql` in commit 8f0d55e) and of 13 and 14 August 2014 (commit 2fb076f) have the values. In the dumps of 2014, Excel changed six values to dates: the sign names `1/4` and `1/6` became `01-Apr` and `01-Jun`, and four Fossey pp values became dates, for example `6-10` became `06-Oct`. The dump of 2013 does not have these changes.
- In the text columns of all the dumps, each character that is not ASCII is an underscore. For example, the form description `|LAGAB×U+A|` is `|LAGAB_U+A|`.
- Some restored numbers have underscores, for example `334_2` in UET 2. The numbers of HA, HZL and other lists that the import copied use the same form, so these underscores are probably in the source.
- The dump of 2013 has 4,779 CDP rows. In ID order, 4,776 rows have the same numbers in the 13 other sign lists as the CDP records in the database, in the same order. The other 3 rows have no record. Their sign name has characters that are not ASCII, and their numbers include MesZL 758, LAK 769 and ZATU N-58. Only LAK 193 is also the number of a record in the database (record 1891).

### Decision

13 September 2026: restore the values from the dump of 2013.

- `utils/restore_2013_values.py` aligns the rows of the dump with the CDP records and writes the values to `migrations/data/2013_sign_list_entries.csv` and `migrations/data/2013_record_details.csv`. Migration e7a2c94b1f05 adds the values to the database. Its downgrade removes them.
- The migration adds 8,072 sign-list entries:

| Sign list | Entries |
| --- | --- |
| UET 2 | 1,031 |
| ARM XV | 781 |
| Clay BE A 14 | 986 |
| Koenig AfO Bei 16 | 643 |
| Ranke BE A 61 | 837 |
| Schroeder VS 12 | 852 |
| Clay BE A 10 | 577 |
| Schroder VS 15 | 745 |
| Fossey pp | 1,620 |

- It adds both variant names, to records 4547 and 4548 (signs ZATU680~a1 and ZATU680~a2).
- It adds 144 of the 227 form descriptions. 72 have only ASCII characters. For the other 72, exactly one name in the tables `sign`, `sign_name` or `oracc_sign` has the same ASCII form, and the migration uses that name.
- It does not add 83 form descriptions. For 79, no name has the same ASCII form. For 4, more than one name has it, for example `|LU__KAD_|`, which can be `|LU₂×KAD₂|` or `|LU₂×KAD₃|`. `uv run utils/restore_2013_values.py` lists the 83 values. One value holds a note: `|EZEN~b_A_| -- need to sort out EZEN~a/b` (record 1561).
- The nine sign lists have no OSL abbreviation in `sign_list.oracc_list`, so their numbers have no links on sign pages.

### Questions

- Is `clean_CDP.xlsx` or `cdp_signs_modified.csv` still available? The spreadsheet can have the 83 form descriptions with all their characters, the values that make the 8 groups of [question 9](#9-duplicate-sign-list-entries) different, and the contents of the two columns without a heading.
- Did the clean-up of the spreadsheet in 2014 change numbers in the nine sign lists? It did not change the numbers of the other 13 lists. The dump of 2013 is older than the clean-up.
- Are the 3 rows of the dump without a record deleted on purpose?

## Rulers, reigns and cities

### Findings

- `csvs/ruler_name_matching.xlsx` compares the ruler names of the tablets with the list of rulers, and proposes replacements. The tablets use the proposed names. The database also resolves the names that the spreadsheet marks `WHICH ONE?`, for example Hammu-rapi (Babylon), Ibbi-Sin (Ur) and Nebuchadnezzar II.
- The spreadsheet gives `uruk` as the comment for Sin-gamil. The tablet `BM_91082` refers to Sin-gamil (Diniktum), `E.4.13.2`. Sin-gamil (Uruk), `E.4.4.3`, has no tablets.
- The spreadsheet has the tablet ruler `Esarhaddon or Assurbanipal`. In the database, 10 tablets from Nineveh refer to both Esarhaddon and Ashurbanipal, for example `K_696` and `K_788`.
- The notes that came with the spreadsheet ask for:
  - Dynasty B.20, in the period Middle Babylonian: the kings of Alalakh. .1 Idrimi, from 1470. .2 Addu-nirari. .3 Niqmepuh, 1450 to 1425. .4 Ilim-ilimma II, from 1420.
  - RIM references in the form `B.`, not `B`.
  - The city Amarna, in the new locality Egypt.
- The dynasty, the four rulers, Amarna and Egypt have been in the database since May 2013. The four reigns were not. All 587 RIM references had the form `B.` or another letter and a full stop.
- No tablet refers to Amarna or to Egypt.
- The city Alalah had 6 tablets, the 3 reigns `E.4.34.1` to `E.4.34.3`, and no locality. The city Alalakh, in Syria, had nothing that referred to it.
- Five ruler names had one space at the end: Abi-eshuh (3 tablets), Ashurnasirpal I, Assur-narari IV, Ilu-shumma and Tikulti-Ninurta II.

### Decision

13 September 2026:

- Migration a3d5f8e1c702 adds the reigns `B.20.1` to `B.20.4` of Idrimi, Addu-nirari, Niqmepuh and Ilim-ilimma II, with the dynasty B.20, the period Middle Babylonian, the city Alalakh and the dates of the notes. They have no sub-period.
- Migration c9b4e2a7d613 changes the city of the tablets and the reigns of Alalah to Alalakh, removes Alalah, and removes the spaces at the ends of the five ruler names.
- Both migrations have a downgrade.

### Questions

- Is the ruler of `BM_91082` Sin-gamil of Diniktum or Sin-gamil of Uruk?
- Which sub-period do the reigns of dynasty B.20 have? The sub-periods of Middle Babylonian are Kassite and Post-Kassite.
- Where is the data from Amarna?
- Must the 10 tablets that refer to Esarhaddon and Ashurbanipal refer to one of them? See also [question 6](#6-empty-columns-and-tables).

## Links to online sign lists

### Done

- `cdpp import-oracc-signs` loads a snapshot of the [Oracc Sign List](https://oracc.museum.upenn.edu/osl/) (OSL) from its source file `osl.asl`, which is in the public domain under CC0. The snapshot is in the tables `oracc_sign` and `oracc_list_number`. The snapshot of 13 September 2026 has 4,262 signs and forms, with 6,311 list numbers.
- `sign_list.oracc_list` holds the OSL abbreviation of 11 sign lists.
- On a sign page, a sign-list number links to the OSL page of the sign or form that has the same number in that list, if exactly one sign or form has it. OSL writes numbers with at least three digits, as in `MZL001`, so the lookup also tries the number with zeros in front.
- An ORACC name links to the OSL page of the sign or form with that name, if exactly one has it. It also links to the eBL page that OSL records for that sign or form. OSL records 2,504 eBL pages.
- A linked sign-list number also links to the eBL page that OSL records for its sign or form: 10,956 of the 11,350 linked numbers have one. 3,199 CDP records have at least one eBL link. 175 of them have eBL links only from their numbers.
- The snapshot holds the Unicode cuneiform of 3,344 OSL signs and forms. The pages show it in Noto Sans Cuneiform for 1,746 of the 3,440 signs, including 352 of the 413 signs with photographs, and for 2,965 of the 3,285 ORACC names. 348 of the 3,344 values contain characters that the font does not have: characters of the private use area, X for a part that Unicode does not have, or characters outside the cuneiform blocks of the font.
- In 795 records, a number leads to a different eBL page from the ORACC name of the record. The difference can be an error in the name or in a number, or OSL can give the number to a form of the sign.

| Sign list | OSL abbreviation | Entries | Entries with a link | Entries with several OSL matches |
| --- | --- | --- | --- | --- |
| MesZL | MZL | 2,219 | 1,933 | 38 |
| ELLes | ELLES | 1,013 | 1,000 | 2 |
| ZATU | ZATU | 1,408 | 17 | 0 |
| LAK | LAK | 1,480 | 1,426 | 5 |
| RSP | RSP | 1,203 | 1,113 | 9 |
| HZL | HZL | 1,228 | 988 | 101 |
| HA | SLLHA | 1,928 | 1,431 | 157 |
| aBZL | ABZL | 1,462 | 1,262 | 121 |
| REC | REC | 484 | 11 | 0 |
| Labat | SLLHA | 1,575 | 1,114 | 139 |
| KWU | KWU | 1,316 | 1,055 | 18 |

Of the 3,285 ORACC names, 3,135 link to OSL, and 3,024 of those also link to eBL.

### Not done

- **Several matches:** a number that more than one OSL sign or form has gets no link. For only 55 of the 590 entries with several matches are all the matches one OSL sign and its forms. The matches of the other 535 entries are different signs. A link to the sign of the forms would add 55 links at most, so it is not done.
- **Forms that OSL does not use:** numbers such as `172?`, `556_8`, `10+127` and `439, 465` have no link.
- **ZATU and REC:** OSL records only 17 ZATU numbers and 16 REC numbers. No other online source with a page for each entry was found. The CDLI list of proto-cuneiform signs on GitHub has an image for each sign name, under CC BY, but no page to link to. LAK and REC are available only as scans of the whole book on archive.org.
- **Emar and Hinke:** no online source was found.
- **eBL lookup by number:** eBL has a public API that finds a sign by list and number, for example `https://www.ebl.lmu.de/api/signs?listsName=MZL&listsNumber=839`. The site notice of eBL reserves all rights, so the application uses only the eBL links that OSL records.
- **CDLI archaic names:** no links. CDLI has no page for each sign.
- **Sign headings:** no link. Only 354 of the 3,440 sign names of the CDP are also OSL names.
- **Refresh:** the snapshot does not update itself. Run `cdpp import-oracc-signs`, then `cdpp dump-data`.

### Questions about sources

- **Which list is aBZL?** It was thought to be Borger's *Assyrisch-babylonische Zeichenliste* (ABZ, numbers 1 to 598). The data suggest Mittermayer's *Altbabylonische Zeichenliste*, which OSL calls ABZL (numbers 1 to 480, and 900 to 904). The highest aBZL number in the data is 480. Where our record has an ORACC or sign name, 94 % of the aBZL numbers that OSL has belong to a sign with the same name. OSL has no ABZ numbers. The spreadsheet `csvs/signs_from_instances.xls` has separate columns for `Borger ABZ` and `aBZL`, so the editors kept the two lists apart. The links use ABZL. Please check against the source of the data.
- **Are HA and Labat the SLLHA numbering?** Both columns link to SLLHA. OSL defines SLLHA from Deimel's *Šumerisches Lexikon*, Labat's *Manuel d'épigraphie akkadienne* and Ellermeier and Studt's *Handbuch Assur*. Of the numbers that OSL has, 89 % of HA numbers and 85 % of Labat numbers belong to a sign with the same name. This is near the rates of lists whose identity is certain: MesZL 78 %, LAK 85 %, HZL 92 %. In 1,227 of the 1,436 records with both numbers, the HA and the Labat numbers are the same. This decision is provisional. To change it, change `sign_list.oracc_list` for HA or Labat, then run `cdpp dump-data`.
- **Name agreement understates the match:** the rates above count a match only when the OSL name is the same as our name. Many differences are two names for one sign, for example `1` and `DIŠ`, or `|3(N57).PIRIG~b1|` and `|GIR₃×(LU.IGI)|`. A specialist check of a sample of the differences would give better rates.
- **Other sign lists:** `csvs/signs_from_instances.xls` also has columns for `Rosengarten` and `LKA`, which the CDP does not have. The columns are empty. The spreadsheet also maps the instance sign names of the first spreadsheets, such as `ca3`, to new names, such as `ŠA3`. The instances in the database use all the new names, with subscript digits.
- **Unverified sources:** the sign pages of the Hethitologie Portal Mainz (for HZL) and the Ebla Digital Archives (for ELLes) did not respond. They may have pages for entries.
- **LaBaSi:** LaBaSi has sign pages with MesZL numbers, but its addresses use internal IDs, and it states no licence for its data.
- **eBL:** would eBL agree to the use of its API, to link numbers that OSL does not have?
- **Uncertain titles:** the full titles of the HA, Emar and Hinke lists are not confirmed. OSL identifies KWU as Schneider, *Die Keilschriftzeichen der Wirtschaftsurkunden von Ur III*.

## Links to catalogues

### Done

- `cdpp import-cdli` loads a snapshot of the catalogue entries of the [Cuneiform Digital Library Initiative](https://cdli.earth) (CDLI) whose museum or accession number is the museum number of a tablet. The source is `cdli_cat.csv` in the [CDLI data repository](https://github.com/cdli-gh/data), last updated in August 2022. The table `cdli_artifact` keeps the P-number, the designation, the museum and accession numbers, the primary publication and the publication history of each entry.
- 220 of the 228 tablets match one entry each. The matches have 216 P-numbers: three seal impressions share an entry with their tablets, and N_5129 and N_6013 are parts of one join (P229543).
- A tablet page links to the CDLI page of its entry.
- The match compares keys made of the letters and the numbers of a museum number, without zeros in front of the numbers. `81_2-4_287` and `1881-02-04, 0287` have the same key. The collection names `OIM`, `Ashm` and `UM` in front of a CDLI number are optional, and so are letters in a registration number, as in `1891-05-09 Bu, 0003`.
- The publications in the data do not change.

| The key of the tablet is in | Tablets |
| --- | --- |
| The museum number of the object | 159 |
| The museum number of a join | 12 |
| The accession number, where the museum number is `BM —` | 48 |
| The accession number, where the museum number names a different object | 1 (K_15272) |

If a tablet has matches of more than one kind, only the matches of the kind higher in the table are kept. For example, K_39 matches `K 00039 + K 00153` (P365272) by accession number, and not USC 6594, whose accession number is `K039`.

### Findings

- For most matched tablets, the publication in the data and a CDLI publication give the same edition in different forms, for example `SAA 8, 70` and `Hunger, SAA 08, 070`, or `RIME.4.3.6.12` and `RIME 4.03.06.12Sumerian, ex. 06`.
- For 15 tablets, the data and CDLI give different numbers. See questions [9](questions-for-the-editors.md#9-which-ruler-is-on-these-tablets), [10](questions-for-the-editors.md#10-are-these-publication-numbers-correct) and [25](questions-for-the-editors.md#25-which-numbers-are-correct) for the editors.
- For other tablets, CDLI gives a different edition from the data, and no conflict: CT 12 and CT 19 for tablets that the data cite from MSL 16, CT 55 to CT 57 for Bongenaar (1997), and CCT 3 and CCT 4 for Larsen, OACT and MVAG 35,3.
- CDLI has no publication for five tablets that have one in the data: BM_131447 (Wiseman (1953) no. 3), BM_131477 (no. 70), BM_131506 (no. 128), K_14443 (MSL 16 p. 74) and K_14895 (MSL 16 p. 49).
- 43 tablets have no publication. CDLI gives a primary publication for 32 of them, and `unpublished unassigned ?` for 9. See [question 26](questions-for-the-editors.md#26-which-publication-does-each-of-these-tablets-have).
- The publications in the data have many forms, for example `RIME.4.3.6.12`, `SAA 8, 70`, `MSL 14 p. 19: Bo, 20: Co`, `Jeyes (1989) no. 11` and `King, BBS pp. 120-127, pls. XCVIII-CII`. Most RIMA numbers have no volume, as in `RIMA.0.76.1`, but VA_Ass_3221_c has `RIMA.1.0.60.1`.

These tablets have no CDLI entry:

| Tablet | Page | Publication |
| --- | --- | --- |
| BM_113352 | `/tablets/536` | unpublished |
| BM_40819 | `/tablets/630` | none |
| BM_59592 | `/tablets/499` | Bongenaar (1997) |
| BM_68332 | `/tablets/628` | none |
| UET_6/3_378 | `/tablets/608` | Alster (1997) p. 328 |
| UET_6/3_452 | `/tablets/607` | Alster (1997) p. 328 |
| W_18202_25 | `/tablets/662` | AUWE 5, 129 |
| Wx17 | `/tablets/535` | AUWE 5, 68 |

### Licence

The [CDLI terms of use](https://cdli.earth/terms-of-use) let users copy, aggregate and re-use the text of CDLI pages according to academic practice, with a citation of CDLI. The terms limit images to non-commercial use. The snapshot contains no images. The CDLI data repository has no licence file.

### Not done

- **Refresh:** the snapshot does not update itself. Run `cdpp import-cdli`, then `cdpp dump-data`. The default source is the file of August 2022. The CDLI site has later changes, but its API gives one entry at a time.

### Questions

- Must the data take the CDLI publications of the tablets that have no publication? See [question 26](questions-for-the-editors.md#26-which-publication-does-each-of-these-tablets-have).
- Must the publications in the data have one form? A form with a series, a volume, a text or page number and a siglum would let the tablet list filter by series.
