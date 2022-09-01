'''
The `Customization` cog for IgKnite.
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
from core.datacls import LockRoles


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
                'The name for the new role.',
                OptionType.string,
                required=True
            )
        ],
        dm_permission=False
    )
    @commands.has_role(LockRoles.admin)
    async def _makerole(
        self,
        inter: disnake.CommandInteraction,
        name: str
    ) -> None:
        role = await inter.guild.create_role(name=name)
        await inter.send(f'Role {role.mention} has been created!')

    # assignrole
    @commands.slash_command(
        name='assignrole',
        description='Assign a role to a server member.',
        options=[
            Option(
                'member',
                'Mention the server member.',
                OptionType.user,
                required=True
            ),
            Option(
                'role',
                'The role to assign to the user.',
                OptionType.role,
                required=True
            )
        ],
        dm_permission=False
    )
    @commands.has_role(LockRoles.admin)
    async def _assignrole(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member,
        role: disnake.Role
    ) -> None:
        await member.add_roles(role)
        await inter.send(f'Role {role.mention} has been assigned to **{member.display_name}**!')

    # removerole
    @commands.slash_command(
        name='removerole',
        description='Remove a role from the server.',
        options=[
            Option(
                'role',
                'The role to remove.',
                OptionType.role,
                required=True
            )
        ],
        dm_permission=False
    )
    @commands.has_role(LockRoles.admin)
    async def _removerole(
        self,
        inter: disnake.CommandInteraction,
        role: disnake.Role
    ) -> None:
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
                'The lifetime of the invite in seconds. Defaults to unlimited.',
                OptionType.integer
            ),
            Option(
                'max_uses',
                'The maximum use limit for the invite. Defaults to 1 user.',
                OptionType.integer
            ),
            Option(
                'reason',
                'The reason behind creating the invite.',
                OptionType.string
            )
        ],
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _makeinvite(
        self,
        inter: disnake.CommandInteraction,
        max_age: int = 0,
        max_uses: int = 1,
        reason: str = 'No reason provided.'
    ) -> None:
        invite = await inter.channel.create_invite(max_age=max_age, max_uses=max_uses, reason=reason)

        embed = core.TypicalEmbed(inter).set_title(
            value='Created a new invite!'
        ).add_field(
            name='Link',
            value=f'https://discord.gg/{invite.code}'
        ).add_field(
            name='Code',
            value=f'`{invite.code}`'
        ).add_field(
            name='Lifetime',
            value='Unlimited' if max_age == 0 else f'{max_age} Seconds'
        )

        await inter.send(embed=embed)

    # nick
    @commands.slash_command(
        name='nick',
        description='Change nickname of a member.',
        options=[
            Option(
                'member',
                'Mention the server member.',
                OptionType.user,
                required=True
            ),
            Option(
                'nickname',
                'The nickname to set for the user.',
                OptionType.string,
                required=True
            )
        ],
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _nick(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member,
        nickname: str
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
                'The name for the new channel.',
                OptionType.string,
                required=True
            ),
            Option(
                'category',
                'The category to put the channel into.'
            ),
            Option(
                'topic',
                'The topic for the new channel.',
                OptionType.string
            )
        ],
        dm_permission=False
    )
    @commands.has_role(LockRoles.admin)
    async def _makechannel(
        self,
        inter: disnake.CommandInteraction,
        name: str,
        category: disnake.CategoryChannel | None = None,
        description: str | None = None
    ) -> None:
        channel = await inter.guild.create_text_channel(
            name=name,
            topic=description,
            category=category
        )
        await inter.send(f'Channel {channel.mention} has been created!')

    # makevc
    @commands.slash_command(
        name='makevc',
        description='Create a new voice channel.',
        options=[
            Option(
                'name',
                'The name of the voice channel.',
                required=True
            ),
            Option(
                'category',
                'The category to put the channel into.'
            )
        ],
        dm_permission=False
    )
    @commands.has_role(LockRoles.admin)
    async def _makevc(
        self,
        inter: disnake.CommandInteraction,
        name: str,
        category: disnake.CategoryChannel | None = None
    ) -> None:
        vc = await inter.guild.create_voice_channel(
            name=name,
            category=category
        )
        await inter.send(f'VC {vc.mention} has been created!')

    # makecategory
    @commands.slash_command(
        name='makecategory',
        description='Create a new channel category.',
        options=[
            Option(
                'name',
                'The name for the new category.',
                OptionType.string
            )
        ],
        dm_permission=False
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
                'The channel you want to delete.',
                OptionType.channel,
                required=True
            )
        ],
        dm_permission=False
    )
    @commands.has_role(LockRoles.admin)
    async def _removechannel(
        self,
        inter: disnake.CommandInteraction,
        channel: disnake.TextChannel | disnake.VoiceChannel | disnake.StageChannel
    ) -> None:
        await channel.delete()
        await inter.send('Channel has been deleted!')


# The setup() function for the cog.
def setup(bot: core.IgKnite) -> None:
    bot.add_cog(Customization(bot))
