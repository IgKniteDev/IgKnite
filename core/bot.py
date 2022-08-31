'''
The brain of IgKnite!
---

MIT License

Copyright (c) 2022 IgKnite

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


# Imports.
import asyncio
from typing import List

import discord
from discord import app_commands
from discord.ext import commands, tasks

import core
from core import global_


# Subclassing discord.app_commands.CommandTree for exception handling and stuff.
class IgKniteTree(app_commands.CommandTree):
    '''
    A subclassed version of `discord.app_commands.CommandTree`.\n
    This class allows execution of global exception handlers and application commands.
    '''

    async def on_error(
        self,
        inter: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        embed = core.TypicalEmbed(inter, is_error=True)
        error = getattr(error, 'original', error)

        if isinstance(error, app_commands.errors.MissingAnyRole):
            embed.title = 'Whoops! You don\'t have the roles.'
        else:
            embed.title = 'Whoops! An alien error occured.'

        embed.description = str(error)

        if inter.response.is_done():
            await inter.followup.send(embed=embed)
        else:
            await inter.response.send_message(embed=embed)


# Set up a custom class for core functionality.
class IgKnite(commands.AutoShardedBot):
    '''
    A subclassed version of `discord.AutoShardedBot`.\n
    Basically works as the core class for all-things IgKnite!
    '''

    def __init__(
        self,
        *args,
        initial_extensions: List[str],
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.initial_extensions = initial_extensions

    async def setup_hook(self) -> None:
        for extension in self.initial_extensions:
            await self.load_extension(extension)

        await self.tree.sync()
        self.task_update_presence.start()

    async def on_connect(self) -> None:
        print(f'\nConnected to Discord as {self.user}.')

    async def on_ready(self) -> None:
        print(f'Inside {len(self.guilds)} server(s) with {self.shard_count} shard(s) active.')

    @tasks.loop(seconds=200)
    async def task_update_presence(self) -> None:
        await self.change_presence(
            status=discord.Status.dnd,
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name=f'slashes inside {len(self.guilds)} server(s)!'
            )
        )

    @task_update_presence.before_loop
    async def task_before_updating_presence(self) -> None:
        await self.wait_until_ready()

    async def on_message(
        self,
        message: discord.Message
    ) -> None:
        if message.author == self.user:
            return

    async def on_message_delete(
        self,
        message: discord.Message
    ) -> None:
        global_.snipeables.append(message)
        await asyncio.sleep(25)
        global_.snipeables.remove(message)
