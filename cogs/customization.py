# SPDX-License-Identifier: MIT


# Imports.
import disnake
from disnake import ChannelType, OptionChoice
from disnake.ext import commands
from disnake.ext.commands import Param

import core
from core.datacls import LockRoles


# Hex to RGB converter.
def get_color(hex: str) -> disnake.Colour:
    hex = hex.lstrip('#')
    try:
        color = tuple(int(hex[i : i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return disnake.Colour.default()
    return disnake.Colour.from_rgb(*color)


# The actual cog.
class Customization(commands.Cog):
    def __init__(self, bot: core.IgKnite) -> None:
        self.bot = bot

    async def cog_before_slash_command_invoke(self, inter: disnake.CommandInteraction) -> None:
        return await inter.response.defer(ephemeral=True)

    # makerole
    @commands.slash_command(
        name='makerole',
        description='Create a new role.',
        dm_permission=False,
    )
    @commands.has_role(LockRoles.admin)
    async def _makerole(
        self,
        inter: disnake.CommandInteraction,
        name: str = Param(description='Give a name for the new role.'),
        color: str = Param(description='Give a color for the new role in Hex.', default='#000000'),
    ) -> None:
        color = get_color(color)
        await inter.guild.create_role(name=name, color=color)

        embed = core.TypicalEmbed(description=f'Role `{name}` has been created.')
        await inter.send(embed=embed)

    # assignrole
    @commands.slash_command(
        name='assignrole',
        description='Assign a role to a server member.',
        dm_permission=False,
    )
    @commands.has_role(LockRoles.admin)
    async def _assignrole(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member = Param(description='Mention the server member.'),
        role: disnake.Role = Param(description='Mention the role to assign to the user.'),
    ) -> None:
        await member.add_roles(role)
        await inter.send(f'Role {role.mention} has been assigned to **{member.display_name}**!')

    # removerole
    @commands.slash_command(
        name='deleterole',
        description='Delete a role from the server.',
        dm_permission=False,
    )
    @commands.has_role(LockRoles.admin)
    async def _removerole(
        self,
        inter: disnake.CommandInteraction,
        role: disnake.Role = Param(description='Mention the role to delete.'),
    ) -> None:
        await role.delete()
        await inter.send(f'Role **@{role.name}** has been removed!')

    # happy birthday to furti :cake:
    # edit: this is hitblast and here's your birthday gift commit :D

    # makeinvite
    @commands.slash_command(
        name='makeinvite',
        description='Create an invitation link to the server.',
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _makeinvite(
        self,
        inter: disnake.CommandInteraction,
        max_age: int = Param(
            description='Specify a lifetime for the invite in seconds. Defaults to unlimited.',
            default=0,
            min_value=0,
        ),
        max_uses: int = Param(
            description='Specify a maximum use limit for the invite. Defaults to 1 user.',
            default=1,
            min_value=1,
        ),
        reason: str = Param(
            description='Give a reason for creating the invite.', default='No reason provided.'
        ),
    ) -> None:
        invite = await inter.channel.create_invite(
            max_age=max_age, max_uses=max_uses, reason=reason
        )

        embed = (
            core.TypicalEmbed(inter=inter, title='Created a new invite!')
            .add_field(name='Link', value=f'https://discord.gg/{invite.code}')
            .add_field(name='Code', value=f'`{invite.code}`')
            .add_field(
                name='Lifetime',
                value='Unlimited' if max_age == 0 else f'{max_age} Seconds',
            )
        )

        await inter.send(embed=embed)

    # nick
    @commands.slash_command(
        name='nick',
        description='Change nickname of a member.',
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _nick(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member = Param(description='Mention the server member.'),
        nickname: str = Param(description='Give the nickname to set for the mentioned user.'),
    ) -> None:
        await member.edit(nick=nickname)
        await inter.send(f'Member {member.mention} has been nicked to **{nickname}**!')

    # slowmode
    @commands.slash_command(
        name='slowmode',
        description='Sets slowmode for the current channel.',
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _slowmode(
        self,
        inter: disnake.CommandInteraction,
        duration: int = Param(
            description='The amount of seconds to set the slowmode to. Set 0 to disable.',
            min_value=0,
            max_value=21600,
            choices=[
                OptionChoice('Remove Slowmode', 0),
                OptionChoice('5s', 5),
                OptionChoice('10s', 10),
                OptionChoice('15s', 15),
                OptionChoice('30s', 30),
                OptionChoice('1m', 60),
                OptionChoice('2m', 120),
                OptionChoice('5m', 300),
                OptionChoice('10m', 600),
                OptionChoice('15m', 900),
                OptionChoice('30m', 1800),
                OptionChoice('1h', 3600),
                OptionChoice('2h', 7200),
                OptionChoice('6h', 21600),
            ],
        ),
    ) -> None:
        await inter.channel.edit(slowmode_delay=duration)

        if duration == 0:
            await inter.send('Slowmode has been disabled!')
        else:
            await inter.send(f'Slowmode has been set to **{duration}** seconds.')

    # makechannel
    @commands.slash_command(
        name='makechannel',
        description='Create a new text channel.',
        dm_permission=False,
    )
    @commands.has_role(LockRoles.admin)
    async def _makechannel(
        self,
        inter: disnake.CommandInteraction,
        name: str = Param(description='Give a name for the new channel.'),
        category: disnake.CategoryChannel = Param(
            description='Specify the category to put the channel into. Defaults to none.',
            default=None,
            channel_types=[ChannelType.category],
        ),
        topic: str = Param(description='Give a topic for the new channel.', default=None),
    ) -> None:
        channel = await inter.guild.create_text_channel(name=name, topic=topic, category=category)
        await inter.send(f'Channel {channel.mention} has been created!')

    # makevc
    @commands.slash_command(
        name='makevoice',
        description='Create a new voice channel.',
        dm_permission=False,
    )
    @commands.has_role(LockRoles.admin)
    async def _makevc(
        self,
        inter: disnake.CommandInteraction,
        name: str = Param(description='Give a name for the new voice channel.'),
        category: disnake.CategoryChannel = Param(
            description='Specify the category to put the channel into. Defaults to none.',
            default=None,
            channel_types=[ChannelType.category],
        ),
    ) -> None:
        vc = await inter.guild.create_voice_channel(name=name, category=category)
        await inter.send(f'{vc.mention} has been created!')

    # makestage
    @commands.slash_command(
        name='makestage',
        description='Creates a new stage channel.',
        dm_permission=False,
    )
    @commands.has_role(LockRoles.admin)
    async def _makestage(
        self,
        inter: disnake.CommandInteraction,
        name: str = Param(description='Give a name for the new voice channel.'),
        category: disnake.CategoryChannel = Param(
            description='Specify the category to put the channel into. Defaults to none.',
            default=None,
            channel_types=[ChannelType.category],
        ),
    ):
        stage = await inter.guild.create_stage_channel(name=name, category=category)
        await inter.send(f'{stage.mention} has been created!')


    # makecategory
    @commands.slash_command(
        name='makecategory',
        description='Create a new channel category.',
        dm_permission=False,
    )
    @commands.has_role(LockRoles.admin)
    async def _makecategory(
        self,
        inter: disnake.CommandInteraction,
        name: str = Param(description='Give a name for the new category.'),
    ) -> None:
        category = await inter.guild.create_category(name=name)
        await inter.send(f'Category {category.mention} has been created!')

    # removechannel
    @commands.slash_command(
        name='deletechannel',
        description='Delete a channel from the server.',
        dm_permission=False,
    )
    @commands.has_role(LockRoles.admin)
    async def _removechannel(
        self,
        inter: disnake.CommandInteraction,
        channel: disnake.abc.Messageable = Param(
            description='Specify the channel that you want to delete.'
        ),
    ) -> None:
        await channel.delete()
        await inter.send('Channel has been deleted!')

    # reset
    @commands.slash_command(
        name='reset', description='Resets the current channel.', dm_permission=False
    )
    @commands.has_role(LockRoles.admin)
    async def _reset(self, inter: disnake.CommandInteraction) -> None:
        name = inter.channel.name
        category = inter.channel.category
        topic = inter.channel.topic
        overwrites = inter.channel.overwrites

        resetted = await inter.guild.create_text_channel(
            name=name, topic=topic, category=category, overwrites=overwrites
        )
        await inter.channel.delete()
        await resetted.send(f'Channel was reset by {inter.author.mention}.')

    # afkvc
    @commands.slash_command(
        name='afkvc',
        description='Configures the inactive (AFK) channel for the server.',
        dm_permission=False,
    )
    @commands.has_role(LockRoles.admin)
    async def _afkvc(
        self,
        inter: disnake.CommandInteraction,
        channel: disnake.VoiceChannel = Param(
            description='Select the AFK channel. Leave blank to create new.',
            default=None,
            channel_types=[ChannelType.voice],
        ),
        timeout: int = Param(
            description='Time after a user is set AFK. Default is 5 minutes (300s).',
            default=300,
            min_value=60,
            max_value=3600,
            choices=[
                OptionChoice('1m', 60),
                OptionChoice('5m', 300),
                OptionChoice('15m', 900),
                OptionChoice('30m', 1800),
                OptionChoice('1h', 3600),
            ],
        ),
    ) -> None:
        if channel is None:
            channel = await inter.guild.create_voice_channel(name='afk-vc')

        await inter.guild.edit(
            reason=f'Inactive channel updated by: {inter.author}',
            afk_channel=channel,
            afk_timeout=timeout,
        )
        await inter.send(
            f'{channel.mention} has been set as the AFK channel with timeout of `{timeout}s`.'
        )


# The setup() function for the cog.
def setup(bot: core.IgKnite) -> None:
    bot.add_cog(Customization(bot))
