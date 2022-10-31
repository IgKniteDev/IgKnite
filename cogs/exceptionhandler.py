'''
The `ExceptionHandler` cog for IgKnite.
---

License can be found here:
https://github.com/IgKniteDev/IgKnite/blob/main/LICENSE
'''


# Imports.
from typing import Any

import core
import disnake
from disnake import errors
from disnake.ext import commands


# The actual cog.
class ExceptionHandler(commands.Cog):
    def __init__(self, bot: core.IgKnite) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter: disnake.CommandInteraction, error: Any) -> None:
        error = getattr(error, 'original', error)
        embed = core.TypicalEmbed(inter, is_error=True)
        view = core.SmallView(inter).add_button(
            label='Report Bug',
            url=core.BOT_METADATA['REPOSITORY'] + '/issues/new?template=bug.yml',
            style=disnake.ButtonStyle.red,
        )

        # MissingPermissions
        if isinstance(error, commands.errors.MissingPermissions) or isinstance(
            error, errors.Forbidden
        ):
            embed.set_title('Nice try! You don\'t have permission to do that.')

        # MissingRole
        elif isinstance(error, commands.errors.MissingRole) or isinstance(
            error, commands.errors.MissingAnyRole
        ):
            embed.set_title('Whoops! You\'re missing a role.')

        else:
            embed.set_title('Whoops! An alien error occured.')

        embed.set_description(str(error))
        await inter.send(embed=embed, view=view, ephemeral=True)

    @commands.Cog.listener()
    async def on_user_command_error(self, inter: disnake.CommandInteraction, error: Any) -> None:
        error = getattr(error, 'original', error)
        embed = core.TypicalEmbed(inter, is_error=True)

        # MissingPermissions
        if isinstance(error, commands.errors.MissingPermissions) or isinstance(
            error, errors.Forbidden
        ):
            embed.set_title('Nice try! You don\'t have permission to do that.')

        # MissingRole
        elif isinstance(error, commands.errors.MissingRole) or isinstance(
            error, commands.errors.MissingAnyRole
        ):
            embed.set_title('Whoops! You\'re missing a role.')

        else:
            embed.set_title('Whoops! An alien error occured.')

        embed.set_description(str(error))
        await inter.send(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_message_command_error(self, inter: disnake.CommandInteraction, error: Any) -> None:
        error = getattr(error, 'original', error)
        embed = core.TypicalEmbed(inter, is_error=True)

        # MissingPermissions
        if isinstance(error, commands.errors.MissingPermissions) or isinstance(
            error, errors.Forbidden
        ):
            embed.set_title('Nice try! You don\'t have permission to do that.')

        # MissingRole
        elif isinstance(error, commands.errors.MissingRole) or isinstance(
            error, commands.errors.MissingAnyRole
        ):
            embed.set_title('Whoops! You\'re missing a role.')

        else:
            embed.set_title('Whoops! An alien error occured.')

        embed.set_description(str(error))
        await inter.send(embed=embed, ephemeral=True)


# The setup() function for the cog.
def setup(bot: core.IgKnite) -> None:
    bot.add_cog(ExceptionHandler(bot))
