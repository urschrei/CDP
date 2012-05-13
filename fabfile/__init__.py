from fabric.api import env, run, local, require, cd, put
from fabric.decorators import task
from fabric.utils import abort
from fabric.contrib.console import confirm
from fabric.context_managers import settings, hide, prefix
from fabric.colors import cyan, yellow, green, red
from time import time
import os

env.basename = os.path.dirname(__file__)


@task
def run_app():
    """
    Start app in debug mode with reloading turned on. Dev only
    """
    with cd(env.basename):
        local('export GLYPH_CONFIGURATION=`pwd`/app/config/dev.py && venv/bin/python ./run.py')


@task
def shell():
    """
    Create a local iPython shell with app imported
    """
    local('export GLYPH_CONFIGURATION=`pwd`/app/config/dev.py && ./shell.py')


@task
def upgrade_db(rev="head"):
    """
    Upgrade DB to specified revision or head. Dev only
    """
    with cd(env.basename):
        local("alembic upgrade %s" % rev)


@task
def downgrade_db(rev="base"):
    """
    Downgrade DB to specified revision or base. Dev only
    """
    with cd(env.basename):
        local("alembic downgrade %s" % rev)
    