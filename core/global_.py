'''
Global variables and instances for the core package.
---

License can be found here:
https://github.com/IgKniteDev/IgKnite/blob/main/LICENSE
'''


# Imports.
import time
import logging
from datetime import datetime

from decouple import config, UndefinedValueError


# The initialize() function.
def initialize() -> None:
    '''
    Initialize the global variables required to run all commands properly inside IgKnite.\n
    - Note: This function only needs to be called 'once' inside the root script (main.py).

    ---

    ```python

    # Structure for adding new global variables.
    # Anything non-relatable to environment variables must be put under the 'else' block.

    global variable_name
    variable_name = value

    ```
    '''

    # Fetch the secrets.
    try:
        global tokens
        tokens = {
            'discord': config('DISCORD_TOKEN', cast=str),
            'spotify': config('SPOTIFY_CLIENT_SECRET', cast=str)
        }

        global identifiers
        identifiers = {
            'discord_owner': config('DISCORD_OWNER_ID', cast=int),
            'spotify_client': config('SPOTIFY_CLIENT_ID', cast=str)
        }

    except UndefinedValueError:
        logging.error('''
            One or more secrets have been left undefined.
            Consider going through the README.md file for proper instructions on setting IgKnite up.
        ''')
        time.sleep(5)
        exit()

    else:
        # global variable to store start time
        global running_since
        running_since = round(datetime.timestamp(datetime.now()))

        # global variable to store sniped messages
        global snipeables
        snipeables = []
