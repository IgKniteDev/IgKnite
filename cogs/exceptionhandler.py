'''
The `ExceptionHandler` cog for IgKnite.
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
import discord
from discord import app_commands
from discord.ext import commands

import core


# The actual cog.
class ExceptionHandler(commands.Cog):
    def __init__(self, bot: core.IgKnite):
        self.bot = bot
        self.bot.tree.error(self.on_error)

    async def on_error(self, inter: discord.Interaction, error: app_commands.AppCommandError):
        embed = core.embeds.ErrorEmbed(inter)
        embed.title = 'Whoops!'

        error = getattr(error, 'original', error)
        embed.description = str(error)

        await inter.response.send_message(embed=embed)


# The setup() function for the cog.
async def setup(bot: core.IgKnite) -> None:
    await bot.add_cog(ExceptionHandler(bot))
