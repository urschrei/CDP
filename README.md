# How to get up and running
1. Ensure you have Python 2.7 on your system
2. Ensure you have a recent MySQL installation
3. Ensure you have a blank database named `glyph`, see [config/common.py](config/common.py) for settings
4. Install pip: `(sudo) easy_install pip`
5. Install virtualenv: `(sudo) pip install virtualenv`
6. Clone this repository, and `cd` into it
7. Create a new virtualenv: `virtualenv venv`
8. Activate it: `source venv/bin/activate`
9. Install required packages: `pip install -r requirements.txt`
10. Run `fab create_db` in order to create the database tables
11. Import the latest database dump 'glyph_latest.sql' from `db_dumps`:
 -  Using [Sequel Pro](http://www.sequelpro.com)
 -  Using the command line: `mysql -h 127.0.0.1 -u root -p glyph < db_dumps/glyph_latest.sql `
12. Run `fab upgrade_db` in order to ensure that all database migrations have been run
13. If all goes well, run the app in debug mode: `fab run_app`
14. Access the site on [http://0.0.0.0:5000](http://0.0.0.0:5000)

Other `fab` commands:

- `fab downgrade_db [version]` downgrade the database to the base version, or to a specific revision
- `fab shell` open an IPython shell with an imported app context and db instance. Queries can then be run like so:
    - `db.session.query(Cdp).join(Sign).filter(Sign.sign_ref == 'AK').all()`

### A note on character sets
As we're using MySQl, please pay particular attention to your DB's character encoding and collation settings.  

For encoding, `utf8mb4` should be used.
For collation, `utf8mb4_bin` should be used. Binary collation is required in order to distinguish between e.g. S and Š.
