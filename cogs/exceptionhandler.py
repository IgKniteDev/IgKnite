'''
The `ExceptionHandler` cog for IgKnite.
---

License can be found here:
https://github.com/IgKniteDev/IgKnite/blob/main/LICENSE
'''


# Imports.
from typing import Any

import disnake
from disnake.ext import commands

import core


# The actual cog.
class ExceptionHandler(commands.Cog):
    def __init__(
        self,
        bot: core.IgKnite
    ) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_slash_command_error(
        self,
        inter: disnake.CommandInteraction,
        error: Any
    ) -> None:
        error = getattr(error, 'original', error)
        embed = core.TypicalEmbed(inter, is_error=True)

        if (
            isinstance(error, commands.errors.MissingRole)
            or isinstance(error, commands.errors.MissingAnyRole)
        ):
            embed.set_title('Whoops! You\'re missing a role.')

        else:
            embed.set_title('Whoops! An alien error occured.')

        embed.set_description(str(error))
        await inter.send(embed=embed, ephemeral=True)


# The setup() function for the cog.
def setup(bot: core.IgKnite) -> None:
    bot.add_cog(ExceptionHandler(bot))
