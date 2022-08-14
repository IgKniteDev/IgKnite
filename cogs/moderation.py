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
    def __init__(self, bot: core.bot.IgKnite) -> None:
        self.bot = bot

    @commands.slash_command(
        name='ban',
        description='Bans a member from server.',
        options=[
            Option('member', 'Mention the server member.', OptionType.user, required=True),
            Option('reason', 'Reason for the ban.', OptionType.string)
        ],
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _ban(self, inter: disnake.CommandInter, member: disnake.Member, reason: str = "No reason provided."):
        await inter.guild.ban(member, reason=reason)
        await inter.send(f'Member **{member.display_name}** has been banned! Reason: {reason}')

    @commands.slash_command(
        name='kick',
        description='Kicks a member from server.',
        options=[
            Option('member', 'Mention the server member.', OptionType.user, required=True),
            Option('reason', 'Reason for the kick.', OptionType.string)
        ],
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _kick(self, inter: disnake.CommandInter, member: disnake.Member, reason: str = "No reason provided."):
        await inter.guild.kick(member, reason=reason)
        await inter.send(f'Member **{member.display_name}** has been kicked! Reason: {reason}')

    @commands.slash_command(
        name='unban',
        description='Unbans a member from server.',
        options=[
            Option('member', 'Mention the server member.', OptionType.user, required=True)
        ],
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _unban(self, inter: disnake.CommandInter, member: disnake.Member):
        await inter.guild.unban(member)
        await inter.send(f'Member **{member.display_name}** has been unbanned!')


# The setup() function for the cog.
def setup(bot: core.bot.IgKnite) -> None:
    bot.add_cog(Moderation(bot))
