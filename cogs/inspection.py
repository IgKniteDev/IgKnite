'''
The `Inspection` cog for IgKnite.
---

License can be found here:
https://github.com/IgKniteDev/IgKnite/blob/main/LICENSE
'''


# Imports.
import math
from datetime import datetime
from time import mktime

import disnake
from disnake.ext import commands
from disnake.ext.commands import Param
from disnake.utils import MISSING

import core
from core.datacls import LockRoles


# View for the `invites` command.
class InviteCommandView(disnake.ui.View):
    def __init__(
        self,
        inter: disnake.CommandInteraction,
        *,
        page_loader,
        top_page: int = 1,
        page: int = 1,
        timeout: float = 60,
    ) -> None:
        super().__init__(timeout=timeout)
        self.inter = inter

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

    @disnake.ui.button(label='< Previous', style=disnake.ButtonStyle.gray, disabled=True)
    async def previous(self, _: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.page -= 1
        self.paginator_logic()

        embed = await self.page_loader(self.page)
        await inter.response.edit_message(
            embed=embed,
            view=self,
        )

    @disnake.ui.button(label='Next >', style=disnake.ButtonStyle.gray)
    async def next(self, _: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.page += 1
        self.paginator_logic()

        embed = await self.page_loader(self.page)
        await inter.response.edit_message(
            embed=embed,
            view=self,
        )

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True

        await self.inter.edit_original_message(view=self)


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

    # Common backend for userinfo-labelled commands.
    # Do not use it within other commands unless really necessary.
    async def _userinfo_backend(
        self, inter: disnake.CommandInteraction, member: disnake.Member
    ) -> None:
        embed = (
            core.TypicalEmbed(inter, title=str(member))
            .add_field(name='Status', value=member.status)
            .add_field(
                name='Birth',
                value=datetime.strptime(str(member.created_at), '%Y-%m-%d %H:%M:%S.%f%z').strftime(
                    '%b %d, %Y'
                ),
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
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _userinfo(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member = Param(
            description='Mention the server member. Defaults to you.',
            default=lambda inter: inter.author,
        ),
    ) -> None:
        await self._userinfo_backend(inter, member)

    # userinfo (user)
    @commands.user_command(name='Show User Information', dm_permission=False)
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _userinfo_user(
        self, inter: disnake.CommandInteraction, member: disnake.Member
    ) -> None:
        await self._userinfo_backend(inter, member)

    # userinfo (message)
    @commands.message_command(name='Show Author Information', dm_permission=False)
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _userinfo_message(
        self, inter: disnake.CommandInteraction, message: disnake.Message
    ) -> None:
        await self._userinfo_backend(inter, message.author)

    # roleinfo
    @commands.slash_command(
        name='roleinfo',
        description='Shows all important information related to a specific role.',
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _roleinfo(
        self,
        inter: disnake.CommandInteraction,
        role: disnake.Role = Param(description='Mention the role.', default=None),
    ) -> None:
        embed = (
            core.TypicalEmbed(inter, title=f'Role information: @{role.name}')
            .add_field(
                name='Birth',
                value=datetime.strptime(str(role.created_at), '%Y-%m-%d %H:%M:%S.%f%z').strftime(
                    '%b %d, %Y'
                ),
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
        await inter.response.defer(ephemeral=True)

        if len(invites := await inter.guild.invites()) == 0:
            return await inter.send('There are no invites to this server yet.')

        page = 1
        invites_per_page = 5
        top_page = math.ceil(len(invites) / invites_per_page)

        async def page_loader(page_num: int) -> core.TypicalEmbed:
            page = page_num
            embed = core.TypicalEmbed(inter, title='Active Invites').set_footer(
                text=f'{page}/{top_page}'
            )

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
                        value=f'🧍{invites[i].inviter.name} '
                        f' **|** 🚪 {invites[i].uses} '
                        f' **|** 🕑 {max_age} \n\n',
                        inline=False,
                    )

            return embed

        embed = await page_loader(page)
        await inter.send(
            embed=embed,
            view=InviteCommandView(
                inter,
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
        description='Revokes invites. '
        + 'By default this removes all invites but you can choose a server member.',
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _revokeinvites(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member = Param(
            description='Mention the server member. Defaults to all.', default=None
        ),
    ) -> None:
        deletion_count = 0
        await inter.response.defer(ephemeral=True)

        for invite in await inter.guild.invites():
            if (member and invite.inviter == member) or (not member):
                await invite.delete()
                deletion_count += 1
            else:
                pass

        if member:
            await inter.send(f'Revoked {deletion_count} invites made by {member.mention}.')
        else:
            await inter.send(f'Revoked {deletion_count} invites.')

    # audit
    @commands.slash_command(
        name='audit',
        description='Views the latest entries of the audit log in detail.',
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _audit(
        self,
        inter: disnake.CommandInteraction,
        limit: int = Param(
            description='The limit for showing audit log entries.',
            default=5,
            min_value=1,
            max_value=100,
        ),
    ):
        await inter.response.defer(ephemeral=True)

        embed = core.TypicalEmbed(inter, title=f'Audit Log ({limit} entries)')
        async for audit_entry in inter.guild.audit_logs(limit=limit):
            embed.add_field(
                name=f'- {audit_entry.action}',
                value=f'User: {audit_entry.user} | Target: {audit_entry.target}',
                inline=False,
            )

        await inter.send(embed=embed)


# The setup() function for the cog.
def setup(bot: core.IgKnite) -> None:
    bot.add_cog(Inspection(bot))
