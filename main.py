# SPDX-License-Identifier: MIT


# Imports.
from time import sleep

import disnake

import core
from core.chain import keychain

# Set up an instance of IgKnite.
bot = core.IgKnite(
    intents=disnake.Intents.all()
)


# Run!
if __name__ == '__main__':
    while (tries := 0) <= 5:
        tries += 1
        try:
            bot.run(keychain.discord_token)
        except disnake.errors.HTTPException:
            print('Failed to connect, retrying...')
            sleep(2)
