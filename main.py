'''
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
from typing import Dict

from decouple import config, UndefinedValueError

from core import global_
from core.bot import IgKnite


# Initialize the global variables from core.global_ .
global_.initialize()

# Fetch the secrets.
try:
    tokens: Dict[str, str] = {
        'discord': config('DISCORD_TOKEN', cast=str)
    }
    owner_ids: Dict[str, int | str] = {
        'discord': config('DISCORD_OWNER_ID', cast=int)
    }

except UndefinedValueError:
    print('''
        One or more secrets have been left undefined.
        Consider going through the README.md file for proper instructions on setting IgKnite up.
    ''')
    time.sleep(5)
    exit()


# Set up an instance of IgKnite.
bot = IgKnite()


# Run the bot.
if __name__ == '__main__':
    bot.load_extensions('cogs')
    bot.run(tokens['discord'])
