'''
The `General` cog for IgKnite.
---

License can be found here:
https://github.com/IgKniteDev/IgKnite/blob/main/LICENSE
'''


# Imports.
import time
from datetime import datetime

import disnake
from disnake import Option, OptionType
from disnake.ext import commands

import core
from core import global_
from core.embeds import TypicalEmbed


# Backend for userinfo-labelled commands.
# Do not use it within other commands unless really necessary.
async def _ping_backend(inter: disnake.CommandInteraction) -> TypicalEmbed:
    system_latency = round(inter.bot.latency * 1000)

    start_time = time.time()
    await inter.response.defer()
    end_time = time.time()

    api_latency = round((end_time - start_time) * 1000)

    uptime = round(datetime.timestamp(datetime.now())) - global_.running_since
    h, m, s = uptime // 3600, uptime % 3600 // 60, uptime % 3600 % 60

    embed = core.TypicalEmbed(
        inter=inter,
        disabled_footer=True
    ).add_field(
        name='System Latency',
        value=f'{system_latency}ms [{inter.bot.shard_count} shard(s)]',
        inline=False
    ).add_field(
        name='API Latency',
        value=f'{api_latency}ms',
        inline=False
    ).add_field(
        name='Uptime',
        value=f'{h}h {m}m {s}s'
    )

    return embed


# View for the `ping` command.
class PingCommandView(disnake.ui.View):
    def __init__(
        self,
        inter: disnake.CommandInteraction,
        timeout: float = 60
    ) -> None:
        super().__init__(timeout=timeout)
        self.inter = inter

    @disnake.ui.button(label='Refresh', style=disnake.ButtonStyle.gray)
    async def _refresh(
        self,
        _: disnake.ui.Button,
        inter: disnake.Interaction
    ) -> None:
        embed = await _ping_backend(inter)
        await inter.edit_original_message(embed=embed, view=self)


# The actual cog.
class General(commands.Cog):
    def __init__(
        self,
        bot: core.IgKnite
    ) -> None:
        self.bot = bot

    # Backend for userinfo-labelled commands.
    # Do not use it within other commands unless really necessary.
    async def _avatar_backend(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member = None
    ) -> None:
        member = inter.author if not member else member

        embed = core.TypicalEmbed(inter).set_title(
            value='Here\'s what I found!'
        ).set_image(
            url=member.avatar
        )

        await inter.send(embed=embed)

    @commands.slash_command(
        name='avatar',
        description='Displays your avatar / the avatar of a server member.',
        options=[
            Option(
                'member',
                'Mention the server member.',
                OptionType.user
            )
        ],
        dm_permission=False
    )
    async def _avatar(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member = None
    ) -> None:
        await self._avatar_backend(inter, member)

    # avatar (user)
    @commands.user_command(
        name='Show Avatar'
    )
    async def _avatar_user(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member
    ) -> None:
        await self._avatar_backend(inter, member)

    # ping
    @commands.slash_command(
        name='ping',
        description='Shows my current response time.'
    )
    async def _ping(
        self,
        inter: disnake.CommandInteraction
    ) -> None:
        embed = await _ping_backend(inter)
        await inter.send(embed=embed, view=PingCommandView(inter=inter))

    # help
    @commands.slash_command(
        name='help',
        description='Get started with IgKnite!'
    )
    async def _help(
        self,
        inter: disnake.CommandInteraction
    ) -> None:
        embed = core.TypicalEmbed(inter).set_title(
            value='Get started with IgKnite!'
        ).add_field(
            name='What is this?',
            value='IgKnite is an open-source Discord bot for moderation and music.',
            inline=False
        ).add_field(
            name='Where can I find the commands?',
            value='You can find them by typing `/` in any server.',
            inline=False
        ).add_field(
            name='Where can I find the source code?',
            value='You can find it [here](https://github.com/IgKniteDev/IgKnite).',
            inline=False
        ).add_field(
            name='Where can I find the documentation?',
            value='You can find it [here](https://igknition.ml/docs/reference.html).',
            inline=False
        )

        await inter.send(embed=embed)


# The setup() function for the cog.
def setup(bot: core.IgKnite) -> None:
    bot.add_cog(General(bot))
