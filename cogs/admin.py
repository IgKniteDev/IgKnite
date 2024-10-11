# SPDX-License-Identifier: MIT


# Imports.

import disnake
from disnake.ext import commands
from disnake.ext.commands import errors
import logging

import core

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Admin(commands.Cog):

    def __init__(self, bot: core.IgKnite) -> None:
        logger.info("[+]Loading Admin cog... init")
        self.bot = bot

    @commands.slash_command(
        name='pingi', description='Shows my current response time.'
    )
    async def _ping(self, inter: disnake.CommandInter) -> None:
        
        await inter.send("no this ")


    @commands.slash_command(
            name='reloadext',
            description='Reload an cog extension.',
            dm_permission=False
        )
    async def reload_extension(
        self, inter: disnake.CommandInter, name: str
    ) -> None:
        """ Use this command to reload an cog extension.
        Args:
            name (str): The name of the extension to reload.
        Exampls use:
            /reloadext admin
            /reloadext general
        """
        try:
            inter.bot.reload_extension(name)
            logger.info(f"Reloaded {name} extension.")
        except Exception as e:
            if isinstance(e, errors.ExtensionNotLoaded):
                msg = f'`{name}` extension is not loaded.'
            elif isinstance(e, errors.ExtensionNotFound):
                msg = f'No extension with name `{name}` exists.'
            elif isinstance(e, errors.ExtensionFailed):
                msg = f'Failed to load `{name}` extension.'
            elif isinstance(e, errors.NoEntryPointError):
                msg = f'Setup function is not defined in `{name}` file.'
            # getting here shouldnt happen, just making sure msg
            # doesnt have an Unbound type.
            else:
                msg = f'Something went wrong while loading `{name}` extension.'

            logger.error(f"Loading extension failed. Reason: {msg}")

            embed = core.TypicalEmbed(description=msg, is_error=True)
            await inter.send(embed=embed)
        else:
            embed = core.TypicalEmbed(
                description=f'Successfully reloaded `{name}` extension.'
            )
            await inter.send(embed=embed)

    @reload_extension.error
    async def reload_ext(
        self, inter: disnake.CommandInter, error: errors.CommandError
    ) -> None:
        if isinstance(error, errors.MissingRequiredArgument):
            embed = core.TypicalEmbed(
                description='Please provide an extension name.', is_error=True
            )
            await inter.send(embed=embed)
        # a check failure would be raised when someone who is not
        # an owner uses the command but we dont wanna catch it,
        # since we dont wanna send any messages if someone who
        # isn't an owner uses the command.
    
    @commands.slash_command(name='unloadext')
    @commands.is_owner()
    async def unload_extension(
        self, inter: disnake.CommandInter, name: str
    ) -> None:
        """ Use this command to unload an cog extension.
        Args:
            name (str): The name of the extension to unload.
        Exampls use:
            /unloadext admin
            /unloadext general
        """
        try:
            inter.bot.unload_extension(name)
            logger.info(f"Unloaded {name} extension.")
        except Exception as e:
            if isinstance(e, errors.ExtensionNotLoaded):
                msg = f'`{name}` extension is not loaded.'
            elif isinstance(e, errors.ExtensionNotFound):
                msg = f'No extension with name `{name}` exists.'
            # getting here shouldnt happen, just making sure msg
            # doesnt have an Unbound type.
            else:
                msg = f'Something went wrong while unloading `{name}` extension.'

            logger.error(f"Unloading extension failed. Reason: {msg}")

            embed = core.TypicalEmbed(description=msg, is_error=True)
            await inter.send(embed=embed)
        else:
            embed = core.TypicalEmbed(
                description=f'Successfully unloaded `{name}` extension.'
            )
            await inter.send(embed=embed)
    
    @commands.slash_command(name='loadext')
    @commands.is_owner()
    async def load_extension(
        self, inter: disnake.CommandInter, name: str
    ) -> None:
        """ Use this command to load an cog extension.
        Args:
            name (str): The name of the extension to load.
        Exampls use:
            /loadext admin
            /loadext general
        """
        try:
            inter.bot.load_extension(name)
            logger.info(f"Loaded {name} extension.")
        except Exception as e:
            if isinstance(e, errors.ExtensionAlreadyLoaded):
                msg = f'`{name}` extension is already loaded.'
            elif isinstance(e, errors.ExtensionNotFound):
                msg = f'No extension with name `{name}` exists.'
            elif isinstance(e, errors.NoEntryPointError):
                msg = f'Setup function is not defined in `{name}` file.'
            # getting here shouldnt happen, just making sure msg
            # doesnt have an Unbound type.
            else:
                msg = f'Something went wrong while loading `{name}` extension.'

            logger.error(f"Loading extension failed. Reason: {msg}")

            embed = core.TypicalEmbed(description=msg, is_error=True)
            await inter.send(embed=embed)
        else:
            embed = core.TypicalEmbed(
                description=f'Successfully loaded `{name}` extension.'
            )
            await inter.send(embed=embed)

    @commands.slash_command(name='shutdown')
    @commands.is_owner()
    async def shutdown(self, inter: disnake.CommandInter) -> None:
        """ Use this command to shutdown the bot. """
        logger.info('[X]Shutting down...')
        await inter.send('Shutting down...')
        await inter.bot.close()

    async def cog_check(self, inter: disnake.CommandInter) -> bool:
        logger.info(f"[-----]Checking if {inter.author} is an owner.")
        return await inter.bot.is_owner(inter.author)


def setup(bot: core.IgKnite) -> None:
    logger.info("[+]Loading Admin cog...")
    bot.add_cog(Admin(bot))
