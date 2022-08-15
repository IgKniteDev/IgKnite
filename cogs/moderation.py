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
import disnake
from disnake import Option, OptionType
from disnake.ext import commands

import core
from core.dataclasses import LockRoles


# The actual cog.
class Moderation(commands.Cog):
    def __init__(self, bot: core.IgKnite) -> None:
        self.bot = bot

    @commands.slash_command(
        name='ban',
        description='Bans a member from the server.',
        options=[
            Option('member', 'Mention the server member.', OptionType.user, required=True),
            Option('reason', 'Reason for the ban.', OptionType.string)
        ],
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _ban(self, inter: disnake.CommandInter, member: disnake.Member,
                   reason: str = "No reason provided.") -> None:
        await inter.guild.ban(member, reason=reason)
        await inter.send(f'Member **{member.display_name}** has been banned! Reason: {reason}')

    @commands.slash_command(
        name='kick',
        description='Kicks a member from the server.',
        options=[
            Option('member', 'Mention the server member.', OptionType.user, required=True),
            Option('reason', 'Reason for the kick.', OptionType.string)
        ],
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _kick(self, inter: disnake.CommandInter, member: disnake.Member,
                    reason: str = "No reason provided.") -> None:
        await inter.guild.kick(member, reason=reason)
        await inter.send(f'Member **{member.display_name}** has been kicked! Reason: {reason}')

    @commands.slash_command(
        name='unban',
        description='Unbans a member from the server.',
        options=[
            Option('member', 'Mention the server member.', OptionType.user, required=True)
        ],
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _unban(self, inter: disnake.CommandInter, member: disnake.Member) -> None:
        await inter.guild.unban(member)
        await inter.send(f'Member **{member.display_name}** has been unbanned!')

    @commands.slash_command(
        name='purge',
        description='Clears messages within the given index.',
        options=[
            Option('amount', 'Specify the amount. Default is 1.', OptionType.integer)
        ],
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _purge(self, inter: disnake.CommandInter, amount: int = 1) -> None:
        await inter.channel.purge(limit=amount)
        await inter.send(f'Purged {amount} messages!', ephemeral=True)

    @commands.slash_command(
        name='purgeone',
        description='Purges a message by its identifier.',
        options=[
            Option('id', 'Identifier of the message.', OptionType.string, required=True)
        ],
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _purgeone(self, inter: disnake.CommandInter, id: str) -> None:
        await (
            await inter.channel.fetch_message(int(id))
        ).delete()
        await inter.send("Message has been purged!", ephemeral=True)

    @commands.slash_command(
        name='ripplepurge',
        description='Clears messages that are sent by a specific user within the given index.',
        options=[
            Option('member', 'Mention the server member.', OptionType.user, required=True),
            Option('amount', 'Specify the amount. Default is 1.', OptionType.integer)
        ],
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _ripplepurge(self, inter: disnake.CommandInter, member: disnake.Member, amount: int = 1) -> None:
        messages = []
        async for msg in inter.channel.history():
            if len(messages) == amount:
                break
            if msg.author == member:
                messages.append(msg)
        await inter.channel.delete_messages(messages)
        await inter.send(f'Purged {amount} messages from **{member.name}#{member.discriminator}**', ephemeral=True)


# The setup() function for the cog.
def setup(bot: core.IgKnite) -> None:
    bot.add_cog(Moderation(bot))
