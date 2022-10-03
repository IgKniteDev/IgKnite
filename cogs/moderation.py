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
from core import global_
from core.datacls import LockRoles


# The actual cog.
class Moderation(commands.Cog):
    def __init__(
        self,
        bot: core.IgKnite
    ) -> None:
        self.bot = bot

    async def cog_before_slash_command_invoke(self, inter: disnake.CommandInteraction) -> None:
        return await inter.response.defer()

    # ban
    @commands.slash_command(
        name='ban',
        description='Bans a member from the server.',
        options=[
            Option(
                'member',
                'Mention the server member.',
                OptionType.user,
                required=True
            ),
            Option(
                'reason',
                'Give a reason for the ban.',
                OptionType.string
            )
        ],
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _ban(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member,
        reason: str = 'No reason provided.'
    ) -> None:
        await inter.guild.ban(member, reason=reason)
        await inter.send(f'Member **{member.display_name}** has been banned! Reason: {reason}')

    # Backend for softban-labelled commands.
    # Do not use it within other commands unless really necessary.
    async def _softban_backend(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member,
        *,
        days: int = 7,
        reason: str = 'No reason provided.'
    ) -> None:
        await inter.guild.ban(
            member,
            delete_message_days=days,
            reason=reason
        )
        await inter.guild.unban(member)
        await inter.send(f'Member **{member.display_name}** has been softbanned! Reason: {reason}')

    # softban (slash)
    @commands.slash_command(
        name='softban',
        description='Temporarily bans members to delete their messages.',
        options=[
            Option(
                'member',
                'Mention the server member.',
                OptionType.user,
                required=True
            ),
            Option(
                'reason',
                'Give a reason for the softban.',
                OptionType.string
            )
        ],
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _softban(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member,
        reason: str = 'No reason provided.'
    ):
        await self._softban_backend(inter, member, reason=reason)

    # softban (user)
    @commands.user_command(
        name='Wipe (Softban)',
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _softban_user(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member
    ) -> None:
        await self._softban_backend(inter, member)

    # kick
    @commands.slash_command(
        name='kick',
        description='Kicks a member from the server.',
        options=[
            Option(
                'member',
                'Mention the server member.',
                OptionType.user,
                required=True
            ),
            Option(
                'reason',
                'Give a reason for the kick.',
                OptionType.string
            )
        ],
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _kick(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member,
        reason: str = 'No reason provided.'
    ) -> None:
        await inter.guild.kick(member, reason=reason)
        await inter.send(f'Member **{member.display_name}** has been kicked! Reason: {reason}')

    # timeout
    @commands.slash_command(
        name='timeout',
        description='Timeouts a member.',
        options=[
            Option(
                'member',
                'Mention the server member.',
                OptionType.user,
                required=True
            ),
            Option(
                'duration',
                'Give a duration for the timeout in seconds. Defaults to 30 seconds.',
                OptionType.integer,
                min_value=1
            ),
            Option(
                'reason',
                'Give a reason for the timeout.',
                OptionType.string
            )
        ],
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _timeout(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member,
        duration: int = 30,
        reason: str = 'No reason provided.'
    ) -> None:
        await member.timeout(duration=duration, reason=reason)
        await inter.send(f'Member **{member.display_name}** has been timed out! Reason: {reason}')

    # unban
    @commands.slash_command(
        name='unban',
        description='Unbans a member from the server.',
        options=[
            Option(
                'member',
                'Mention the server member.',
                OptionType.user,
                required=True
            )
        ],
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _unban(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member
    ) -> None:
        await inter.guild.unban(member)
        await inter.send(f'Member **{member.display_name}** has been unbanned!')

    # purge
    @commands.slash_command(
        name='purge',
        description='Clears messages within the given index.',
        options=[
            Option(
                'amount',
                'The amount of messages to purge. Defaults to 1.',
                OptionType.integer,
                min_value=1
            )
        ],
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _purge(
        self,
        inter: disnake.CommandInteraction,
        amount: int = 1
    ) -> None:
        await inter.channel.purge(limit=amount + 1)
        await inter.send(f'Purged **{amount}** messages.', ephemeral=True)

    # Backend for ripplepurge-labelled commands.
    # Do not use it within other commands unless really necessary.
    async def _ripplepurge_backend(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member,
        amount: int = 10
    ) -> None:
        messages = []
        async for msg in inter.channel.history():
            if len(messages) == amount:
                break

            if msg.author == member:
                messages.append(msg)

        await inter.channel.delete_messages(messages)
        await inter.send(
            f'Purged 10 messages that were sent by **{member.display_name}.**',
            ephemeral=True
        )

    # ripplepurge (slash)
    @commands.slash_command(
        name='ripplepurge',
        description='Clears messages that are sent by a specific user within the given index.',
        options=[
            Option(
                'member',
                'Mention the server member.',
                OptionType.user,
                required=True
            ),
            Option(
                'amount',
                'The amount of messages to purge. Defaults to 10.',
                OptionType.integer,
                min_value=1
            )
        ],
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _ripplepurge(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member,
        amount: int = 10
    ) -> None:
        await self._ripplepurge_backend(inter, member, amount)

    # ripplepurge (user)
    @commands.user_command(
        name='Ripple Purge',
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _ripplepurge_user(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member
    ) -> None:
        await self._ripplepurge_backend(inter, member)

    # ripplepurge (message)
    @commands.message_command(
        name='Ripple Purge',
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _ripplepurge_message(
        self,
        inter: disnake.CommandInteraction,
        message: disnake.Message
    ) -> None:
        await self._ripplepurge_backend(inter, message.author)

    # snipe
    @commands.slash_command(
        name='snipe',
        description='Snipes messages within 25 seconds of their deletion.',
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _snipe(
        self,
        inter: disnake.CommandInteraction
    ) -> None:
        webhook: disnake.Webhook = None
        sniped_count: int = 0

        if global_.snipeables:
            for snipeable in global_.snipeables:
                if snipeable.guild == inter.guild:
                    if (
                        webhook
                        and webhook.name == snipeable.author.display_name
                    ):
                        pass

                    else:
                        webhook = await inter.channel.create_webhook(name=snipeable.author)

                    await webhook.send(
                        content=snipeable.content,
                        username=snipeable.author.display_name,
                        avatar_url=snipeable.author.avatar
                    )
                    sniped_count += 1

            await webhook.delete()
            await inter.send(f'Sniped **{sniped_count}** messages.', ephemeral=True)

        else:
            await inter.send('No messages were found in my list.', ephemeral=True)


# The setup() function for the cog.
def setup(bot: core.IgKnite) -> None:
    bot.add_cog(Moderation(bot))
