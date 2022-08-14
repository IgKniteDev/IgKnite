'''
The `General` cog for IgKnite.
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
import time

import disnake
from disnake import Option, OptionType
from disnake.ext import commands

import core


# The actual cog.
class General(commands.Cog):
    def __init__(self, bot: core.IgKnite) -> None:
        self.bot = bot

    @commands.slash_command(
        name='avatar',
        description='Displays the avatar / profile picture of a server member.',
        options=[
            Option('member', 'Mention the server member.', OptionType.user)
        ],
        dm_permission=False
    )
    async def _avatar(self, inter: disnake.CommandInter, member: disnake.Member = None) -> None:
        member = inter.author if not member else member

        embed = core.embeds.ClassicEmbed(inter).set_image(
            url=member.avatar
        )
        embed.title = 'Here\'s what I found!'

        await inter.send(embed=embed)

    @commands.slash_command(
        name='ping',
        description='Shows my current response time.',
    )
    async def _ping(self, inter: disnake.CommandInter) -> None:
        system_latency = round(self.bot.latency * 1000)

        start_time = time.time()
        await inter.response.defer()  # TODO: Might need to rethink the structure for this command.
        end_time = time.time()

        api_latency = round((end_time - start_time) * 1000)

        embed = core.embeds.ClassicEmbed(inter).add_field(
            name='System Latency',
            value=f'{system_latency}ms [{self.bot.shard_count} shard(s)]',
            inline=False
        ).add_field(
            name='API Latency',
            value=f'{api_latency}ms'
        )

        await inter.edit_original_message(content=None, embed=embed)


# The setup() function for the cog.
def setup(bot: core.IgKnite) -> None:
    bot.add_cog(General(bot))
