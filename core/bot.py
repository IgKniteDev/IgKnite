# SPDX-License-Identifier: MIT


# Imports.
import asyncio
from typing import Optional, Set

import disnake
from disnake.ext import commands

from cogs import EXTENTIONS
from core.chain import keychain


# Set up a custom class for core functionality.
class IgKnite(commands.AutoShardedBot):
    """
    A subclassed version of `commands.AutoShardedBot`.\n
    Basically works as the core class for all-things IgKnite!
    """

    def __init__(
        self, *args, ignored_extensions: Optional[Set[str]] = None, **kwargs
    ) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or('.'),
            strip_after_prefix=True,
            case_insensitive=True,
            # owner_ids={}, # provide this if you dont want a api call to fetch the owner
            *args,
            **kwargs,
        )

        to_load = EXTENTIONS
        if ignored_extensions is not None:
            # ignored_extensions need's to be a set, can add a check
            # but not worth it since these are gonna be passed by a
            # developer
            to_load -= ignored_extensions

        for extension in to_load:
            self.load_extension(extension)

    async def _update_presence(self) -> None:
        """
        Updates the rich presence of IgKnite.
        """

        await self.change_presence(
            status=disnake.Status.dnd,
            activity=disnake.Activity(
                type=disnake.ActivityType.listening,
                name=f'slashes inside {len(self.guilds)} server(s)!',
            ),
        )

    async def on_connect(self) -> None:
        print(f'\nConnected to Discord as {self.user}.')

    async def on_ready(self) -> None:
        print(
            f'Inside {len(self.guilds)} server(s) with {self.shard_count} shard(s) active.'
        )
        await self._update_presence()

    async def on_guild_join(self, _: disnake.Guild) -> None:
        await self._update_presence()

    async def on_guild_remove(self, _: disnake.Guild) -> None:
        await self._update_presence()

    async def on_message_delete(self, message: disnake.Message) -> None:
        keychain.snipeables.append(message)
        await asyncio.sleep(25)
        keychain.snipeables.remove(message)
