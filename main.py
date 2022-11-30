'''
License can be found here:
https://github.com/IgKniteDev/IgKnite/blob/main/LICENSE
'''


# Imports.
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
    bot.run(keychain.discord_token)
