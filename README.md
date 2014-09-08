# Cuneiform Digital Palæography Project (CDPP)
## Installation
1. Ensure you have Python 2.7.x on your system
2. Ensure you have a recent MySQL (5.5.x / 5.6.x) installation
3. Ensure you have a blank database named `glyph`, see [config/common.py](config/common.py) for settings
4. Install pip: `(sudo) easy_install pip`
5. Install virtualenv: `(sudo) pip install virtualenv`
6. Clone this repository, and `cd` into it
7. Create a new virtualenv: `virtualenv venv`
8. Activate it: `source venv/bin/activate`
9. Install required packages: `pip install -r requirements.txt`
10. Run `fab build_db` in order to create the database tables and import the latest data dump
11. Once the tables have been created and populated, run the app in debug mode: `fab run_app`
12. Access the site on [http://0.0.0.0:5000](http://0.0.0.0:5000)

Other `fab` commands:

- `fab shell` open an IPython shell with an imported app context and db instance. Queries can then be run like so:
    - `db.session.query(Cdp).join(Sign).filter(Sign.sign_ref == 'AK').all()`

## Elasticsearch
The search functionality requires [Elasticsearch](http://www.elasticsearch.org/overview/), running on port 9200.  

In order to generate the index before first use, run `fab elasticsearch`. Record changes and insertions should propagate to the index automatically, so long as the ORM is being used (i.e. in the normal course of things). The import script may also be run manually from a `fab shell`: `%run utils/elastic.py`

## A note on character sets
As we're using MySQL, please pay particular attention to your DB's character encoding and collation settings.  

For encoding, `utf8mb4` should be used.
For collation, `utf8mb4_bin` should be used. Binary collation is required in order to distinguish between e.g. S and Š.
