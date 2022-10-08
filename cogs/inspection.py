'''
The `Inspection` cog for IgKnite.
---

License can be found here:
https://github.com/IgKniteDev/IgKnite/blob/main/LICENSE
'''


# Imports.
import math
from time import mktime
from typing import List
from datetime import datetime

import disnake
from disnake import Option, OptionType, Invite
from disnake.ext import commands
from disnake.utils import MISSING

import core
from core.datacls import LockRoles


# Selection menu for the `invites` command.
class InviteCommandSelect(disnake.ui.Select):
    def __init__(
        self,
        inter: disnake.CommandInteraction,
        invites: List[Invite]
    ) -> None:
        self.inter = inter
        self.invites = invites[0:25]

        options = []
        for i in range(len(self.invites)):
            options.append(
                disnake.SelectOption(
                    label=f'#{i + 1} - {invites[i].code}',
                    value=i,
                    description=invites[i].inviter.name
                )
            )

        super().__init__(
            options=options
        )

    async def callback(
        self,
        inter: disnake.MessageInteraction
    ) -> None:
        index = int(self.values[0])
        invite = self.invites[index]

        if invite.max_age == 0:
            max_age = 'never'
        else:
            date_time = datetime.fromtimestamp(mktime(invite.expires_at.timetuple()))
            max_age = f'<t:{int(mktime(date_time.timetuple()))}:R>'

        if invite.max_uses == 0:
            usage = f'{invite.uses} / ∞'
        else:
            usage = f'{invite.uses} / {invite.max_uses}'

        embed = core.TypicalEmbed(inter).set_title(
            value=f'Invite | `{invite.code}`'
        ).add_field(
            name='Inviter',
            value=invite.inviter
        ).add_field(
            name='Code',
            value=invite.code
        ).add_field(
            name='Link',
            value=f'https://discord.gg/{invite.code}'
        ).add_field(
            name='Expires',
            value=max_age
        ).add_field(
            name='Usage',
            value=usage
        )

        await inter.response.send_message(
            embed=embed,
            ephemeral=True
        )


# View for the `invites` command.
class InviteCommandView(disnake.ui.View):
    def __init__(
        self,
        inter: disnake.CommandInteraction,
        page_loader,
        top_page: int = 1,
        page: int = 1,
        invites: List[Invite] = [],
        timeout: float = 60
    ) -> None:
        super().__init__(timeout=timeout)

        self.page_loader = page_loader
        self.top_page = top_page
        self.page = page
        self.invites = []
        self.add_item(InviteCommandSelect(inter, invites))

        if self.page + 1 > self.top_page:
            self.children[1].disabled = True

    def paginator_logic(self) -> None:
        if self.page == 1:
            self.children[0].disabled = True
        else:
            self.children[0].disabled = False

        if self.page + 1 > self.top_page:
            self.children[1].disabled = True
        else:
            self.children[1].disabled = False

    @disnake.ui.button(
        label='Back',
        style=disnake.ButtonStyle.gray,
        disabled=True,
    )
    async def go_down(
        self,
        _: disnake.ui.Button,
        inter: disnake.MessageInteraction
    ) -> None:
        self.page -= 1
        self.paginator_logic()

        embed = await self.page_loader(self.page)
        await inter.response.edit_message(
            embed=embed,
            view=self,
        )

    @disnake.ui.button(
        label='Next',
        style=disnake.ButtonStyle.gray
    )
    async def go_up(
        self,
        _: disnake.ui.Button,
        inter: disnake.MessageInteraction
    ) -> None:
        self.page += 1
        self.paginator_logic()

        embed = await self.page_loader(self.page)
        await inter.response.edit_message(
            embed=embed,
            view=self,
        )


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

    # invites
    @commands.slash_command(
        name='invites',
        description='Displays active server invites.',
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _invites(
        self,
        inter: disnake.CommandInteraction,
    ) -> None:
        invites = await inter.guild.invites()
        page = 1

        invites_per_page = 5
        top_page = math.ceil(len(invites) / invites_per_page)

        async def load_page(page_num: int) -> core.TypicalEmbed:
            page = page_num

            embed = core.TypicalEmbed(inter).set_title(
                value='Invites'
            ).set_description(
                value='List of all invites within the server:'
            )
            if invites:
                embed.set_footer(text=f'{page}/{top_page}')
            else:
                embed.set_description("There are no invites to this server yet")

            for i in range(
                (page_num * invites_per_page) - invites_per_page,
                page_num * invites_per_page
            ):
                if i < len(invites):
                    if not invites[i].max_age:
                        max_age = 'never'
                    else:
                        date_time = datetime.fromtimestamp(mktime(invites[i].expires_at.timetuple()))
                        max_age = f'<t:{int(mktime(date_time.timetuple()))}:R>'

                    embed.add_field(
                        name=f'{i + 1} - `{invites[i].code}`',
                        value=f'🧍{invites[i].inviter.name}'
                              f' **|** 🚪 {invites[i].uses}'
                              f' **|** 🕑 {max_age} \n\n',
                        inline=False
                    )

            return embed

        embed = await load_page(page)
        await inter.send(
            embed=embed,
            view=InviteCommandView(
                inter, load_page, top_page,
                page, await inter.guild.invites()
            ) if invites else MISSING
        )

    # audit
    @commands.slash_command(
        name='audit',
        description='Views the latest entries of the audit log in detail.',
        options=[
            Option(
                'limit',
                'The limit for showing entries. Must be within 1 and 100.',
                OptionType.integer,
                min_value=1,
                max_value=100
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
