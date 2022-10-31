'''
The `Customization` cog for IgKnite.
---

License can be found here:
https://github.com/IgKniteDev/IgKnite/blob/main/LICENSE
'''


# Imports.
import core
import disnake
from core.datacls import LockRoles
from disnake import ChannelType, Option, OptionChoice, OptionType
from disnake.ext import commands


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
        return await inter.response.defer()

    # makerole
    @commands.slash_command(
        name='makerole',
        description='Create a new role.',
        options=[
            Option(
                'name',
                'Give a name for the new role.',
                OptionType.string,
                required=True,
            ),
            Option(
                'color',
                'Give a color for the new role in Hex.',
                OptionType.string,
                required=False,
            ),
        ],
        dm_permission=False,
    )
    @commands.has_role(LockRoles.admin)
    async def _makerole(
        self, inter: disnake.CommandInteraction, name: str, color: str = '#000000'
    ) -> None:
        color = get_color(color)
        await inter.guild.create_role(name=name, color=color)
        embed = disnake.Embed(description=f'Role `{name}` has been created.', color=color)
        await inter.send(embed=embed)

    # assignrole
    @commands.slash_command(
        name='assignrole',
        description='Assign a role to a server member.',
        options=[
            Option('member', 'Mention the server member.', OptionType.user, required=True),
            Option(
                'role',
                'Mention the role to assign to the user.',
                OptionType.role,
                required=True,
            ),
        ],
        dm_permission=False,
    )
    @commands.has_role(LockRoles.admin)
    async def _assignrole(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member,
        role: disnake.Role,
    ) -> None:
        await member.add_roles(role)
        await inter.send(f'Role {role.mention} has been assigned to **{member.display_name}**!')

    # removerole
    @commands.slash_command(
        name='removerole',
        description='Remove a role from the server.',
        options=[Option('role', 'Mention the role to remove.', OptionType.role, required=True)],
        dm_permission=False,
    )
    @commands.has_role(LockRoles.admin)
    async def _removerole(self, inter: disnake.CommandInteraction, role: disnake.Role) -> None:
        await role.delete()
        await inter.send(f'Role **@{role.name}** has been removed!')

    # happy birthday to furti :cake:
    # edit: this is hitblast and here's your birthday gift commit :D

    # makeinvite
    @commands.slash_command(
        name='makeinvite',
        description='Create an invitation link to the server.',
        options=[
            Option(
                'max_age',
                'Specify a lifetime for the invite in seconds. Defaults to unlimited.',
                OptionType.integer,
                min_value=0,
            ),
            Option(
                'max_uses',
                'Specify a maximum use limit for the invite. Defaults to 1 user.',
                OptionType.integer,
                min_value=1,
            ),
            Option('reason', 'Give a reason for creating the invite.', OptionType.string),
        ],
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _makeinvite(
        self,
        inter: disnake.CommandInteraction,
        max_age: int = 0,
        max_uses: int = 1,
        reason: str = 'No reason provided.',
    ) -> None:
        invite = await inter.channel.create_invite(
            max_age=max_age, max_uses=max_uses, reason=reason
        )

        embed = (
            core.TypicalEmbed(inter)
            .set_title(value='Created a new invite!')
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
        options=[
            Option('member', 'Mention the server member.', OptionType.user, required=True),
            Option(
                'nickname',
                'Give the nickname to set for the mentioned user.',
                OptionType.string,
                required=True,
            ),
        ],
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _nick(
        self, inter: disnake.CommandInteraction, member: disnake.Member, nickname: str
    ) -> None:
        await member.edit(nick=nickname)
        await inter.send(f'Member {member.mention} has been nicked to **{nickname}**!')

    # makechannel
    @commands.slash_command(
        name='makechannel',
        description='Create a new text channel.',
        options=[
            Option(
                'name',
                'Give a name for the new channel.',
                OptionType.string,
                required=True,
            ),
            Option(
                'category',
                'Specify the category to put the channel into.',
                OptionType.channel,
                channel_types=[ChannelType.category],
            ),
            Option('topic', 'Give a topic for the new channel.', OptionType.string),
        ],
        dm_permission=False,
    )
    @commands.has_role(LockRoles.admin)
    async def _makechannel(
        self,
        inter: disnake.CommandInteraction,
        name: str,
        category: disnake.CategoryChannel | None = None,
        topic: str | None = None,
    ) -> None:
        channel = await inter.guild.create_text_channel(name=name, topic=topic, category=category)
        await inter.send(f'Channel {channel.mention} has been created!')

    # makevc
    @commands.slash_command(
        name='makevc',
        description='Create a new voice channel.',
        options=[
            Option('name', 'Give a name of the voice channel.', required=True),
            Option(
                'category',
                'Specify the category to put the channel into.',
                OptionType.channel,
                channel_types=[ChannelType.category],
            ),
        ],
        dm_permission=False,
    )
    @commands.has_role(LockRoles.admin)
    async def _makevc(
        self,
        inter: disnake.CommandInteraction,
        name: str,
        category: disnake.CategoryChannel | None = None,
    ) -> None:
        vc = await inter.guild.create_voice_channel(name=name, category=category)
        await inter.send(f'VC {vc.mention} has been created!')

    # makecategory
    @commands.slash_command(
        name='makecategory',
        description='Create a new channel category.',
        options=[
            Option(
                'name',
                'Give a name for the new category.',
                OptionType.string,
                required=True,
            )
        ],
        dm_permission=False,
    )
    @commands.has_role(LockRoles.admin)
    async def _makecategory(
        self,
        inter: disnake.CommandInteraction,
        name: str,
    ) -> None:
        category = await inter.guild.create_category(name=name)
        await inter.send(f'Category {category.mention} has been created!')

    # removechannel
    @commands.slash_command(
        name='removechannel',
        description='Remove a channel from the server.',
        options=[
            Option(
                'channel',
                'Specify the channel you want to delete.',
                OptionType.channel,
                required=True,
            )
        ],
        dm_permission=False,
    )
    @commands.has_role(LockRoles.admin)
    async def _removechannel(
        self,
        inter: disnake.CommandInteraction,
        channel: disnake.TextChannel | disnake.VoiceChannel | disnake.StageChannel,
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

    # setup afkvc
    @commands.slash_command(
        name='afkvc',
        description='Configures AFK channel for the server.',
        dm_permission=False,
        options=[
            Option('channel', 'Select AFK channel. Leave blank to create new.', OptionType.channel),
            Option(
                'timeout',
                'Time after a user is set AFK.',
                OptionType.integer,
                min_value=60,
                max_value=3600,
                choices=[
                    OptionChoice('1 min', 60),
                    OptionChoice('5 min', 300),
                    OptionChoice('15 min', 900),
                    OptionChoice('30 min', 1800),
                    OptionChoice('1 hour', 3600),
                ],
            ),
        ],
    )
    @commands.has_role(LockRoles.admin)
    async def _afkvc(
        self,
        inter: disnake.CommandInteraction,
        channel: disnake.VoiceChannel | None = None,
        timeout: int | None = None,
    ) -> None:
        timeout = 300 if timeout is None else timeout
        if channel is None:
            channel = await inter.guild.create_voice_channel(name='afk-vc')

        await inter.guild.edit(reason='Update AFK VC', afk_channel=channel, afk_timeout=timeout)
        await inter.send(
            f'{channel.mention} has been set as AFK channel with timeout of {timeout} secs.'
        )


# The setup() function for the cog.
def setup(bot: core.IgKnite) -> None:
    bot.add_cog(Customization(bot))
