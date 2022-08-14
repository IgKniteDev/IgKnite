'''
The `Inspection` cog for IgKnite.
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
from datetime import datetime

import disnake
from disnake import Option, OptionType
from disnake.ext import commands

import core
from core.dataclasses import LockRoles


# The actual cog.
class Inspection(commands.Cog):
    def __init__(self, bot: core.bot.IgKnite) -> None:
        self.bot = bot

    @commands.slash_command(
        name='guildinfo',
        description='Shows all important information about the server.',
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _guildinfo(self, inter: disnake.CommandInter) -> None:
        embed = core.embeds.ClassicEmbed(inter).add_field(
            name='Birth',
            value=datetime.strptime(
                str(inter.guild.created_at), '%Y-%m-%d %H:%M:%S.%f%z'
            ).strftime('%b %d, %Y')
        ).add_field(
            name='Owner',
            value=inter.guild.owner.mention
        ).add_field(
            name='Members',
            value=inter.guild.member_count
        ).add_field(
            name='Roles',
            value=len(inter.guild.roles)
        ).add_field(
            name='Channels',
            value=len(inter.guild.text_channels) + len(inter.guild.voice_channels)
        ).add_field(
            name='Identifier',
            value=inter.guild_id
        )

        if inter.guild.icon:
            embed.set_thumbnail(url=inter.guild.icon)

        await inter.send(embed=embed)

    @commands.slash_command(
        name='userinfo',
        description='Shows all important information on a user.',
        options=[
            Option('member', 'Mention the server member.', OptionType.user)
        ],
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _userinfo(self, inter: disnake.CommandInter, member: disnake.Member = None) -> None:
        member = inter.author if not member else member

        embed = core.embeds.ClassicEmbed(inter).add_field(
            name='Status',
            value=member.status
        ).add_field(
            name='Birth',
            value=datetime.strptime(
                str(member.created_at), '%Y-%m-%d %H:%M:%S.%f%z'
            ).strftime('%b %d, %Y')
        ).add_field(
            name='On Mobile',
            value=member.is_on_mobile()
        ).add_field(
            name='Race',
            value="Bot" if member.bot else "Human"
        ).add_field(
            name='Roles',
            value=len(member.roles)
        ).add_field(
            name='Position',
            value=f"<@&{member.top_role.id}>"
        ).add_field(
            name='Identifier',
            value=member.id
        ).set_thumbnail(
            url=member.display_avatar
        )
        embed.title = member.display_name

        await inter.send(embed=embed)

    @commands.slash_command(
        name='roleinfo',
        description='Shows all important information related to a specific role.',
        options=[
            Option('role', 'Mention the role.', OptionType.role)
        ],
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _roleinfo(self, inter: disnake.CommandInter, role: disnake.Role) -> None:
        embed = core.embeds.ClassicEmbed(inter).add_field(
            name='Birth',
            value=datetime.strptime(
                str(role.created_at), '%Y-%m-%d %H:%M:%S.%f%z'
            ).strftime('%b %d, %Y')
        ).add_field(
            name='Mentionable',
            value=role.mentionable
        ).add_field(
            name='Managed By Integration',
            value=role.managed
        ).add_field(
            name='Managed By Bot',
            value=role.is_bot_managed()
        ).add_field(
            name='Role Position',
            value=role.position
        ).add_field(
            name='Identifier',
            value=f'`{role.id}`'
        )
        embed.title = f"Role Information: @{role.name}"

        await inter.send(embed=embed)


# The setup() function for the cog.
def setup(bot: core.bot.IgKnite) -> None:
    bot.add_cog(Inspection(bot))
