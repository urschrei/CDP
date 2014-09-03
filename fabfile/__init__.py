#!/usr/bin/env python
# -*- coding: utf-8 -*-
# n0k …

from fabric.api import env, run, local, require, cd, put
from fabric.decorators import task
from fabric.utils import abort
from fabric.contrib.console import confirm
from fabric.context_managers import settings, hide, prefix
from fabric.colors import cyan, yellow, green, red, white
from time import time
from alembic.config import Config
from alembic import command

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base

import sys
import os
import subprocess


env.basename = os.path.dirname(__file__)
alembic_cfg = Config(os.path.join(os.path.dirname(env.basename), "alembic.ini"))

env.hosts = ['cdpp@oracc.museum.upenn.edu']

@task
def run_app():
    """
    Start app in debug mode with reloading turned on. Dev only
    """
    with cd(env.basename):
        # clean up any *.pyc files in our app dir
        # local('rm glyph/*.pyc')
        local('export GLYPH_CONFIGURATION=`pwd`/config/dev.py && venv/bin/python ./run.py')


@task
def shell():
    """
    Run iPython without the deprecated Werkzeug stuff
    """
    local('export GLYPH_CONFIGURATION=`pwd`/config/dev.py && ipython -i -c "%run shell.py"')


@task
def deploy():
    with cd('CDP/glyph'):
        run('git pull')
        # run('venv/bin/alembic upgrade head')
        # touch run.wsgi


# Alembic stuff. See http://alembic.readthedocs.org/en/latest/api.html
@task
def upgrade_db(rev="head"):
    """
    Upgrade DB to specified revision or head
    """
    print(cyan("Running Alembic migrations, upgrading DB to %s" % rev))
    command.upgrade(alembic_cfg, rev)


@task
def downgrade_db(rev="base"):
    """
    Downgrade DB to specified revision or base
    """
    print(cyan("Running Alembic migrations, downgrading DB to %s" % rev))
    command.downgrade(alembic_cfg, rev)


@task
def show_migrations():
    """
    List all DB migrations in chronological order
    """
    command.history(alembic_cfg)

@task
def build_db():
    """
    Build a database using the App's models
    """
    print(red("Creating CDPP tables in DB"))
    # create / sync all models
    local('export GLYPH_CONFIGURATION=`pwd`/config/dev.py && venv/bin/python ./create_db.py', capture=True)
    # stamp the db with the most recent revision
    command.stamp(alembic_cfg, 'head')
    print(white("Tables successfully created and synced"))
    print(red("Importing latest data dump"))
    proc = subprocess.Popen(
        ["mysql", "--user=root", "glyph"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)
    out, err = proc.communicate(file("db_dumps/glyph_latest.sql").read())
    print(white("Data successfully imported. CDPP DB is ready to use."))
