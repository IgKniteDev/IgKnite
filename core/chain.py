# SPDX-License-Identifier: MIT


# Imports.
import logging
from typing import List

from decouple import UndefinedValueError, config
from disnake import Message


# Custom class for handling environment secrets and global variables..
class KeyChain:
    def __init__(self) -> None:
        try:
            self.discord_token = config('DISCORD_TOKEN', cast=str)
            self.spotify_client_secret = config(
                'SPOTIFY_CLIENT_SECRET', cast=str
            )
            self.spotify_client_id = config('SPOTIFY_CLIENT_ID', cast=str)

        except UndefinedValueError:
            logging.error(
                'One or more secrets have been left undefined. '
                + 'Consider going through the README.md file for '
                + 'proper instructions on setting IgKnite up.'
            )

        else:
            self.snipeables: List[Message] = []


# Initializing it.
keychain = KeyChain()
