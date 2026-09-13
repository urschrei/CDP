# Schema and data questions

This document tracks the questions about the database schema and the data that need a decision before the schema can change. The numbers are those of the review of the models. When you make a decision, record it with its date in the section of the question, and update the status table.

Unless a section says otherwise, the findings describe the data in `db_dumps/cdpp.sql` on 13 September 2026.

## Status

| Question | Status |
| --- | --- |
| [6. Empty columns and tables](#6-empty-columns-and-tables) | Open |
| [7. Values that contradict each other](#7-values-that-contradict-each-other) | Open |
| [8. Two records of one fact](#8-two-records-of-one-fact) | Open |
| [9. Duplicate sign-list entries](#9-duplicate-sign-list-entries) | Open |
| [10. Lookup tables for plain values](#10-lookup-tables-for-plain-values) | Open |
| [11. Dates stored as text](#11-dates-stored-as-text) | Open |
| [12. Sign lists and sign names](#12-sign-lists-and-sign-names) | Done; one question open |
| [Links to online sign lists](#links-to-online-sign-lists) | Partly done; questions open |

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

## 6. Empty columns and tables

### Findings

- These `tablet` columns are empty in all 228 rows: `city_site_id`, `to_id`, `language_id`, `dynasty_id`, `sub_locality_id`, `function_id` and `reign_id`.
- The tables `city_site`, `sub_locality` and `subperiod_dynasty` have no rows.
- The table `reign` has 587 rows. No tablet refers to a reign, and the application does not read the table.
- These `cdp` columns are empty in all 4,776 rows: `form_name`, `variant_name`, `form_description` and `notes`.
- These sign lists have no entries: UET 2, ARM XV, Clay BE A 14, Koenig AfO Bei 16, Ranke BE A 61, Schroeder VS 12, Clay BE A 10, Schroder VS 15 and Fossey pp. Each was an empty column of `cdp` before the normalisation of question 12.
- The application does not read `period.from_date`, `period.to_date`, `text_vehicle.bm_catalogue`, `text_vehicle.cdli` or `reign.rim_ref`.

### Questions

- Will anyone enter data into these columns, tables and sign lists?
- Is the reign data needed, for example to show the reign of the ruler of a tablet?

### Options

- Remove the empty columns, tables and sign lists. The filters and the tablet details become shorter.
- Keep those that are for future data entry, and remove the others.

### Decision

Open.

## 7. Values that contradict each other

### Findings

- The sub-period of 39 tablets belongs to a different period from the period of the tablet.
- One tablet has an eponym that is different from the eponym of its year.
- Two tablets have a city with a locality, but no locality of their own.

### Questions

- For the 39 tablets, which value is correct: the period or the sub-period?
- Is the locality of a tablet always the locality of its city?
- Is the eponym of a tablet always the eponym of its year?

### Options

- Derive: store the sub-period, and derive the period from it when a tablet has a sub-period. Do the same for the locality and the eponym.
- Validate: keep both values, and reject a change that makes them contradict each other.

### Decision

Open.

## 8. Two records of one fact

### Findings

- A tablet can record its recipient in `tablet.to_id` (0 rows) or in the association table `tablet_correspondent` (1 row).
- The association table `instance_language` has 11,039 rows. No instance has more than one language, and 365 instances have no language. `tablet.language_id` is empty.

### Questions

- Can a tablet have more than one recipient?
- Can a sign instance have more than one language?

### Options

- Keep `tablet_correspondent`, and remove `tablet.to_id`.
- If an instance has one language at most, replace `instance_language` with a nullable column `instance.language_id`.

### Decision

Open.

## 9. Duplicate sign-list entries

### Findings

- 227 of the 4,776 `cdp` rows are copies of another row, in all columns except `id`. The copies have the same names and the same sign-list numbers as their originals.
- Nothing in the data makes a copy different from its original.

### Questions

- Do the copies record different forms of a sign that the data do not yet show?

### Options

- Remove the copies, and add a constraint that prevents new copies.
- Keep the copies, and add the information that makes them different.

### Decision

Open.

## 10. Lookup tables for plain values

### Findings

- The tables `column` (22 rows, for example `ii'`), `line` (561 rows, for example `10'`) and `iteration` (15 rows, `1` to `15`) each hold one text value. To show the position of an instance, a page joins five tables.
- The table `function` holds sign functions: `syllable`, `logogram`, `determinative` and `gloss`. Sign instances use the table. No tablet uses it.
- The table `surface` has 12 values, including the abbreviations `obv`, `rev`, `a`, `be` and `aas`. The pages show the values as they are.

### Questions

- Do column, line and iteration values need records of their own, for example for sorting or for notes?
- Can a tablet have a function, as the column `tablet.function_id` suggests?
- What do the surface values `a`, `be` and `aas` mean?

### Options

- Store the column, the line and the iteration as text columns of `instance`, and remove the three tables.
- Use `function` for sign instances only, and give it a name that shows that it holds sign functions.

### Decision

Open.

## 11. Dates stored as text

### Findings

- `year.year` holds values such as `1244 BC`. `period.from_date` and `period.to_date` hold values such as `1800 BC`. Text values do not sort or compare as dates.
- The periods Archaic, ED, Late Third Millennium and Early Dynastic all have the dates `5000 BC` to `5000 BC`.
- There is a period named `ED` and a period named `Early Dynastic`.
- Tablets and reigns refer to 320 of the 2,600 rows in `year`.
- The ancient date columns of `tablet` hold values such as `1Bb`, which are not numbers.

### Questions

- Are the `5000 BC` dates placeholders for unknown dates?
- Are `ED` and `Early Dynastic` the same period?
- Are the 2,280 years that nothing refers to needed?

### Options

- Store years as integers in astronomical year numbering, for example -1243 for 1244 BC, and show them as text on the pages. Store unknown dates as null. Pages can then filter and sort tablets by date.
- Keep the ancient date columns as text.

### Decision

Open.

## 12. Sign lists and sign names

### Findings before the change

- `cdp` had one column for each of 22 sign lists. To add a sign list, a migration had to add a column, and the code had to change.
- Sign-list references are not always numbers, for example `556b` and `10+127`.
- The tables `description`, `oracc` and `cdli` had the same structure: an ID and a `sign_ref`.
- 1,891 names were in both `description` and `oracc`.
- In 2,359 `cdp` rows, the `description` name was the same as the sign name. In 1,000 rows, the `oracc` name was the same as the sign name.

### Decision

13 September 2026: normalise both.

- `sign_list` has one row for each of the 22 sign lists, with its name and its position in tables. `sign_list_entry` has one row for each number of a CDP record in a sign list: 16,989 rows. The number is text.
- `sign_name` has one row for each name of a CDP record, with the source of the name: `description`, `oracc` or `cdli`. It has 10,549 rows. A record has one name from each source at most.
- Both migrations have a downgrade that restores the former columns and tables.

The migrations changed three things in the data:

- They removed the spaces at the ends of three KWU numbers.
- They did not copy the KWU value of record 3099 (sign MAŠMIN), which held only three spaces.
- They did not copy the CDLI name `NA`, which no record used. It is probably a marker for a missing value from the spreadsheets of the original import.

### Question still open

- What does the source `description` hold? Its values look like sign names, for example `ILIMMU`, not like descriptions. If they are sign names, rename the source.

## Links to online sign lists

### Done

- `cdpp import-oracc-signs` loads a snapshot of the [Oracc Sign List](https://oracc.museum.upenn.edu/osl/) (OSL) from its source file `osl.asl`, which is in the public domain under CC0. The snapshot is in the tables `oracc_sign` and `oracc_list_number`. The snapshot of 13 September 2026 has 4,262 signs and forms, with 6,311 list numbers.
- `sign_list.oracc_list` holds the OSL abbreviation of 11 sign lists.
- On a sign page, a sign-list number links to the OSL page of the sign or form that has the same number in that list, if exactly one sign or form has it. OSL writes numbers with at least three digits, as in `MZL001`, so the lookup also tries the number with zeros in front.
- An ORACC name links to the OSL page of the sign or form with that name, if exactly one has it. It also links to the eBL page that OSL records for that sign or form. OSL records 2,504 eBL pages.

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

- **Several matches:** a number that more than one OSL sign or form has gets no link. Often this is a sign and one of its forms. The snapshot could record the sign of each form, and the page could then link to the sign.
- **Forms that OSL does not use:** numbers such as `172?`, `556_8`, `10+127` and `439, 465` have no link.
- **ZATU and REC:** OSL records only 17 ZATU numbers and 16 REC numbers. No other online source with a page for each entry was found. The CDLI list of proto-cuneiform signs on GitHub has an image for each sign name, under CC BY, but no page to link to. LAK and REC are available only as scans of the whole book on archive.org.
- **Emar and Hinke:** no online source was found.
- **eBL lookup by number:** eBL has a public API that finds a sign by list and number, for example `https://www.ebl.lmu.de/api/signs?listsName=MZL&listsNumber=839`. The site notice of eBL reserves all rights, so the application uses only the eBL links that OSL records.
- **CDLI archaic names:** no links. CDLI has no page for each sign.
- **Sign headings:** no link. Only 354 of the 3,440 sign names of the CDP are also OSL names.
- **Refresh:** the snapshot does not update itself. Run `cdpp import-oracc-signs`, then `cdpp dump-data`.

### Questions about sources

- **Which list is aBZL?** It was thought to be Borger's *Assyrisch-babylonische Zeichenliste* (ABZ, numbers 1 to 598). The data suggest Mittermayer's *Altbabylonische Zeichenliste*, which OSL calls ABZL (numbers 1 to 480, and 900 to 904). The highest aBZL number in the data is 480. Where our record has an ORACC or sign name, 94 % of the aBZL numbers that OSL has belong to a sign with the same name. OSL has no ABZ numbers. The links use ABZL. Please check against the source of the data.
- **Are HA and Labat the SLLHA numbering?** Both columns link to SLLHA. OSL defines SLLHA from Deimel's *Šumerisches Lexikon*, Labat's *Manuel d'épigraphie akkadienne* and Ellermeier and Studt's *Handbuch Assur*. Of the numbers that OSL has, 89 % of HA numbers and 85 % of Labat numbers belong to a sign with the same name. This is near the rates of lists whose identity is certain: MesZL 78 %, LAK 85 %, HZL 92 %. In 1,227 of the 1,436 records with both numbers, the HA and the Labat numbers are the same. This decision is provisional. To change it, change `sign_list.oracc_list` for HA or Labat, then run `cdpp dump-data`.
- **Name agreement understates the match:** the rates above count a match only when the OSL name is the same as our name. Many differences are two names for one sign, for example `1` and `DIŠ`, or `|3(N57).PIRIG~b1|` and `|GIR₃×(LU.IGI)|`. A specialist check of a sample of the differences would give better rates.
- **Unverified sources:** the sign pages of the Hethitologie Portal Mainz (for HZL) and the Ebla Digital Archives (for ELLes) did not respond. They may have pages for entries.
- **LaBaSi:** LaBaSi has sign pages with MesZL numbers, but its addresses use internal IDs, and it states no licence for its data.
- **eBL:** would eBL agree to the use of its API, to link numbers that OSL does not have?
- **Uncertain titles:** the full titles of the HA, Emar and Hinke lists are not confirmed. OSL identifies KWU as Schneider, *Die Keilschriftzeichen der Wirtschaftsurkunden von Ur III*.
