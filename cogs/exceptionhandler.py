# SPDX-License-Identifier: MIT


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

    def get_view(self, inter: disnake.CommandInter) -> core.SmallView:
        view = core.SmallView(inter).add_button(
            label="Think it's a bug?",
            url=core.BotData.repo + '/issues/new?template=bug.yml',
            style=disnake.ButtonStyle.red,
        )
        return view

    async def process_error(
        self, inter: disnake.CommandInter, error: Any
    ) -> None:
        """
        A method for processing the exceptions caused in interaction commands and responding
        accordingly.
        """

        error = getattr(error, 'original', error)
        embed = core.TypicalEmbed(inter=inter, is_error=True)

        # MissingPermissions
        if isinstance(error, commands.errors.MissingPermissions) or isinstance(
            error, errors.Forbidden
        ):
            embed.title = "Nice try! I don't have permission to do that."

        # MissingRole
        elif isinstance(error, commands.errors.MissingRole) or isinstance(
            error, commands.errors.MissingAnyRole
        ):
            embed.title = "Oops! You're missing a role."

        # Anything else...
        else:
            embed.title = 'Oops! An alien error occured.'

        embed.description = str(error)
        await inter.send(embed=embed, view=self.get_view(inter), ephemeral=True)

    @commands.Cog.listener()
    async def on_slash_command_error(
        self, inter: disnake.CommandInter, error: Any
    ) -> None:
        await self.process_error(inter, error)

    @commands.Cog.listener()
    async def on_user_command_error(
        self, inter: disnake.CommandInter, error: Any
    ) -> None:
        await self.process_error(inter, error)

    @commands.Cog.listener()
    async def on_message_command_error(
        self, inter: disnake.CommandInter, error: Any
    ) -> None:
        await self.process_error(inter, error)


# The setup() function for the cog.
def setup(bot: core.IgKnite) -> None:
    bot.add_cog(ExceptionHandler(bot))
