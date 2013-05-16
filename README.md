# How to get up and running
1. Ensure you have Python 2.7 on your system
2. Ensure you have a recent MySQL installation
3. Ensure you have a blank database named `glyph`
4. Install pip: `(sudo) easy_install pip`
5. Install virtualenv: `(sudo) pip install virtualenv`
6. Clone this repository, and `cd` into it
7. Import the latest database dump from `db_dumps` using e.g. [Sequel Pro](http://www.sequelpro.com)
8. Create a new virtualenv: `virtualenv venv`
9. Activate it: `source venv/bin/activate`
10. Install required packages: `pip install -r requirements.txt`
11. If all goes well, run the app in debug mode: `fab run_app`
12. Access the site on 0.0.0.0:5000
