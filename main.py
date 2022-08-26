'''
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
import logging

import discord
from discord.ext import commands

from core import IgKnite, global_


# Initialize the global variables from core.global_ .
global_.initialize()


# The main() coroutine.
async def main() -> None:
    logger = logging.getLogger('discord')
    handler = logging.handlers.RotatingFileHandler(
        filename='discord.log',
        encoding='utf-8',
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=3,  # Rotate through 5 files
    )

    datetime_format = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', datetime_format, style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    async with IgKnite(
        command_prefix=commands.when_mentioned,
        intents=discord.Intents.all(),
        initial_extensions=[
            'cogs.general',
            'cogs.inspection',
            'cogs.moderation'
        ]
    ) as bot:
        await bot.run(global_.tokens['discord'])


# Run.
asyncio.run(main())
