# Cuneiform Digital Palæography Project (CDPP)

## Installation (manual, assumes an Apache server)
1. Ensure you have `git` and `mod_wsgi` installed on your box, install using yum if necessary
2. Install the Python `Virtualenv` package using yum
3. Clone this repository: `git clone https://github.com/urschrei/CDP.git`
4. `cd` to the directory (it's probably called `CDP`)
5. Create a new [virtualenv](http://virtualenv.readthedocs.org/en/latest/virtualenv.html) called `venv`, by executing `virtualenv venv`
6. Activate it by executing `source venv/bin/activate` 
7. Install the required Python libraries by executing `pip install -r requirements.txt`
8. Ensure that a MySQL database named `glyph` exists. Username and password should both be `glyph`. See the section on Character Sets, below, for encoding and collation settings
9. Execute `fab build_db` to create the database structure and populate it. The db can also be populated by first importing `db_dumps/schema.sql`, then importing `db_dumps/glyph_latest.sql`
10. Open the `run.wsgi` file in an editor, and modify the first line with the **full path** to the `activate_this` script. For example, if you've cloned this repository into the `/var/www` directory, the full path would be `/var/www/CDP/venv/bin/activate_this.py`
11. See [here](http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/#configuring-apache) for a sample Apache WSGI virtualhost
12. Remember to reload Apache when you've created the new vhost.

## Development Box Installation (will run on Nginx/Gunicorn in a virtual machine)
1. Install [Vagrant](http://www.vagrantup.com) and [Virtualbox](https://www.virtualbox.org)
2. Clone this repository, and `cd` into it
3. Run `vagrant up`. This will create a new virtual machine with all necessary packages
4. When it's completed, run `vagrant ssh` to access the VM
5. Run `fab build_db` to populate the database
5. Run `fab run_app` to start the application in debug mode
6. Access the site on [localhost:5000](http://localhost:5000)
7. The site will run in production configuration on `10.11.12.15`

Other `fab` commands:

- `fab shell`: open an IPython shell with an imported app context and db instance. Queries can then be run like so:
    - `db.session.query(Cdp).join(Sign).filter(Sign.sign_ref == 'AK').all()`

### Database admin
The database can be accessed via SSH (using e.g. Sequel Pro):

1. The SSH host is 10.11.12.15
2. The SSH user and password are `vagrant/vagrant`
3. The MySQL user is `root`, the password is blank

The application user/pass are `glyph/glyph`, and the db is `glyph`


## Elasticsearch
The search functionality requires [Elasticsearch](http://www.elasticsearch.org/overview/), running on port 9200.  

In order to generate the index before first use, run `fab elasticsearch`. Record changes and insertions should propagate to the index automatically, so long as the ORM is being used (i.e. in the normal course of things). The import script may also be run manually from a `fab shell`: `%run utils/elastic.py`

## A note on MySQL character sets
As we're using MySQL, please pay particular attention to your DB's character encoding and collation settings, if you're setting it up manually.    

For encoding, `utf8mb4` should be used.
For collation, `utf8mb4_bin` should be used. Binary collation is required in order to distinguish between e.g. S and Š.

## Citation
This project has a DOI: [10.5281/zenodo.11647](http://dx.doi.org/10.5281/zenodo.11647)  

Cite as:  
Stephan Hügel (2014). Cuneiform Digital Palaeography Project (CDPP) v0.2. ZENODO.  
10.5281/zenodo.11647  
[![DOI](https://zenodo.org/badge/doi/10.5281/zenodo.11647.png)](http://dx.doi.org/10.5281/zenodo.11647)
