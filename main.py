'''
License can be found here

https://github.com/IgKniteDev/IgKnite/blob/main/LICENSE
'''


# Imports.
import disnake
from core import global_, IgKnite

# Initialize the global variables from core.global_ .
global_.initialize()

# Set up an instance of IgKnite.
bot = IgKnite(
    intents=disnake.Intents.all(),
    initial_extensions=[
        'cogs.customization',
        'cogs.exceptionhandler',
        'cogs.general',
        'cogs.inspection',
        'cogs.moderation',
        'cogs.music'
    ]
)

# Run!
if __name__ == '__main__':
    bot.run(global_.tokens['discord'])
