'''
The brain of IgKnite!
---

License can be found here:
https://github.com/IgKniteDev/IgKnite/blob/main/LICENSE
'''


# Imports.
import asyncio
from typing import List

import disnake
from disnake.ext import commands, tasks

from core import global_


# Set up a custom class for core functionality.
class IgKnite(commands.AutoShardedInteractionBot):
    '''
    A subclassed version of `commands.AutoShardedInteractionBot`.\n
    Basically works as the core class for all-things IgKnite!
    '''

    def __init__(self, *args, initial_extensions: List[str], **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.task_update_presence.start()

        for extension in initial_extensions:
            self.load_extension(extension)

    async def on_connect(self) -> None:
        print(f'\nConnected to Discord as {self.user}.')

    async def on_ready(self) -> None:
        print(f'Inside {len(self.guilds)} server(s) with {self.shard_count} shard(s) active.')

    @tasks.loop(seconds=200)
    async def task_update_presence(self) -> None:
        await self.change_presence(
            status=disnake.Status.dnd,
            activity=disnake.Activity(
                type=disnake.ActivityType.listening,
                name=f'slashes inside {len(self.guilds)} server(s)!',
            ),
        )

    @task_update_presence.before_loop
    async def task_before_updating_presence(self) -> None:
        await self.wait_until_ready()

    async def on_message(self, message: disnake.Message) -> None:
        if message.author == self.user:
            return

    async def on_message_delete(self, message: disnake.Message) -> None:
        global_.snipeables.append(message)
        await asyncio.sleep(25)
        global_.snipeables.remove(message)
