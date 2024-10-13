# SPDX-License-Identifier: MIT


# Imports.
from typing import Any
import logging
import os 
import json

import disnake
from disnake import errors
from disnake.ext import commands

import core

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

Exception_config_path="./cogs/exceptionhandler.json"

class LogerrorsCommandView(disnake.ui.View):
    """A view for the logerror command.
    Inherits:
        disnake.ui.View
    Args:
        inter (disnake.CommandInter): The interaction object.
        timeout (float): View interaction will be disabled after this time.
    """

    def __init__(self, inter: disnake.CommandInter, *, timeout: float = 15) -> None:
        super().__init__(timeout = timeout)
        self.inter = inter
        self.clicked = False

    @disnake.ui.button(label='Log Errors here', style=disnake.ButtonStyle.gray)
    async def logerrors(self, button: disnake.ui.Button, inter: disnake.Interaction)-> None:
        """disables the button in the view and logs the error in the specified channel."""
        self.clicked = True
        await inter.response.defer()

        for child in self.children:
            child.disabled = True
        await self.inter.edit_original_message(view=self)

        self.config = {
            "guild_id": inter.guild.id,
            "guild_name": inter.guild.name,
            "channel_id": inter.channel.id,
            "channel_name": inter.channel.name
        }

        with open(Exception_config_path, "w") as f:
            json.dump(self.config, f, indent=4)
        logger.info(f"Error logging enabled to guild. Guild: `{inter.guild.name}`, Channel: `{inter.channel.name}`")
        
        await inter.send(f"Error logging enabled in this guild. Guild: `{inter.guild.name}`, Channel: `{inter.channel.name}`", ephemeral=True)

    async def on_timeout(self) -> None:
        """Disables the button in the view after the timeout."""
        if not self.clicked:
            for child in self.children:
                child.disabled = True
            await self.inter.send("You took too long to respond. Please try again.", ephemeral=True)
            await self.inter.edit_original_message(view=self)


class ExceptionHandler(commands.Cog):
    """Contains commands for handling exceptions during command execution.
    Inherits:
        commands.Cog
    Args:
        bot (core.IgKnite): An instance of `core.IgKnite`."""
    def __init__(self, bot: core.IgKnite) -> None:
        self.bot = bot
    
        if not os.path.exists(Exception_config_path):
            logger.warning("exceptionhandler.json not found... file will be created when `logerrors` command is used.")
        else:    
            try:
                with open(Exception_config_path, "r") as f:
                    self.config = json.load(f)
                    logger.info(f"exceptionhandler.json present. Logging errors guild: {self.config.get('guild_name')}, channel: {self.config.get('channel_name')}")
            except json.JSONDecodeError:
                logger.error("Log errors: exceptionhandler.json is not a valid json file...")
                self.config = {}

            

    def get_view(self, inter: disnake.CommandInter) -> core.SmallView:
        return core.SmallView(inter).add_button(
            label="Think it's a bug?",
            url=core.BotData.repo + '/issues/new?template=bug.yml',
            style=disnake.ButtonStyle.red,
        )
        

    async def process_error(
        self, inter: disnake.CommandInter, error: Any
    ) -> None:
        """
        A method for processing the exceptions caused in interaction commands and responding
        accordingly.
        """

        logger.error(f"[!]Error in command \"{inter.application_command.qualified_name}\". Error: \"{error}\". User: `{inter.author}`. Guild: `{inter.guild}`. Channel: `{inter.channel if inter.guild else None}`. Cog: \"{inter.application_command.cog_name}\"",exc_info=True)
        if self.config:
            try:
                await self.bot.get_channel(self.config['channel_id']).send(f"[!]Error in command \"{inter.application_command.qualified_name}\". \nError: \"{error}\". \nUser: `{inter.author}`. Guild: `{inter.guild}`. Channel: `{inter.channel if inter.guild else None}`. Cog: \"{inter.application_command.cog_name}\"")
            except Exception as e:
                logger.error(f"Failed to log error in the specified channel. Error: {e}")

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

        #cooldown
        elif isinstance(error, commands.errors.CommandOnCooldown):
            embed.title = "Hold your horses!"

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

    @commands.slash_command(
        name='logerrors',
        dm_permission=False,
    )
    @commands.is_owner()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def log_errors(self, inter: disnake.CommandInter) -> None:
        """Logs errors in the specified channel.
        """
        msg=""
        if self.config:
            msg=f"Error logging is already enabled in the channel `{self.config.get('channel_name')}` in the guild `{self.config.get('guild_name')}`."
        msg+=" Are you sure you want to enable error logging in this channel?"
        embed = core.TypicalEmbed(inter=inter, title="Log errors here?", description=msg,disabled_footer=True)

        await inter.send(embed=embed, view=LogerrorsCommandView(inter,timeout=15))



# The setup() function for the cog.
def setup(bot: core.IgKnite) -> None:
    bot.add_cog(ExceptionHandler(bot))
