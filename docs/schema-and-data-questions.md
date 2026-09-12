# Schema and data questions

This document tracks the questions about the database schema and the data that need a decision before the schema can change. The numbers are those of the review of the models. When you make a decision, record it with its date in the section of the question, and update the status table.

The findings describe the data in `db_dumps/cdpp.sql` on 13 September 2026.

## Status

| Question | Status |
| --- | --- |
| [6. Empty columns and tables](#6-empty-columns-and-tables) | Open |
| [7. Values that contradict each other](#7-values-that-contradict-each-other) | Open |
| [8. Two records of one fact](#8-two-records-of-one-fact) | Open |
| [9. Duplicate sign-list entries](#9-duplicate-sign-list-entries) | Open |
| [10. Lookup tables for plain values](#10-lookup-tables-for-plain-values) | Open |
| [11. Dates stored as text](#11-dates-stored-as-text) | Open |
| [12. Sign lists and sign names](#12-sign-lists-and-sign-names) | Open |
| [Links to online sign lists](#links-to-online-sign-lists) | To explore |

## Decisions made

13 September 2026:

- The SQLite dump in `db_dumps/cdpp.sql` is the source of record. The MySQL dump and its importer are removed.
- Every foreign key column has an index.
- A correspondent has exactly one of a ruler and a non-ruler.
- `Correspondent.name` is available in SQL queries.
- A read of an unloaded collection raises an error instead of querying the database.
- `tablet.timestamp` is removed. It held only the two times of the import in 2012.

## 6. Empty columns and tables

### Findings

- These `tablet` columns are empty in all 228 rows: `city_site_id`, `to_id`, `language_id`, `dynasty_id`, `sub_locality_id`, `function_id` and `reign_id`.
- The tables `city_site`, `sub_locality` and `subperiod_dynasty` have no rows.
- The table `reign` has 587 rows. No tablet refers to a reign, and the application does not read the table.
- These `cdp` columns are empty in all 4,776 rows: `form_name`, `variant_name`, `form_description`, `notes`, and the sign-list columns `UET_2`, `ARM_XV`, `Clay_BE_A_14`, `Koenig_AfO_Bei_16`, `Ranke_BE_A_61`, `Schroeder_VS_12`, `Clay_BE_A_10`, `Schroder_VS_15` and `Fossey_pp`.
- The application does not read `period.from_date`, `period.to_date`, `text_vehicle.bm_catalogue`, `text_vehicle.cdli` or `reign.rim_ref`.

### Questions

- Will anyone enter data into these columns and tables?
- Is the reign data needed, for example to show the reign of the ruler of a tablet?

### Options

- Remove the empty columns and tables. The filters and the tablet details become shorter.
- Keep the columns and tables that are for future data entry, and remove the others.

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

- 227 of the 4,776 `cdp` rows are copies of another row, in all columns except `id`.
- Nothing in the data makes a copy different from its original.

### Questions

- Do the copies record different forms of a sign that the data do not yet show?

### Options

- Remove the copies, and add a unique constraint on the columns of an entry.
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

### Findings

- `cdp` has one column for each of 22 sign lists. To add a sign list, a migration must add a column, and the code must change.
- Sign-list references are not always numbers, for example `556b` and `10+127`.
- The tables `description`, `oracc` and `cdli` have the same structure: an ID and a `sign_ref`.
- 1,891 names are in both `description` and `oracc`.
- In 2,359 `cdp` rows, the `description` name is the same as the sign name. In 1,000 rows, the `oracc` name is the same as the sign name.

### Questions

- What does the table `description` hold? Its values look like sign names, for example `ILIMMU`, not like descriptions.
- Are the ORACC and CDLI names the names of the sign in those projects?

### Options

- Replace the sign-list columns with a table `sign_list`, with one row for each list, and a table `sign_list_entry`, with one row for each reference as text.
- Replace `description`, `oracc` and `cdli` with one table of names, with a column for the source of each name.

### Decision

Open.

## Links to online sign lists

Link each sign-list reference to its entry in the sign list, where the list is online and its entries have stable addresses.

### Questions

- Which of the 22 sign lists are online, and which of them have an address for each entry?
- Do the ORACC and CDLI names give addresses in those projects?

### Depends on

- [Question 12](#12-sign-lists-and-sign-names). A `sign_list` table can hold the address pattern of each list.
