"""
Dof Discord Bot
===============

Prerequisites
-------------

You must have Python 3 installed. You must have the token loaded (check `src/constants`). You must install this package
by running `python -m pip install .` in `dof-discord-bot` folder.

Usage
-----

Run the code by executing the following::

    python -m dof-discord-bot

Or alternatively, execute the parent folder::

    python <some_path>/dof-discord-bot

Or, if you really want to run the module directly, just execute this file::

    python <some_path>/__main__.py
"""
from src import *

# If you fail to run the code, check if the token is loaded in constants.py
Bot(COMMAND_PREFIX).run(TOKEN)
