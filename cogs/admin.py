# SPDX-License-Identifier: MIT


# Imports.

import disnake
from disnake.ext import commands
from disnake.ext.commands import errors
import logging
import time
import json
import os

import core

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

Cog_config_path = "./cogs/cogs.json"

#todo: add registration of cogs. modify the json when cogs is loaded, unloaded, registered, unregistered.
class ShutdownCommandView(disnake.ui.View):
    """A view for the shutdown command.
    Inherits:
        disnake.ui.View
    Args:
        inter (disnake.CommandInter): The interaction object.
        timeout (float): View interaction will be disabled after this time.
    """

    def __init__(self, inter: disnake.CommandInter, *, timeout: float = 15) -> None:
        super().__init__(timeout = timeout)
        self.inter = inter
        self.clicked=False

    @disnake.ui.button(label='Shutdown', style=disnake.ButtonStyle.red)
    async def shutdown(self, button: disnake.ui.Button, inter: disnake.Interaction)-> None:
        """disables the button and shuts down the bot."""
        logger.info('Shutdown button clicked')
        self.clicked=True
        await inter.response.defer()

        for child in self.children:
            child.disabled = True
        logger.info('[X]Shutting down...')
        
        await inter.send('Shutting down...', ephemeral=True)
        await inter.edit_original_message(view=self)
        
        #sleep for 3 seconds before shutting down
        time.sleep(3)
        
        await inter.bot.close()
        

    async def on_timeout(self) -> None:
        """Disables the button in the view after timeout."""
        if not self.clicked:
            for child in self.children:
                child.disabled = True
            # try:
            await self.inter.send('You took too long to respond. Please try again', ephemeral=True)
            await self.inter.edit_original_message(view=self)
        

class Admin(commands.Cog):
    """Contains commands for cog handler and shutdown
    Inherits:
        commands.Cog
    Args:
        bot (core.IgKnite): An instance of `core.IgKnite`.
    """

    def __init__(self, bot: core.IgKnite) -> None:

        self.bot = bot
        #wait until bot is ready
        


        self.loaded_cogs=[] #cogs which are loaded
        self.all_cogs=[] #cogs which are present in the cogs.json file
        self.cog_object=[] #cogs.json object

        #read cog configuration from file
        
    @commands.Cog.listener()
    async def on_ready(self):
        """Load the cogs when the bot is ready.
        This is seperated from __init__ to avoid conflict with bot.py's cog loading, where the cog enabled status changes due to errors in loading the cog."""
        try:
            self.cog_object=json.load(open(Cog_config_path))
        except FileNotFoundError:
            logger.error("cogs.json not found... please see if the file exists in the cogs directory.")
            
        except json.JSONDecodeError:
            logger.error("cogs.json is not a valid json file...")
        for cog in self.cog_object:
            if cog['is_enabled']:
                self.loaded_cogs.append(cog['name'])
            self.all_cogs.append(cog['name'])

    def update_cog_object(self, name:str, is_enabled:bool):
        """When a cog status is changed, this function is used to update the cogs.json file.
        Args:
            name (str): The name of the cog to update.
            is_enabled (bool): The status of the cog."""
        if is_enabled:
            if name not in self.loaded_cogs:
                self.loaded_cogs.append(name)
        else:
            if name in self.loaded_cogs:
                self.loaded_cogs.remove(name)
        for cog in self.cog_object:
            if cog['name']==name:
                cog['is_enabled']=is_enabled
        with open(Cog_config_path, 'w') as f:
            json.dump(self.cog_object,f,indent=4)
    
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
        #registerd cogs
        embed = core.TypicalEmbed(
            title='List of registered cogs:',
            description='\n'.join(self.all_cogs),
     
        )
        #loaded cogs
        embed.add_field(
            name='**Loaded Cogs:**',
            value='\n'.join(self.loaded_cogs) if self.loaded_cogs else 'No cogs loaded.'
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
            inter.bot.reload_extension(f"cogs.{name}")
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
            is_error=True
        else:
            msg = f'Successfully reloaded `{name}` extension.'
            is_error=False
        embed = core.TypicalEmbed(
            description=f'Successfully reloaded `{name}` extension.',is_error=is_error
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
            if name not in self.all_cogs:
                raise errors.ExtensionNotFound(name)
            if name == "admin":
                return await inter.send("You cannot unload the admin cog.")
            inter.bot.unload_extension(f"cogs.{name}")
            self.update_cog_object(name,False)
            logger.info(f"Unloaded {name} extension. cog object: {self.cog_object}")

        except Exception as e:
            if isinstance(e, errors.ExtensionNotLoaded):
                msg = f'`{name}` extension is not loaded.\n Use `/cog load {name}` to load it.'
            elif isinstance(e, errors.ExtensionNotFound):
                msg = f'No extension with name `{name}` is registered.\n Use `/cog register {name}` to register it.'
            # getting here shouldnt happen, just making sure msg
            # doesnt have an Unbound type.
            else:
                msg = f'Something went wrong while unloading `{name}` extension.'

            logger.error(f"Unloading extension failed. Reason: {msg}")

            is_error=True
        else:
            msg = f'Successfully unloaded `{name}` extension.'
            is_error=False
        embed = core.TypicalEmbed(
            description=f'Successfully unloaded `{name}` extension.',is_error=is_error
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
            if name not in self.all_cogs:
                raise errors.ExtensionNotFound(name)
            inter.bot.load_extension(f"cogs.{name}")
            #update the cog object
            self.update_cog_object(name,True)
            logger.info(f"Loaded {name} extension.")
        except Exception as e:
            if isinstance(e, errors.ExtensionAlreadyLoaded):
                msg = f'`{name}` extension is already loaded.'
            elif isinstance(e, errors.ExtensionNotFound):
                msg = f'No extension with name `{name}` exists.\n Use `/cog register {name}` to register it.'
            elif isinstance(e, errors.NoEntryPointError):
                msg = f'Setup function is not defined in `{name}` file.'
            # getting here shouldnt happen, just making sure msg
            # doesnt have an Unbound type.
            else:
                msg = f'Something went wrong while loading `{name}` extension.'

            logger.error(f"Loading extension failed. Reason: {msg} Error: {e}")

            is_error=True
            
        else:
            msg = f'Successfully loaded `{name}` extension.'
            is_error=False
        embed = core.TypicalEmbed(
            description=f'Successfully loaded `{name}` extension.',is_error=is_error
        )
        await inter.send(embed=embed)

    @_cog.sub_command(
        name='register',
        description='Register an cog extension.',
    )
    async def register_extension(
        self, inter: disnake.CommandInter, name: str= commands.Param(description='The name of the extension to register.'), description: str= commands.Param(description='Description of the extension.')
    ) -> None:
        """ Register an cog extension.
        Args:
            name (str): The name of the extension to register.
        """
        if name in self.all_cogs:
            embed = core.TypicalEmbed(
                description=f'`{name}` extension is already registered.',
                is_error=True
            )
            
        #check if cog file is present
        elif not os.path.exists(f"./cogs/{name}.py"):
            embed = core.TypicalEmbed(
                description=f'`{name}` extension file is not found. Make sure it is present in the cogs directory.',
                is_error=True
            )
            
        else:
            self.cog_object.append({'name':name, 'description':description,'is_enabled':False})
            self.all_cogs.append(name)
            with open(Cog_config_path, 'w') as f:
                json.dump(self.cog_object,f,indent=4)
            embed = core.TypicalEmbed(
                description=f'Successfully registered `{name}` extension.'
            )
        await inter.send(embed=embed)

    @_cog.sub_command(
        name='unregister',
        description='Unregister an cog extension.',
    )
    async def unregister_extension(
        self, inter: disnake.CommandInter, name: str= commands.Param(description='The name of the extension to unregister.')
    ) -> None:
        """ Unregister an cog extension.
        Args:
            name (str): The name of the extension to unregister.
        """
        if name not in self.all_cogs:
            embed = core.TypicalEmbed(
                description=f'`{name}` extension is not registered.',
                is_error=True
            )
            
        elif name in self.loaded_cogs:
            embed = core.TypicalEmbed(
                description=f'`{name}` extension is loaded. Unload it first.',
                is_error=True
            )
            
        else:
            self.cog_object=[cog for cog in self.cog_object if cog['name']!=name]
            self.all_cogs.remove(name)
            with open(Cog_config_path, 'w') as f:
                json.dump(self.cog_object,f,indent=4)
            embed = core.TypicalEmbed(
                description=f'Successfully unregistered `{name}` extension.'
            )
        await inter.send(embed=embed)

    @commands.slash_command(
            name='shutdown',
            description='Shutdown the bot.',
            # cooldown=disnake.Cooldown(1, 5, disnake.BucketType.user),
            )
    @commands.is_owner()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def shutdown(self, inter: disnake.CommandInter) -> None:
        """Shutdown the bot."""
        
        embed = core.TypicalEmbed(
            inter=inter,
            title='Shutdown the bot?',
            description='Are you sure you want to shut down the bot?',
            disabled_footer=True
        )
        
        view=ShutdownCommandView(inter,timeout=15)
        await inter.send(embed=embed,view=view)
        


def setup(bot: core.IgKnite) -> None:
    bot.add_cog(Admin(bot))
