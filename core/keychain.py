'''
Global variables and instances for the core package.
---

License can be found here:
https://github.com/IgKniteDev/IgKnite/blob/main/LICENSE
'''


# Imports.
import logging

from decouple import UndefinedValueError, config


# Custom class for handling environment secrets and global variables..
class KeyChain:
    def __init__(self) -> None:
        try:
            self.discord_token = config('DISCORD_TOKEN', cast=str)
            self.discord_owner_id = config('DISCORD_OWNER_ID', cast=int)

            self.spotify_token = config('SPOTIFY_CLIENT_SECRET', cast=str)
            self.client_spotify = config('SPOTIFY_CLIENT_ID', cast=str)

        except UndefinedValueError:
            logging.error(
                'One or more secrets have been left undefined. '
                + 'Consider going through the README.md file for '
                + 'proper instructions on setting IgKnite up.'
            )

        else:
            self.snipeables = []
