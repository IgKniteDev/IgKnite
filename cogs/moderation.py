'''
The `Moderation` cog for IgKnite.
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
from core import global_
from core.datacls import LockRoles


# The actual cog.
class Moderation(commands.Cog):
    def __init__(self, bot: core.IgKnite) -> None:
        self.bot = bot

    # ban
    @app_commands.command(
        name='ban',
        description='Bans a member from the server.'
    )
    @app_commands.describe(
        member='Mention the server member.'
    )
    @app_commands.guild_only()
    @app_commands.checks.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _ban(
        self,
        inter: discord.Interaction,
        member: discord.Member,
        reason: str = 'No reason provided.'
    ) -> None:
        await inter.guild.ban(member, reason=reason)
        await inter.response.send_message(f'Member **{member.display_name}** has been banned! Reason: {reason}')

    # softban
    @app_commands.command(
        name='softban',
        description='Temporarily bans members to delete their messages.'
    )
    @app_commands.describe(
        member='Mention the server member.',
        reason='Reason for the ban.'
    )
    @app_commands.guild_only()
    @app_commands.checks.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _softban(
        self,
        inter: discord.Interaction,
        member: discord.Member,
        *,
        reason: str = 'No reason provided.'
    ):
        await inter.guild.ban(member, delete_message_days=7, reason=reason)
        await inter.guild.unban(member)
        await inter.response.send_message(f'Member **{member.display_name}** has been softbanned! Reason: {reason}')

    # kick
    @app_commands.command(
        name='kick',
        description='Kicks a member from the server.'
    )
    @app_commands.describe(
        member='Mention the server member.',
        reason='Reason for the kick.'
    )
    @app_commands.guild_only()
    @app_commands.checks.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _kick(
        self,
        inter: discord.Interaction,
        member: discord.Member,
        reason: str = 'No reason provided.'
    ) -> None:
        await inter.guild.kick(member, reason=reason)
        await inter.response.send_message(f'Member **{member.display_name}** has been kicked! Reason: {reason}')

    # timeout
    @app_commands.command(
        name='timeout',
        description='Timeouts a member.'
    )
    @app_commands.describe(
        member='Mention the server member.',
        duration='The duration of the timeout.',
        reason='Reason for the timeout.'
    )
    @app_commands.guild_only()
    @app_commands.checks.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _deafen(
        self,
        inter: discord.Interaction,
        member: discord.Member,
        duration: int = 30,
        *,
        reason: str = 'No reason provided.'
    ) -> None:
        await member.timeout(duration=duration, reason=reason)
        await inter.response.send_message(f'Member **{member.display_name}** has been timed out! Reason: {reason}')

    # unban
    @app_commands.command(
        name='unban',
        description='Unbans a member from the server.'
    )
    @app_commands.describe(
        member='Mention the server member.'
    )
    @app_commands.guild_only()
    @app_commands.checks.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _unban(
        self,
        inter: discord.Interaction,
        member: discord.Member
    ) -> None:
        await inter.guild.unban(member)
        await inter.response.send_message(f'Member **{member.display_name}** has been unbanned!')

    # purge
    @app_commands.command(
        name='purge',
        description='Clears messages within the given index.'
    )
    @app_commands.describe(
        amount='The amount of messages to purge. Default is 2.'
    )
    @app_commands.guild_only()
    @app_commands.checks.has_any_role(LockRoles.mod, LockRoles.admin)
    @core.decor.long_running_command
    async def _purge(
        self,
        inter: discord.Interaction,
        amount: int = 2  # 1 + 1
    ) -> None:
        await inter.channel.purge(limit=amount)

    # purgeone
    @app_commands.command(
        name='purgeone',
        description='Purges a message by its identifier.'
    )
    @app_commands.describe(
        id='The ID of the message.'
    )
    @app_commands.guild_only()
    @app_commands.checks.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _purgeone(
        self,
        inter: discord.Interaction,
        id: str
    ) -> None:
        await (
            await inter.channel.fetch_message(int(id))
        ).delete()
        await inter.response.send_message('Message has been purged!', ephemeral=True)

    # ripplepurge
    @app_commands.command(
        name='ripplepurge',
        description='Clears messages that are sent by a specific user within the given index.'
    )
    @app_commands.describe(
        member='Mention the server member.',
        amount='The amount of messages to purge. Default is 10.'
    )
    @app_commands.guild_only()
    @app_commands.checks.has_any_role(LockRoles.mod, LockRoles.admin)
    @core.decor.long_running_command
    async def _ripplepurge(
        self,
        inter: discord.Interaction,
        member: discord.Member,
        amount: int = 10
    ) -> None:
        messages = []

        async for msg in inter.channel.history():
            if len(messages) == amount:
                break

            if msg.author == member:
                messages.append(msg)

        await inter.channel.delete_messages(messages)
        await inter.followup.send(
            f'Purged {len(messages)} messages that were sent by **{member}.**',
            ephemeral=True
        )

    # snipe
    @app_commands.command(
        name='snipe',
        description='Snipes messages within 25 seconds of getting deleted.'
    )
    @app_commands.guild_only()
    @app_commands.checks.has_any_role(LockRoles.mod, LockRoles.admin)
    @core.decor.long_running_command
    async def _snipe(
        self, 
        inter: discord.Interaction
    ) -> None:
        webhook: discord.Webhook = None
        sniped_count: int = 0

        if global_.snipeables:
            for snipeable in global_.snipeables:
                if snipeable.guild == inter.guild:
                    if (
                        webhook
                        and webhook.name == snipeable.author.display_name
                    ):
                        pass

                    else:
                        webhook = await inter.channel.create_webhook(name=snipeable.author.display_name)

                    await webhook.send(
                        content=snipeable.content,
                        username=snipeable.author.name,
                        avatar_url=snipeable.author.avatar
                    )
                    sniped_count += 1

            await webhook.delete()
            await inter.followup.send(f'Sniped **{sniped_count}** messages.', ephemeral=True)

        else:
            await inter.followup.send('No messages were found in my list.', ephemeral=True)


# The setup() function for the cog.
async def setup(bot: core.IgKnite) -> None:
    await bot.add_cog(Moderation(bot))
