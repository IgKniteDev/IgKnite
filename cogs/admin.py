# SPDX-License-Identifier: MIT


# Imports.

import disnake
from disnake.ext import commands
from disnake.ext.commands import errors
import logging
import time

import core

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ShutdownCommandView(disnake.ui.View):
    def __init__(self, inter: disnake.CommandInter, *, timeout: float = 30) -> None:
        super().__init__(timeout=timeout)
        self.inter = inter

    @disnake.ui.button(label='Shutdown', style=disnake.ButtonStyle.red)
    async def shutdown(self, button: disnake.ui.Button, inter: disnake.Interaction):

        await inter.response.send_message('You clicket the button...', ephemeral=True)
        for child in self.children:
            child.disabled = True
        await inter.edit_original_message(view=self)
        

    # @disnake.ui.button(label='Cancel', style=disnake.ButtonStyle.gray)
    # async def cancel(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
    #     await interaction.response.send_message('Shutdown cancelled.', ephemeral=True)
    #     self.stop()

class Admin(commands.Cog):

    def __init__(self, bot: core.IgKnite) -> None:
        
        self.bot = bot

    
    @commands.slash_command(
            name='cog',
            description='Manage cog extensions.',
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_owner()
    async def _cog(self, inter: disnake.CommandInter) -> None:
        """Manage cog extensions.
        """
        pass
    @_cog.sub_command(
        name="list",
        description='List all cog extensions.',
    )
    async def list_extensions(self, inter: disnake.CommandInter) -> None:
        """List all cog extensions.
        """

        extensions = self.bot.extensions
        embed = core.TypicalEmbed(
            title='List of all cog extensions.',
            description='\n'.join(extensions.keys()),
        )
        await inter.send(embed=embed)

    @_cog.sub_command(
            name='reload',
            description='Reload an cog extension.',
            
        )
    async def reload_extension(
        self, 
        inter: disnake.CommandInter, 
        name: str= commands.Param(description='The name of the extension to reload.')
    ) -> None:
        """ Reload an cog extension.
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

    
    @_cog.sub_command(name='unload', description='Unload an cog extension.')
    
    async def unload_extension(
        self, inter: disnake.CommandInter, name: str= commands.Param(description='The name of the cog extension to unload.')
    ) -> None:
        """unload an cog extension.
        Args:
            name (str): The name of the extension to unload.
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
    
    @_cog.sub_command(
            name='load',
            description='Load an cog extension.',
            )
    async def load_extension(
        self, inter: disnake.CommandInter, name: str= commands.Param(description='The name of the cog extension to load.')
    ) -> None:
        """ Load an cog extension.
        Args:
            name (str): The name of the extension to load.
        
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

            logger.error(f"Loading extension failed. Reason: {msg} Error: {e}")

            embed = core.TypicalEmbed(description=msg, is_error=True)
            await inter.send(embed=embed)
        else:
            embed = core.TypicalEmbed(
                description=f'Successfully loaded `{name}` extension.'
            )
            await inter.send(embed=embed)


    # def get_view(self, inter: disnake.CommandInter) -> core.SmallView:
    #     view = core.SmallView(inter,timeout=15).add_button(
    #         label="Shutdown",
    #         style=disnake.ButtonStyle.red,
    #     )
    #     return view
    
    # async def disable_button(self,view:core.SmallView,inter: disnake.CommandInter) -> None:
    #     """disables the button once the user has clicked it"""
    #     logger.info("I am inside disable_button")
    #     await view.disable_button(inter)

        

    @commands.slash_command(
            name='shutdown',
            description='Shutdown the bot.',
            # cooldown=disnake.Cooldown(1, 5, disnake.BucketType.user),
            )
    @commands.is_owner()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def shutdown(self, inter: disnake.CommandInter) -> None:
        """Shutdown the bot. """
        
        embed = core.TypicalEmbed(
                description='Are you sure you want to shut down the bot?',
            )
        
        await inter.send(embed=embed,view=ShutdownCommandView(inter))
        
        try:
            # await inter.bot.wait_for('button_click', check=lambda i: i.author == inter.author, timeout=15)
            pass
        except TimeoutError:
            return await inter.send('You took too long to respond.')
        # await self.disable_button(view,inter)
        logger.info('[X]Shutting down...')
        time.sleep(10)
        await inter.send('Shutting down...')
        #sleep for 10 seconds
        
        await inter.bot.close()



def setup(bot: core.IgKnite) -> None:
    bot.add_cog(Admin(bot))
