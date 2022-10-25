'''
The `Inspection` cog for IgKnite.
---

License can be found here:
https://github.com/IgKniteDev/IgKnite/blob/main/LICENSE
'''


# Imports.
import math
from time import mktime
from datetime import datetime
from typing import List, Tuple

import disnake
from disnake import Option, OptionType, Invite
from disnake.ext import commands
from disnake.utils import MISSING

import core
from core.datacls import LockRoles


# View for the `invites` command.
class InviteCommandView(disnake.ui.View):
    def __init__(
        self,
        page_loader,
        top_page: int = 1,
        page: int = 1,
        timeout: float = 60,
    ) -> None:
        super().__init__(timeout=timeout)

        self.page_loader = page_loader
        self.top_page = top_page
        self.page = page

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
        label='Previous',
        style=disnake.ButtonStyle.gray,
        disabled=True,
    )
    async def previous(
        self, _: disnake.ui.Button, inter: disnake.MessageInteraction
    ) -> None:
        self.page -= 1
        self.paginator_logic()

        embed = await self.page_loader(self.page)
        await inter.response.edit_message(
            embed=embed,
            view=self,
        )

    @disnake.ui.button(label='Next', style=disnake.ButtonStyle.gray)
    async def next(
        self, _: disnake.ui.Button, inter: disnake.MessageInteraction
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
    def __init__(self, bot: core.IgKnite) -> None:
        self.bot = bot

    # guildinfo
    @commands.slash_command(
        name='guildinfo',
        description='Shows all important information about the server.',
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _guildinfo(self, inter: disnake.CommandInteraction) -> None:
        embed = (
            core.TypicalEmbed(inter)
            .add_field(
                name='Birth',
                value=datetime.strptime(
                    str(inter.guild.created_at), '%Y-%m-%d %H:%M:%S.%f%z'
                ).strftime('%b %d, %Y'),
            )
            .add_field(name='Owner', value=inter.guild.owner.mention)
            .add_field(name='Members', value=inter.guild.member_count)
            .add_field(name='Roles', value=len(inter.guild.roles))
            .add_field(
                name='Channels',
                value=len(inter.guild.text_channels) + len(inter.guild.voice_channels),
            )
            .add_field(name='Identifier', value=inter.guild_id)
        )

        if inter.guild.icon:
            embed.set_image(url=inter.guild.icon)

        await inter.send(embed=embed)

    # Backend for userinfo-labelled commands.
    # Do not use it within other commands unless really necessary.
    async def _userinfo_backend(
        self, inter: disnake.CommandInteraction, member: disnake.Member = None
    ) -> None:
        member = inter.author if not member else member

        embed = (
            core.TypicalEmbed(inter)
            .set_title(value=str(member))
            .add_field(name='Status', value=member.status)
            .add_field(
                name='Birth',
                value=datetime.strptime(
                    str(member.created_at), '%Y-%m-%d %H:%M:%S.%f%z'
                ).strftime('%b %d, %Y'),
            )
            .add_field(name='On Mobile', value=member.is_on_mobile())
            .add_field(name='Race', value="Bot" if member.bot else "Human")
            .add_field(name='Roles', value=len(member.roles))
            .add_field(name='Position', value=member.top_role.mention)
            .add_field(name='Identifier', value=member.id)
            .set_thumbnail(url=member.display_avatar)
        )
        await inter.send(embed=embed)

    # userinfo (slash)
    @commands.slash_command(
        name='userinfo',
        description='Shows all important information on a user.',
        options=[Option('member', 'Mention the server member.', OptionType.user)],
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _userinfo(
        self, inter: disnake.CommandInteraction, member: disnake.Member = None
    ) -> None:
        await self._userinfo_backend(inter, member)

    # userinfo (user)
    @commands.user_command(name='Show User Information', dm_permission=False)
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _userinfo_user(
        self, inter: disnake.CommandInteraction, member: disnake.Member
    ) -> None:
        await self._userinfo_backend(inter, member)

    # roleinfo
    @commands.slash_command(
        name='roleinfo',
        description='Shows all important information related to a specific role.',
        options=[Option('role', 'Mention the role.', OptionType.role, required=True)],
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _roleinfo(
        self, inter: disnake.CommandInteraction, role: disnake.Role
    ) -> None:
        embed = (
            core.TypicalEmbed(inter)
            .set_title(value=f'Role information: @{role.name}')
            .add_field(
                name='Birth',
                value=datetime.strptime(
                    str(role.created_at), '%Y-%m-%d %H:%M:%S.%f%z'
                ).strftime('%b %d, %Y'),
            )
            .add_field(name='Mentionable', value=role.mentionable)
            .add_field(name='Managed By Integration', value=role.managed)
            .add_field(name='Managed By Bot', value=role.is_bot_managed())
            .add_field(name='Role Position', value=role.position)
            .add_field(name='Identifier', value=f'`{role.id}`')
        )

        await inter.send(embed=embed)

    # invites
    @commands.slash_command(
        name='invites',
        description='Displays active server invites.',
        dm_permission=False,
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

        async def page_loader(page_num: int) -> Tuple[core.TypicalEmbed, List[Invite]]:
            page = page_num

            embed = (
                core.TypicalEmbed(inter)
                .set_title(value='Invites')
                .set_description(value='List of all invites within the server:')
            )
            if invites:
                embed.set_footer(text=f'{page}/{top_page}')
            else:
                embed.set_description('There are no invites to this server yet.')

            for i in range(
                (page_num * invites_per_page) - invites_per_page,
                page_num * invites_per_page,
            ):
                if i < len(invites):
                    if not invites[i].max_age:
                        max_age = 'never'
                    else:
                        date_time = datetime.fromtimestamp(
                            mktime(invites[i].expires_at.timetuple())
                        )
                        max_age = f'<t:{int(mktime(date_time.timetuple()))}:R>'

                    embed.add_field(
                        name=f'{i + 1} - `{invites[i].code}`',
                        value=f'🧍{invites[i].inviter.name}'
                        f' **|** 🚪 {invites[i].uses}'
                        f' **|** 🕑 {max_age} \n\n',
                        inline=False,
                    )

            return embed

        embed = await page_loader(page)
        await inter.send(
            embed=embed,
            view=InviteCommandView(
                page_loader=page_loader,
                top_page=top_page,
                page=page,
            )
            if invites
            else MISSING,
        )

    # revokeinvites
    @commands.slash_command(
        name='revokeinvites',
        description='Revokes invites. By default this removes all invites but you can choose a server member.',
        options=[Option('member', 'Mention the server member.', OptionType.user)],
    )
    async def _revokeinvites(
        self, inter: disnake.CommandInteraction, member: disnake.Member | None = None
    ) -> None:
        deletion_count = 0

        await inter.response.defer()
        for invite in await inter.guild.invites():
            if (member and invite.inviter == member) or (not member):
                await invite.delete()
                deletion_count += 1
            else:
                pass

        if member:
            await inter.send(
                f'Revoked {deletion_count} invites made by {member.mention}.',
                ephemeral=True,
            )
        else:
            await inter.send(f'Revoked {deletion_count} invites.', ephemeral=True)

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
                max_value=100,
            )
        ],
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _audit(self, inter: disnake.CommandInteraction, limit: int = 5):
        embed = core.TypicalEmbed(inter).set_title(value=f'Audit Log ({limit} entries)')
        async for audit_entry in inter.guild.audit_logs(limit=limit):
            embed.add_field(
                name=f'- {audit_entry.action}',
                value=f'User: {audit_entry.user} | Target: {audit_entry.target}',
                inline=False,
            )

        await inter.send(embed=embed, ephemeral=True)

    # show member count in VC
    @commands.slash_command(
        name='membercount',
        description='Shows the current member count in the server.',
        options=[
            Option(
                'sticky',
                'Set True to show member count in side bar.',
                OptionType.boolean,
            )
        ],
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _membercount(
        self, inter: disnake.CommandInteraction, sticky: bool = False
    ) -> None:
        embed = (
            core.TypicalEmbed(inter)
            .set_title(value='Member Count')
            .set_description(
                value=f'There are currently {len(inter.guild.members)} members in the server.'
            )
        )

        for channel in inter.guild.channels:
            if channel.name.startswith('Members:'):
                await channel.delete()

        if sticky:
            await inter.guild.create_voice_channel(
                name=f'Members: {inter.guild.member_count}',
                position=0,
                overwrites={
                    inter.guild.default_role: disnake.PermissionOverwrite(connect=False),
                    inter.guild.me: disnake.PermissionOverwrite(manage_channels=True, connect=False),
                }
            )
            embed.set_footer(text='Sticky mode enabled.')
            await inter.send(embed=embed)

        else:
            await inter.send(embed=embed)


# The setup() function for the cog.
def setup(bot: core.IgKnite) -> None:
    bot.add_cog(Inspection(bot))
