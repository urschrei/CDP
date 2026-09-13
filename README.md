# Cuneiform Digital Palaeography Project (CDPP)

A web application for comparing the forms of cuneiform signs. It contains 11,404 photographs of individual signs on 228 tablets, and sign-list entries for 3,440 signs. Editors can change the position and reading of each sign instance, that is, each occurrence of a sign on a tablet, and the application records each change. It is a Flask application with an SQLite database, full-text search with SQLite FTS5, and a front end built with htmx, Tailwind CSS and esbuild.

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

### Editing a sign instance

A sign instance is one occurrence of a sign on a tablet, with its own photograph. An edit changes only that instance: the sign, and its instances on this and other tablets, do not change.

1. Open the tablet. In the table **Signs on this tablet**, each row is one instance.
2. In the row of the instance, select **Edit**. The form shows the photograph of the instance.
3. Change the surface, column, line, iteration, function or language. Leave a field empty if the source gives no value.
4. Enter your name. The site keeps it for your next edit. Optionally, enter a comment, for example the reason for the change.
5. Select **Save**.

If someone saved a change to the instance after you opened the form, the form shows the saved values instead. Make your change again, then save.

### Undoing a change

1. Select **Changes** in the navigation, or **History of this instance** in the edit form.
2. Select the change set.
3. Enter your name, and select **Undo change set**.

Undo records a new change set. If a later change set changed the same values, undo them in order, newest first.

### Backing up the database

When editors use the site, the database is the only copy of their changes until the next backup or dump. Back it up on a schedule, and keep the copies on another computer.

```sh
uv run cdpp backup "backups/cdpp-$(date +%Y-%m-%d).sqlite3"
```

The command can run while the site runs. With Docker Compose, write the copy to the `data` volume, then copy it off the server:

```sh
docker compose exec app cdpp backup "/data/cdpp-$(date +%Y-%m-%d).sqlite3"
```

### Writing a snapshot of the data to the dump

The dump contains the schema, the records and the change sets. Write it to record a state of the data in version control, for example for a release:

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

If the database has change sets that are not in the dump, the command stops. Back up the database first. To replace it and lose those change sets, add `--discard-changes`.

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

### Updating the catalogue snapshots

The links from tablet pages to CDLI and to Oracc editions use snapshots in the database.

1. Import the CDLI catalogue and the Oracc catalogues:

   ```sh
   uv run cdpp import-cdli
   uv run cdpp import-oracc-texts
   ```

2. Write the comparison with CDLI into the questions for the editors:

   ```sh
   uv run cdpp check-cdli
   ```

3. Write the database to the dump:

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

`compose.yaml` runs the application with gunicorn on port 8000. The database, with its search tables, is on the `data` volume. The image contains the photographs and the dump. At the first start, `deploy/start.sh` creates the database from the dump. At each later start, it applies newer migrations.

> [!IMPORTANT]
> If `CDPP_PASSWORD` is not set, anyone who can reach the site can edit. Set it, or run the site only on a private network.

1. Build the application image:

   ```sh
   docker compose build
   ```

2. Start the application:

   ```sh
   docker compose up -d
   ```

### Deploying to Fly.io

`fly.toml` runs the application on one machine in London, with the database on the volume `cdpp_data`. The machine suspends when it has no requests, and starts again at the next request. The file server of the machine sends the photographs from the image, so a request for a photograph does not need the password. Fly takes a snapshot of the volume each day, and keeps each snapshot for 60 days.

1. Create the application:

   ```sh
   fly apps create cdpp --org personal
   ```

2. Set the password:

   ```sh
   fly secrets set --stage -a cdpp CDPP_PASSWORD=PASSWORD
   ```

3. Deploy:

   ```sh
   fly deploy --ha=false
   ```

   The first deployment creates the volume, and `deploy/start.sh` creates the database from `db_dumps/cdpp.sql`. Each later deployment applies newer migrations to the database on the volume, and does not load the dump.

To change the password, run `fly secrets set -a cdpp CDPP_PASSWORD=PASSWORD`. The machine restarts with the new password.

## Reference

### Commands

Run each command as `uv run cdpp COMMAND`. `cdpp` is the Flask command-line interface, bound to this application, so the standard Flask commands are also available.

| Command | Action |
| --- | --- |
| `run` | Start the development server. |
| `load-data [--replace [--discard-changes]] [PATH]` | Create the database from an SQL dump, apply newer migrations, and make the search tables. `PATH` defaults to `db_dumps/cdpp.sql`. `--replace` deletes the existing tables first. It stops if the database has change sets that are not in the dump, unless you add `--discard-changes`. |
| `dump-data [PATH]` | Write the schema, the records, the change sets and the migration revision to an SQL dump. The dump does not contain the search tables. `PATH` defaults to `db_dumps/cdpp.sql`. |
| `backup PATH` | Write a copy of the database to `PATH`, which must not exist. |
| `import-oracc-signs [SOURCE]` | Replace the snapshot of the Oracc Sign List with the signs in `osl.asl`. `SOURCE` is a path or a URL, and defaults to the file in the [OSL repository](https://github.com/oracc/osl). |
| `import-cdli [SOURCE]` | Replace the snapshot of the CDLI catalogue entries of the tablets. `SOURCE` is a path or a URL of the CDLI catalogue in CSV, and defaults to the file in the CDLI data repository. |
| `import-oracc-texts [SOURCE ...]` | Replace the snapshot of the Oracc texts of the tablets. Each `SOURCE` is a path or a URL of an Oracc JSON archive. The defaults are the archives of SAAo, RIAo, RINAP, RIBo and DCCLT. |
| `check-cdli [PATH]` | Write the tablets whose period, city, object type, medium or language does not agree with their CDLI entries into the sections of `PATH`. `PATH` defaults to `docs/questions-for-the-editors.md`. |
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
| `CDPP_PASSWORD` | Not set | Password that each request must give, with HTTP basic authentication. The user name can be any text. If the variable is not set, the site does not ask for a password. |

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
| `/instances/INSTANCE_ID` | A sign instance: its photograph enlarged, its position, its tablet, and the neighbouring instances of the same sign and on the same tablet. `scale` is 1, 2 (the default) or 4. `compare` is the comparison that the page adds the instance to. |
| `/compare?instances=IDS` | Up to 12 sign instances side by side, at one scale. `IDS` is a comma-separated list of instance IDs. `scale` is 1, 2 (the default) or 4. |
| `/compare?sign=SIGN_ID` | Redirects to a comparison of one instance of the sign from each period: the instance with the lowest ID. |
| `/instances/INSTANCE_ID/edit` | The form that edits the position of a sign instance. |
| `/instances/INSTANCE_ID/history` | The change sets that changed a sign instance. |
| `/changes` | All change sets, newest first. |
| `/changes/CHANGE_SET_ID` | A change set, with the form that undoes it. |
| `/search?q=QUERY` | Signs and tablets that match the query. |
| `/media/instance/FILENAME` | A sign photograph. |

The paginated pages take a `page` parameter.

### Tablet filters

Each filter selects the tablets with a related record of the given name, for example `/tablets?period=Old%20Babylonian&medium=clay`. `language` selects the tablets with a sign instance in the given language. `series` selects the tablets whose publication is in the given series, for example `/tablets?series=SAA`.

`city`, `eponym`, `function`, `genre`, `language`, `locality`, `medium`, `method`, `period`, `ruler`, `script_type`, `sent_from`, `sent_to`, `series`, `sub_period`, `text_vehicle`, `year`

### Project layout

| Path | Content |
| --- | --- |
| `src/cdpp/` | The application: models, views, edit pages, filters, search and commands. |
| `src/cdpp/templates/` | Jinja templates. Files with names that start with `_` are fragments that htmx requests, or parts of other templates. |
| `frontend/` | Front-end sources. esbuild bundles them, with htmx, the fonts and the Tailwind build. |
| `migrations/` | Alembic migrations, managed by Flask-Migrate. |
| `migrations/data/` | CSV files that data migrations read. |
| `tests/` | pytest tests. |
| `docs/schema-and-data-questions.md` | Open questions about the schema and the data. |
| `docs/questions-for-the-editors.md` | Questions for the editors of the data, with the tablets, signs and photographs that each question is about. |
| `db_dumps/cdpp.sql` | A snapshot of the data: an SQLite dump of the schema, the records, the change sets and the migration revision. |
| `media/instance/` | Sign photographs. |
| `Dockerfile`, `compose.yaml` | The application image, and a Docker Compose service that runs it. |
| `deploy/start.sh` | Start script of the image: prepares the database on `/data`, then starts gunicorn. |
| `fly.toml` | Fly.io configuration. |
| `utils/`, `csvs/` | Notebooks and spreadsheets from the original preparation of the data. They are not used by the application. |
| `utils/restore_2013_values.py` | Writes the CSV files of the migration that restores the values that the import of 2014 did not copy. |

## About the architecture

The data come from a MySQL dump of the original site, and the table and column names are still those of the MySQL schema. SQLite compares text byte by byte, as the binary collation of the MySQL database did, so sign names such as `S` and `Š` stay distinct.

### Records and snapshots

When editors use the site, the database is the source of record, and its change sets are the history of the edits. The SQL dump in `db_dumps/cdpp.sql` is a snapshot: it is plain text, so version control shows each change between two snapshots. `cdpp load-data` builds a database from a snapshot, for development, for the tests and for a new site. `cdpp backup` copies the database with SQLite's `VACUUM INTO`, which is consistent while the site writes to the database.

### Edits and change sets

Each save of an edit form is one transaction. It changes the record, and writes a row to `change_set` (the editor's name, the time in UTC and an optional comment) and a row to `change` for each value that it changes (the table, the record, the field, and the old and new values as JSON). Triggers refuse to update or delete rows of `change_set` and `change`, so a change set cannot change after it is written.

An edit form contains a digest of the values that it shows. If the digest of the saved values is different when the form is saved, someone saved a change after the form was loaded, and the save stops. Undo writes a new change set that sets each value back to its old value, and refers to the change set that it undoes. Undo stops if a later change set changed one of the values.

The site has no user accounts. If `CDPP_PASSWORD` is set, each request must give that password. A cookie keeps the editor's name, and the site refuses a form that a page on another site sends.

### Consistency rules

A tablet with a city takes its locality from the city, and has a locality of its own only if it has no city. A check constraint refuses a tablet with both. The schema stores other values twice: a tablet has a period and a sub-period, and an eponym and a year. SQLite triggers refuse a change to a tablet or a reign that contradicts its sub-period or its year, and a change to a sub-period or a year that contradicts its tablets or reigns. `CONSISTENCY_RULES` in `src/cdpp/models.py` defines the rules, and a migration creates the same triggers. The triggers do not check the rows that existed before them. A migration that makes one of these tables again in batch mode removes its triggers, so it must create them again: a test compares the triggers of a migrated database with the triggers of the models.

### Years

Years are integers in astronomical numbering: 1 BC is 0, and 1244 BC is -1243. `src/cdpp/dates.py` converts them to the text that pages show, for example 1244 BC, and the year filter takes the same text. The table `eponym_year` gives the eponym of each year that has one, from 910 BC to 645 BC. One eponym name can name more than one year. A tablet page shows the eponym of the year of the tablet, if the tablet has no eponym of its own.

### Search

Search uses two SQLite FTS5 tables with the trigram tokenizer: `search_sign` holds the name of each sign and its names in other sign lists, and `search_tablet` holds the details of each tablet. The tables hold the text in a normalised form, Unicode NFKC and then case folding, so `gir3` finds GIR₃, and `S` and `Š` stay distinct. A search finds the records with a field that contains the query. An exact value ranks first, then a value that starts with the query, then a value that contains it. The trigram index cannot find a query shorter than three characters, so a shorter query reads all the rows. The search tables are derived from the other tables, so they are not in the models, the migrations or the dump. `cdpp load-data` and `cdpp reindex` make them, and a search makes them if they do not exist. The edit forms change only sign instances, which the search tables do not contain.

### Links to sign lists

On a sign page, a sign-list number links to the [Oracc Sign List](https://oracc.museum.upenn.edu/osl/) (OSL) if exactly one OSL sign or form has the same number in that list. An ORACC name links to OSL if exactly one OSL sign or form has that name. After a link, a second link leads to the page of the same sign or form in the electronic Babylonian Library (eBL), if OSL records one. A row of the table links to each OSL page and each eBL page once: the ORACC name and the numbers of a record often lead to the same OSL sign, so only the first of them has the links. The links come from a snapshot of OSL in the tables `oracc_sign` and `oracc_list_number`, so a page does not depend on Oracc. [docs/schema-and-data-questions.md](docs/schema-and-data-questions.md) lists the sign lists that have links, and the open questions about them.

### Links to catalogues

A tablet page links to the CDLI catalogue entry of the tablet, and to the editions of its texts in the Oracc projects SAAo, RIAo, RINAP, RIBo and DCCLT. The links come from snapshots in the tables `cdli_artifact` and `oracc_text`. A tablet matches a CDLI entry by its museum number, the museum number of a join, or its accession number. The tablet page shows the publication in one citation form, and the tablet list can filter by series. The database keeps each publication as its text.

`cdpp check-cdli` compares the period, the city, the object type, the medium and the languages of each tablet with its CDLI entries. The data and CDLI give different names to some periods, places and object types, so tables in `src/cdpp/cdli_comparison.py` state which names agree. The command writes these tables and the tablets that do not agree into the questions for the editors.

### Unicode cuneiform

A sign page, the list of signs and the search results show a sign in Unicode cuneiform if the snapshot of OSL gives one value for the name of the sign, or, if it has no value for that name, one value for the ORACC names of the CDP records of the sign. In the table of CDP records, the column **Unicode** shows the cuneiform of each ORACC name. The font Noto Sans Cuneiform draws one standard form of each sign, not a form from a tablet. OSL writes some signs with characters of the private use area, or with X for a part that Unicode does not have. The pages do not show those values, because the font cannot draw them.

### Photographs, instance pages and comparisons

The photographs have the extension `.jpg`, but most of them are GIF images. The application reads the first bytes of each file, and sends the photograph with the type of its content. On Fly.io, the file server of the machine sends the photographs with the type `image/jpeg` and without cache headers. Browsers identify an image by its content, so they show the GIF images. An instance page and a comparison read the width and the height from the header of the file, and set the size of the enlarged image from them.

On an instance page, the instances of the same sign are in the order of the period, from the first year of the period, then of the museum number, then of the position. The order of positions is the surface (obverse, reverse, then the other surfaces), the column as a Roman numeral, and the line. An instance without a surface or a column sorts with the default, obverse and column i.

A comparison is only in the URL: the parameter `instances` of the comparison page, and the parameter `compare` of an instance page. Each state of a comparison has its own URL, so a user can share it, and the back button undoes an addition. Links between instance pages keep the comparison. Links to other pages do not.

### Pages and htmx

The server renders every page. htmx updates parts of pages without a full reload: the tablet list when a filter changes, the search results while the user types, the table of signs on a tablet page when the JJT notes are hidden or shown, the edit form in a row of that table, and the random selection of signs on the home page. A request from htmx names its target element in the `HX-Target` header, and the server then returns only the fragment for that element. Links and forms also work without JavaScript: without it, the edit form opens on a page of its own. Only the button that shows other signs on the home page needs JavaScript.

Sign names are set in Gentium Book Plus, the interface in Atkinson Hyperlegible Next, and Unicode cuneiform in Noto Sans Cuneiform. The browser loads the cuneiform font only for a page that shows cuneiform. The font subsets do not contain subscript digits, so the browser takes those characters from another font.

## Citation

This project has a DOI: [10.5281/zenodo.11647](https://doi.org/10.5281/zenodo.11647)

Cite as:
Stephan Hügel (2014). Cuneiform Digital Palaeography Project (CDPP) v0.2. Zenodo. 10.5281/zenodo.11647

## Licence

The code is available under the MIT licence. The licence of the data is not settled. See [LICENCE.md](LICENCE.md). The snapshot of the Oracc Sign List in the dump is in the public domain, under the CC0 licence of `osl.asl`.

The snapshot of catalogue entries in the table `cdli_artifact` comes from the [Cuneiform Digital Library Initiative](https://cdli.earth) (CDLI), through its [data repository](https://github.com/cdli-gh/data). Its re-use follows the [CDLI terms of use](https://cdli.earth/terms-of-use), which ask for a citation of CDLI.

The snapshot of Oracc texts in the table `oracc_text` keeps project names and text IDs from the catalogues of the [Oracc](https://oracc.museum.upenn.edu) JSON archives of SAAo, RIAo, RINAP, RIBo and DCCLT, which are released under CC0. The Oracc editions that tablet pages link to are released under CC BY-SA 3.0.
