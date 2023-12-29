# SPDX-License-Identifier: MIT


# Imports.
import time
from datetime import datetime

import disnake
from disnake.ext import commands
from disnake.ext.commands import Param

import core


# Common backend for ping-labelled commands.
# Do not use it within other commands unless really necessary.
async def _ping_backend(inter: disnake.CommandInter) -> core.TypicalEmbed:
    system_latency = round(inter.bot.latency * 1000)

    start_time = time.time()
    await inter.response.defer()
    end_time = time.time()

    api_latency = round((end_time - start_time) * 1000)

    uptime = round(datetime.timestamp(datetime.now())) - core.BotData.running_since
    h, m, s = uptime // 3600, uptime % 3600 // 60, uptime % 3600 % 60

    embed = (
        core.TypicalEmbed(inter=inter, disabled_footer=True)
        .add_field(
            name='System Latency',
            value=f'{system_latency}ms [{inter.bot.shard_count} shard(s)]',
            inline=False,
        )
        .add_field(name='API Latency', value=f'{api_latency}ms', inline=False)
        .add_field(name='Uptime', value=f'{h}h {m}m {s}s')
        .add_field(name='Patch Version', value=core.BotData.version, inline=False)
    )

    return embed


# View for the `ping` command.
class PingCommandView(disnake.ui.View):
    def __init__(self, inter: disnake.CommandInter, *, timeout: float = 60) -> None:
        super().__init__(timeout=timeout)
        self.inter = inter

    @disnake.ui.button(label='Refresh', style=disnake.ButtonStyle.gray)
    async def _refresh(self, _: disnake.ui.Button, inter: disnake.Interaction) -> None:
        embed = await _ping_backend(inter)
        await inter.edit_original_message(embed=embed, view=self)

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True

        await self.inter.edit_original_message(view=self)


# The actual cog.
class General(commands.Cog):
    def __init__(self, bot: core.IgKnite) -> None:
        self.bot = bot

    # Listener for the bookmark feature.
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: disnake.RawReactionActionEvent) -> None:
        if payload.emoji.name == '🔖':
            if payload.event_type == 'REACTION_ADD':
                chnl = self.bot.get_channel(payload.channel_id)
                msg = disnake.utils.get(await chnl.history(limit=5).flatten(), id=payload.message_id)
                embed = core.TypicalEmbed(
                    title='You\'ve bookmarked a message.',
                    description=msg.content
                    + f'\n\nSent by {msg.author.name} '
                    + f'on {payload.member.guild.name}',
                )
                view = core.SmallView().add_button(
                    label='Original Message', url=msg.jump_url
                )
                await payload.member.send(embed=embed, view=view)

    # Common backend for avatar-labelled commands.
    # Do not use it within other commands unless really necessary.
    async def _avatar_backend(
        self, inter: disnake.CommandInter, member: disnake.Member = None
    ) -> None:
        embed = core.TypicalEmbed(inter=inter, title='Here\'s what I found!').set_image(
            url=member.avatar
        )

        await inter.send(embed=embed)

    # avatar (slash)
    @commands.slash_command(
        name='avatar',
        description='Displays the avatar of a server member.',
        dm_permission=False,
    )
    async def _avatar(
        self,
        inter: disnake.CommandInter,
        member: disnake.Member = Param(
            description='Mention the server member. Defaults to you.',
            default=lambda inter: inter.author,
        ),
    ) -> None:
        await self._avatar_backend(inter, member)

    # avatar (user)
    @commands.user_command(name='Show Avatar', dm_permission=False)
    async def _avatar_user(self, inter: disnake.CommandInter, member: disnake.Member) -> None:
        await self._avatar_backend(inter, member)

    # ping
    @commands.slash_command(name='ping', description='Shows my current response time.')
    async def _ping(self, inter: disnake.CommandInter) -> None:
        embed = await _ping_backend(inter)
        await inter.send(embed=embed, view=PingCommandView(inter))

    # help
    @commands.slash_command(name='help', description='Get to know IgKnite!')
    async def help(self, inter: disnake.CommandInter):
        embed = core.TypicalEmbed(
            inter,
            title='Hey there! I\'m IgKnite.',
            description='I\'m a bot with no text commands (you heard that right) '
            + 'and I\'m here to help you manage and moderate your Discord server alongside '
            + 'having a midnight music party with your friends in a random voice channel. '
            + 'Looking forward to being friends with you!',
            disabled_footer=True,
        )

        view = (
            core.SmallView(inter)
            .add_button(label='GitHub', url=core.BotData.repo)
            .add_button(label='Documentation', url=core.BotData.documentation)
        )

        await inter.send(embed=embed, view=view)


# The setup() function for the cog.
def setup(bot: core.IgKnite) -> None:
    bot.add_cog(General(bot))
