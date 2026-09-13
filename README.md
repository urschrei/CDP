# Cuneiform Digital Palaeography Project (CDPP)

A web application for comparing the forms of cuneiform signs. It holds 11,404 photographs of individual signs on 228 tablets, and sign-list entries for 3,440 signs. It is a Flask application with an SQLite database, full-text search with SQLite FTS5, and a front end built with htmx, Tailwind CSS and esbuild.

## Running the site locally

This tutorial installs the application, creates the database from the data dump and starts a development server.

### Prerequisites

- [uv](https://docs.astral.sh/uv/) 0.12 or later. uv installs Python 3.14 if it is not present.
- Node.js 22 or later, with npm.

### Steps

1. Install the Python dependencies:

   ```sh
   uv sync
   ```

2. Install the front-end dependencies and build the assets into `src/cdpp/static/dist`:

   ```sh
   npm ci
   npm run build
   ```

3. Create the database `instance/cdpp.sqlite3` from the dump in `db_dumps/cdpp.sql`. The command also applies the migrations that are newer than the dump, and makes the search tables:

   ```sh
   uv run cdpp load-data
   ```

   ```text
   Loaded db_dumps/cdpp.sql.
   Indexed 3440 signs and 228 tablets.
   ```

4. Start the development server:

   ```sh
   uv run cdpp run --debug --port 8000
   ```

5. Open <http://127.0.0.1:8000>.

To rebuild the assets when a template or a front-end file changes, run `npm run dev` in a second terminal.

## How-to guides

### Saving changes to the data

The dump in `db_dumps/cdpp.sql` is the source of record. When you change records in the database, write the database back to the dump and commit the dump.

```sh
uv run cdpp dump-data
```

### Rebuilding the search tables

The search tables do not change when you change records with SQL, a migration or `cdpp import-oracc-signs`. Make them again:

```sh
uv run cdpp reindex
```

### Restoring the database from the dump

> [!WARNING]
> `--replace` deletes every table in the database. Changes that are not in the dump are lost.

```sh
uv run cdpp load-data --replace
```

### Updating the Oracc Sign List snapshot

The links from sign pages to the Oracc Sign List use a snapshot of the list in the database.

1. Import the current `osl.asl` from the OSL repository:

   ```sh
   uv run cdpp import-oracc-signs
   ```

2. Write the database to the dump:

   ```sh
   uv run cdpp dump-data
   ```

### Changing the schema

1. Change the models in `src/cdpp/models.py`.
2. Generate a migration, and read it before you continue:

   ```sh
   uv run cdpp db migrate -m "DESCRIPTION_OF_CHANGE"
   ```

3. Apply the migration:

   ```sh
   uv run cdpp db upgrade
   ```

4. If the migration changes records, rebuild the search tables:

   ```sh
   uv run cdpp reindex
   ```

5. Write the migrated database to the dump:

   ```sh
   uv run cdpp dump-data
   ```

### Running the tests and checks

```sh
uv run pytest
uv run ruff check
uv run ruff format --check
uv run ty check src tests
npm run lint
```

### Deploying with Docker Compose

`compose.yaml` runs the application with gunicorn on port 8000. The database, with its search tables, is on the `data` volume. The images in `media/` and the dump in `db_dumps/` are mounted read-only.

1. Build the application image:

   ```sh
   docker compose build
   ```

2. Create the database from the dump:

   ```sh
   docker compose run --rm app cdpp load-data
   ```

3. Start the application:

   ```sh
   docker compose up -d
   ```

## Reference

### Commands

Run each command as `uv run cdpp COMMAND`. `cdpp` is the Flask command-line interface, bound to this application, so the standard Flask commands are also available.

| Command | Action |
| --- | --- |
| `run` | Start the development server. |
| `load-data [--replace] [PATH]` | Create the database from an SQL dump, apply newer migrations, and make the search tables. `PATH` defaults to `db_dumps/cdpp.sql`. `--replace` deletes the existing tables first. |
| `dump-data [PATH]` | Write the schema, the records and the migration revision to an SQL dump. The dump does not contain the search tables. `PATH` defaults to `db_dumps/cdpp.sql`. |
| `import-oracc-signs [SOURCE]` | Replace the snapshot of the Oracc Sign List with the signs in `osl.asl`. `SOURCE` is a path or a URL, and defaults to the file in the [OSL repository](https://github.com/oracc/osl). |
| `db upgrade` | Apply the database migrations. |
| `db migrate -m MESSAGE` | Generate a migration from changes to the models. |
| `reindex` | Make the search tables again from the database. |
| `shell` | Start a Python shell with the application context. |

### Configuration

Set these environment variables to change the defaults.

| Variable | Default | Meaning |
| --- | --- | --- |
| `CDPP_SQLALCHEMY_DATABASE_URI` | `sqlite:///instance/cdpp.sqlite3`, in the project directory | Database URL. The application works only with SQLite. |
| `CDPP_MEDIA_ROOT` | `media`, in the project directory | Directory that contains the `instance` directory of sign photographs. |

### Pages

| Path | Content |
| --- | --- |
| `/` | Introduction, and a random selection of sign photographs. |
| `/signs` | All signs. Add `with_images=1` to show only signs with photographs. |
| `/signs/SIGN_ID` | A sign, its sign-list entries, and the tablets with photographs of it. |
| `/signs/SIGN_ID/images` | All photographs of a sign, grouped by tablet. |
| `/tablets` | All tablets, with filters. |
| `/tablets/TABLET_ID` | A tablet, its details, and the sign instances on it. Add `notes=hide` to hide the JJT notes. |
| `/tablets/TABLET_ID/images` | All photographs from a tablet, grouped by sign. |
| `/search?q=QUERY` | Signs and tablets that match the query. |
| `/media/instance/FILENAME` | A sign photograph. |

The paginated pages take a `page` parameter.

### Tablet filters

Each filter selects the tablets with a related record of the given name, for example `/tablets?period=Old%20Babylonian&medium=clay`.

`city`, `dynasty`, `eponym`, `function`, `genre`, `language`, `locality`, `medium`, `method`, `period`, `ruler`, `script_type`, `sent_from`, `sent_to`, `sub_period`, `text_vehicle`, `year`

### Project layout

| Path | Content |
| --- | --- |
| `src/cdpp/` | The application: models, views, filters, search and commands. |
| `src/cdpp/templates/` | Jinja templates. Files with names that start with `_` are fragments that htmx requests. |
| `frontend/` | Front-end sources. esbuild bundles them, with htmx, the fonts and the Tailwind build. |
| `migrations/` | Alembic migrations, managed by Flask-Migrate. |
| `migrations/data/` | CSV files that data migrations read. |
| `tests/` | pytest tests. |
| `docs/schema-and-data-questions.md` | Open questions about the schema and the data. |
| `docs/questions-for-the-editors.md` | Questions for the editors of the data, with the tablets, signs and photographs that each question is about. |
| `db_dumps/cdpp.sql` | The data: an SQLite dump of the schema, the records and the migration revision. |
| `media/instance/` | Sign photographs. |
| `utils/`, `csvs/` | Notebooks and spreadsheets from the original preparation of the data. They are not used by the application. |
| `utils/restore_2013_values.py` | Writes the CSV files of the migration that restores the values that the import of 2014 did not copy. |

## About the architecture

The SQL dump in `db_dumps/cdpp.sql` is the source of record. It is plain text, so version control shows each change to the records and the schema. `cdpp load-data` builds the SQLite database from the dump, and applies the migrations that are newer than the dump. The data come from a MySQL dump of the original site, and the table and column names are still those of the MySQL schema. SQLite compares text byte by byte, as the binary collation of the MySQL database did, so sign names such as `S` and `Š` stay distinct.

Search uses two SQLite FTS5 tables with the trigram tokenizer: `search_sign` holds the name of each sign and its names in other sign lists, and `search_tablet` holds the details of each tablet. The tables hold the text in a normalised form, Unicode NFKC and then case folding, so `gir3` finds GIR₃, and `S` and `Š` stay distinct. A search finds the records with a field that contains the query. An exact value ranks first, then a value that starts with the query, then a value that contains it. The trigram index cannot find a query shorter than three characters, so a shorter query reads all the rows. The search tables are derived from the other tables, so they are not in the models, the migrations or the dump. `cdpp load-data` and `cdpp reindex` make them, and a search makes them if they do not exist.

On a sign page, a sign-list number links to the [Oracc Sign List](https://oracc.museum.upenn.edu/osl/) (OSL) if exactly one OSL sign or form has the same number in that list. An ORACC name links to OSL if exactly one OSL sign or form has that name, and to the electronic Babylonian Library (eBL) if OSL records an eBL page for it. The links come from a snapshot of OSL in the tables `oracc_sign` and `oracc_list_number`, so a page does not depend on Oracc. [docs/schema-and-data-questions.md](docs/schema-and-data-questions.md) lists the sign lists that have links, and the open questions about them.

The server renders every page. htmx updates parts of pages without a full reload: the tablet list when a filter changes, the search results while the user types, the table of signs on a tablet page when the JJT notes are hidden or shown, and the random selection of signs on the home page. A request from htmx names its target element in the `HX-Target` header, and the server then returns only the fragment for that element. Links and forms also work without JavaScript. Only the button that shows other signs on the home page needs it.

Sign names are set in Gentium Book Plus, and the interface in Atkinson Hyperlegible Next. The font subsets do not contain subscript digits, so the browser takes those characters from another font.

## Citation

This project has a DOI: [10.5281/zenodo.11647](https://doi.org/10.5281/zenodo.11647)

Cite as:
Stephan Hügel (2014). Cuneiform Digital Palaeography Project (CDPP) v0.2. Zenodo. 10.5281/zenodo.11647

## Licence

The code is available under the MIT licence. The licence of the data is not settled. See [LICENCE.md](LICENCE.md). The snapshot of the Oracc Sign List in the dump is in the public domain, under the CC0 licence of `osl.asl`.
