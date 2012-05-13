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
    """Start app in debug mode (for development)."""
    with cd(env.basename):
        local('export GLYPH_CONFIGURATION=`pwd`/app/config/dev.py && venv/bin/python ./run.py')


@task    
def shell():
    "Gets a local shell"
    local('export GLYPH_CONFIGURATION=`pwd`/app/config/dev.py && ./shell.py')
