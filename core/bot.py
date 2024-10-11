# SPDX-License-Identifier: MIT


# Imports.
import asyncio
from typing import Optional, Set

import disnake
from disnake.ext import commands

import logging

from cogs import EXTENTIONS
from core.chain import keychain

#setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("core")

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
        logger.info("[+]=======Starting IgKnite=======")

        to_load = EXTENTIONS
        if ignored_extensions is not None:
            # ignored_extensions need's to be a set, can add a check
            # but not worth it since these are gonna be passed by a
            # developer
            to_load -= ignored_extensions
        
        logger.info(f"Selected cogs to load: {", ".join(to_load)}")

        for extension in to_load:
            try:
                self.load_extension(extension)
                logger.info(f"[+]Loaded {extension} successfully")
            except Exception as e:
                logger.error(f"[-]Failed to load extension {extension}")
                logger.error(e)

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
        logger.info(f'[+]Connected to Discord as {self.user}!')

    async def on_ready(self) -> None:
        logger.info(
            f'[+]Inside {len(self.guilds)} server(s) with {self.shard_count} shard(s) active.'
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
