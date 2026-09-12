# Cuneiform Digital Palaeography Project (CDPP)

A web application for comparing the forms of cuneiform signs. It holds 11,404 photographs of individual signs on 228 tablets, and sign-list entries for 3,440 signs. It is a Flask application with an SQLite database, Meilisearch for full-text search, and a front end built with htmx, Tailwind CSS and esbuild.

## Running the site locally

This tutorial installs the application, loads the data, builds the search index and starts a development server.

### Prerequisites

- [uv](https://docs.astral.sh/uv/) 0.12 or later. uv installs Python 3.14 if it is not present.
- Node.js 22 or later, with npm.
- [Meilisearch](https://www.meilisearch.com/docs/learn/self_hosted/install_meilisearch_locally) 1.53 or later. On macOS: `brew install meilisearch`.

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

3. Create the database schema in `instance/cdpp.sqlite3`:

   ```sh
   uv run cdpp db upgrade
   ```

4. Import the records from the MySQL dump. The command prints the number of rows it imports into each table, and then the total:

   ```sh
   uv run cdpp import-dump
   ```

   ```text
   Imported 43668 rows from db_dumps/glyph_latest.sql.
   ```

5. In a second terminal, start Meilisearch. It keeps its data in `data.ms` in the current directory:

   ```sh
   meilisearch --env development --no-analytics
   ```

6. Build the search indexes:

   ```sh
   uv run cdpp reindex
   ```

   ```text
   Indexed 3440 signs.
   Indexed 228 tablets.
   ```

7. Start the development server:

   ```sh
   uv run cdpp run --debug --port 8000
   ```

8. Open <http://127.0.0.1:8000>.

To rebuild the assets when a template or a front-end file changes, run `npm run dev` in a third terminal.

## How-to guides

### Replacing the data

`cdpp import-dump` replaces every record with the contents of a MySQL dump, in one transaction. If a row refers to a record that does not exist, the command stops and changes nothing.

1. Import the dump:

   ```sh
   uv run cdpp import-dump PATH_TO_DUMP
   ```

2. Rebuild the search indexes. The indexes do not change when the database changes.

   ```sh
   uv run cdpp reindex
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

### Running the tests and checks

```sh
uv run pytest
uv run ruff check
uv run ruff format --check
uv run ty check src tests
npm run lint
```

One search test needs a running Meilisearch server. It is skipped unless you give the server address:

```sh
CDPP_TEST_MEILISEARCH_URL=http://127.0.0.1:7700 uv run pytest
```

The test creates indexes with a random prefix and deletes them when it finishes.

### Deploying with Docker Compose

`compose.yaml` runs the application with gunicorn on port 8000, and Meilisearch with a master key. The database is on the `data` volume. The images in `media/` and the dumps in `db_dumps/` are mounted read-only.

1. Set a master key for Meilisearch:

   ```sh
   export MEILI_MASTER_KEY="$(openssl rand -base64 32)"
   ```

2. Build the application image:

   ```sh
   docker compose build
   ```

3. Create the schema and import the data:

   ```sh
   docker compose run --rm app cdpp db upgrade
   docker compose run --rm app cdpp import-dump
   ```

4. Start the services:

   ```sh
   docker compose up -d
   ```

5. Build the search indexes:

   ```sh
   docker compose exec app cdpp reindex
   ```

## Reference

### Commands

Run each command as `uv run cdpp COMMAND`. `cdpp` is the Flask command-line interface, bound to this application, so the standard Flask commands are also available.

| Command | Action |
| --- | --- |
| `run` | Start the development server. |
| `db upgrade` | Apply the database migrations. |
| `db migrate -m MESSAGE` | Generate a migration from changes to the models. |
| `import-dump [DUMP]` | Replace all records with the contents of a MySQL dump. `DUMP` defaults to `db_dumps/glyph_latest.sql`. |
| `reindex` | Rebuild the Meilisearch indexes from the database. |
| `shell` | Start a Python shell with the application context. |

### Configuration

Set these environment variables to change the defaults.

| Variable | Default | Meaning |
| --- | --- | --- |
| `CDPP_SQLALCHEMY_DATABASE_URI` | `sqlite:///instance/cdpp.sqlite3`, in the project directory | Database URL. |
| `CDPP_MEILISEARCH_URL` | `http://127.0.0.1:7700` | Meilisearch server address. |
| `CDPP_MEILISEARCH_API_KEY` | None | Meilisearch key. `cdpp reindex` needs a key that can create and delete indexes. |
| `CDPP_MEILISEARCH_INDEX_PREFIX` | `cdpp_` | Prefix of the index names. The indexes are `PREFIXsigns` and `PREFIXtablets`. |
| `CDPP_MEDIA_ROOT` | `media`, in the project directory | Directory that contains the `instance` directory of sign photographs. |

### Pages

| Path | Content |
| --- | --- |
| `/` | Introduction, and a random selection of sign photographs. |
| `/signs` | All signs. Add `with_images=1` to show only signs with photographs. |
| `/signs/SIGN_ID` | A sign, its sign-list entries, and the tablets with photographs of it. |
| `/signs/SIGN_ID/images` | All photographs of a sign, grouped by tablet. |
| `/tablets` | All tablets, with filters. |
| `/tablets/TABLET_ID` | A tablet, its details, and the sign instances on it. |
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
| `src/cdpp/` | The application: models, views, filters, search, commands and the dump importer. |
| `src/cdpp/templates/` | Jinja templates. Files with names that start with `_` are fragments that htmx requests. |
| `frontend/` | Front-end sources. esbuild bundles them, with htmx, the fonts and the Tailwind build. |
| `migrations/` | Alembic migrations, managed by Flask-Migrate. |
| `tests/` | pytest tests. |
| `db_dumps/glyph_latest.sql` | The data, as a MySQL dump. |
| `media/instance/` | Sign photographs. |
| `utils/`, `csvs/` | Notebooks and spreadsheets from the original preparation of the data. They are not used by the application. |

## About the architecture

The SQLite database is the source of record. The table and column names are the same as in the original MySQL schema, so the historical dump imports without a mapping step. SQLite compares text byte by byte, as the binary collation of the MySQL database did, so sign names such as `S` and `Š` stay distinct.

Meilisearch holds a copy of the sign names and the tablet details for full-text search. `cdpp reindex` builds each index in a staging index, then swaps it with the live index, so search continues to work during a rebuild. If Meilisearch is not available, the search page tells the user, and the other pages continue to work.

The server renders every page. htmx updates parts of pages without a full reload: the tablet list when a filter changes, the search results while the user types, and the random selection of signs on the home page. A request from htmx names its target element in the `HX-Target` header, and the server then returns only the fragment for that element. Links and forms also work without JavaScript. Only the button that shows other signs on the home page needs it.

Sign names are set in Gentium Book Plus, and the interface in Atkinson Hyperlegible Next. The font subsets do not contain subscript digits, so the browser takes those characters from another font.

## Citation

This project has a DOI: [10.5281/zenodo.11647](https://doi.org/10.5281/zenodo.11647)

Cite as:
Stephan Hügel (2014). Cuneiform Digital Palaeography Project (CDPP) v0.2. Zenodo. 10.5281/zenodo.11647

## Licence

The code is available under the MIT licence. The licence of the data is not settled. See [LICENCE.md](LICENCE.md).
