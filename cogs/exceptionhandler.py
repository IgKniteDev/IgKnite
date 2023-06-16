'''
The `ExceptionHandler` cog for IgKnite.
---

License can be found here:
https://github.com/IgKniteDev/IgKnite/blob/main/LICENSE
'''


# Imports.
from typing import Any

import disnake
from disnake import errors
from disnake.ext import commands

import core


# The actual cog.
class ExceptionHandler(commands.Cog):
    def __init__(self, bot: core.IgKnite) -> None:
        self.bot = bot

    def get_view(self, inter: disnake.CommandInteraction) -> core.SmallView:
        view = core.SmallView(inter).add_button(
            label='It\'s a bug?',
            url=core.BotData.repo + '/issues/new?template=bug.yml',
            style=disnake.ButtonStyle.red,
        )
        return view

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter: disnake.CommandInteraction, error: Any) -> None:
        error = getattr(error, 'original', error)
        embed = core.TypicalEmbed(inter, is_error=True)

        # MissingPermissions
        if isinstance(error, commands.errors.MissingPermissions) or isinstance(
            error, errors.Forbidden
        ):
            embed.title = 'Nice try! I don\'t have permission to do that.'

        # MissingRole
        elif isinstance(error, commands.errors.MissingRole) or isinstance(
            error, commands.errors.MissingAnyRole
        ):
            embed.title = 'Whoops! You\'re missing a role.'

        else:
            embed.title = 'Whoops! An alien error occured.'

        embed.set_description(str(error))
        await inter.send(embed=embed, view=self.get_view(inter), ephemeral=True)

    @commands.Cog.listener()
    async def on_user_command_error(self, inter: disnake.CommandInteraction, error: Any) -> None:
        error = getattr(error, 'original', error)
        embed = core.TypicalEmbed(inter, is_error=True)

        # MissingPermissions
        if isinstance(error, commands.errors.MissingPermissions) or isinstance(
            error, errors.Forbidden
        ):
            embed.title = 'Nice try! I don\'t have permission to do that.'

        # MissingRole
        elif isinstance(error, commands.errors.MissingRole) or isinstance(
            error, commands.errors.MissingAnyRole
        ):
            embed.title = 'Whoops! You\'re missing a role.'

        else:
            embed.title = 'Whoops! An alien error occured.'

        embed.set_description(str(error))
        await inter.send(embed=embed, view=self.get_view(inter), ephemeral=True)

    @commands.Cog.listener()
    async def on_message_command_error(self, inter: disnake.CommandInteraction, error: Any) -> None:
        error = getattr(error, 'original', error)
        embed = core.TypicalEmbed(inter, is_error=True)

        # MissingPermissions
        if isinstance(error, commands.errors.MissingPermissions) or isinstance(
            error, errors.Forbidden
        ):
            embed.title = 'Nice try! I don\'t have permission to do that.'

        # MissingRole
        elif isinstance(error, commands.errors.MissingRole) or isinstance(
            error, commands.errors.MissingAnyRole
        ):
            embed.title = 'Whoops! You\'re missing a role.'

        else:
            embed.title = 'Whoops! An alien error occured.'

        embed.set_description(str(error))
        await inter.send(embed=embed, view=self.get_view(inter), ephemeral=True)


# The setup() function for the cog.
def setup(bot: core.IgKnite) -> None:
    bot.add_cog(ExceptionHandler(bot))
