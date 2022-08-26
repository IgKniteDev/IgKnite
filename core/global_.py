'''
Global variables and instances for the core package.
---

MIT License

Copyright (c) 2022 IgKnite

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


# Imports.
import time
import logging

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
            'discord': config('DISCORD_TOKEN', cast=str)
        }

        global identifiers
        identifiers = {
            'discord_owner': config('DISCORD_OWNER_ID', cast=int),
        }

    except UndefinedValueError:
        logging.error('''
            One or more secrets have been left undefined.
            Consider going through the README.md file for proper instructions on setting IgKnite up.
        ''')
        time.sleep(5)
        exit()

    else:
        # global variable (list) for storing sniped messages
        global snipeables
        snipeables = []
