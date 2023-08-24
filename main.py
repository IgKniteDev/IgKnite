# SPDX-License-Identifier: MIT


# Imports.
from os import system

import disnake

import core
from core.chain import keychain

# Set up an instance of IgKnite.
bot = core.IgKnite(
    intents=disnake.Intents.all(),
    initial_extensions=[
        'cogs.customization',
        'cogs.exceptionhandler',
        'cogs.general',
        'cogs.inspection',
        'cogs.moderation',
        'cogs.music',
    ],
)


# Run!
if __name__ == '__main__':
    try:
        bot.run(keychain.discord_token)
    except disnake.errors.HTTPException:
        system('python reboot.py && kill 1')
