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


# Backend for ping-labelled commands.
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
    ).add_field(
        name='Patch Version',
        value=core.BOT_METADATA['VERSION'],
        inline=False
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

    async def on_timeout(self) -> None:
        for children in self.children:
            children.disabled = True

        await self.inter.edit_original_message(view=self)


# The actual cog.
class General(commands.Cog):
    def __init__(
        self,
        bot: core.IgKnite
    ) -> None:
        self.bot = bot

    # Backend for avatar-labelled commands.
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

    # avatar (slash)
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
        description='Get to know IgKnite!'
    )
    async def help(inter):
        embed = core.TypicalEmbed(
            inter=inter,
            disabled_footer=True
        ).set_title(
            value='Hey there! I\'m IgKnite.'
        ).set_description(
            value='I\'m a bot with no text commands (you heard that right) and I\'m here to help you manage and moderate your Discord server alongside having a midnight music party with your friends in a random voice channel. Looking forward to being friends with you!'
        )

        view = core.SmallView(inter).add_button(
            label='GitHub',
            url=core.BOT_METADATA['REPOSITORY']
        ).add_button(
            label='Documentation',
            url=core.BOT_METADATA['DOCUMENTATION']
        )

        await inter.send(embed=embed, view=view)


# The setup() function for the cog.
def setup(bot: core.IgKnite) -> None:
    bot.add_cog(General(bot))
