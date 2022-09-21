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
from core.datacls import LockRoles


# The actual cog.
class Inspection(commands.Cog):
    def __init__(
        self,
        bot: core.IgKnite
    ) -> None:
        self.bot = bot

    # guildinfo
    @commands.slash_command(
        name='guildinfo',
        description='Shows all important information about the server.',
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _guildinfo(
        self,
        inter: disnake.CommandInteraction
    ) -> None:
        embed = core.TypicalEmbed(inter).add_field(
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

    # Backend for userinfo-labelled commands.
    # Do not use it within other commands unless really necessary.
    async def _userinfo_backend(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member = None
    ) -> None:
        member = inter.author if not member else member

        embed = core.TypicalEmbed(inter).set_title(
            value=str(member)
        ).add_field(
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
            value=member.top_role.mention
        ).add_field(
            name='Identifier',
            value=member.id
        ).set_thumbnail(
            url=member.display_avatar
        )
        await inter.send(embed=embed)

    # userinfo (slash)
    @commands.slash_command(
        name='userinfo',
        description='Shows all important information on a user.',
        options=[
            Option(
                'member',
                'Mention the server member.',
                OptionType.user
            )
        ],
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _userinfo(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member = None
    ) -> None:
        await self._userinfo_backend(inter, member)

    # userinfo (user)
    @commands.user_command(
        name='Show User Information',
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _userinfo_user(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member
    ) -> None:
        await self._userinfo_backend(inter, member)

    # roleinfo
    @commands.slash_command(
        name='roleinfo',
        description='Shows all important information related to a specific role.',
        options=[
            Option(
                'role',
                'Mention the role.',
                OptionType.role,
                required=True
            )
        ],
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _roleinfo(
        self,
        inter: disnake.CommandInteraction,
        role: disnake.Role
    ) -> None:
        embed = core.TypicalEmbed(inter).set_title(
            value=f'Role information: @{role.name}'
        ).add_field(
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

        await inter.send(embed=embed)

    # audit
    @commands.slash_command(
        name='audit',
        description='Views the latest entries of the audit log in detail.',
        options=[
            Option(
                'limit',
                'The limit for showing entries. Must be within 1 and 100.',
                OptionType.integer
            )
        ],
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _audit(
        self,
        inter: disnake.CommandInteraction,
        limit: int = 5
    ):
        if limit not in range(1, 101):
            await inter.response.send_message(f'{limit} is not within the given range.', ephemeral=True)

        else:
            embed = core.TypicalEmbed(inter).set_title(
                value=f'Audit Log ({limit} entries)'
            )

            async for audit_entry in inter.guild.audit_logs(limit=limit):
                embed.add_field(
                    name=f'- {audit_entry.action}',
                    value=f'User: {audit_entry.user} | Target: {audit_entry.target}',
                    inline=False
                )

            await inter.send(embed=embed, ephemeral=True)


# The setup() function for the cog.
def setup(bot: core.IgKnite) -> None:
    bot.add_cog(Inspection(bot))
