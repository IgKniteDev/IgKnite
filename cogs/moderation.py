# SPDX-License-Identifier: MIT


# Imports.
from typing import List

import disnake
from disnake import OptionChoice
from disnake.ext import commands
from disnake.ext.commands import Param

import core
from core.chain import keychain
from core.datacls import LockRoles


# The actual cog.
class Moderation(commands.Cog):
    def __init__(self, bot: core.IgKnite) -> None:
        self.bot = bot

    # ban
    @commands.slash_command(
        name='ban',
        description='Bans a member from the server.',
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _ban(
        self,
        inter: disnake.CommandInter,
        member: disnake.Member = Param(description='Mention the server member.'),
        reason: str = Param(
            description='Give a reason for the ban.', default='No reason provided.'
        ),
    ) -> None:
        await inter.guild.ban(member, reason=reason)
        await inter.send(f'Member **{member.display_name}** has been banned! Reason: {reason}')

    # Common backend for softban-labelled commands.
    # Do not use it within other commands unless really necessary.
    async def _softban_backend(
        self,
        inter: disnake.CommandInter,
        member: disnake.Member,
        *,
        days: int = 7,
        reason: str = 'No reason provided.',
    ) -> None:
        await inter.guild.ban(member, delete_message_days=days, reason=reason)
        await inter.guild.unban(member)
        await inter.send(f'Member **{member.display_name}** has been softbanned! Reason: {reason}')

    # softban (slash)
    @commands.slash_command(
        name='softban',
        description='Temporarily bans members to delete their messages.',
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _softban(
        self,
        inter: disnake.CommandInter,
        member: disnake.Member = Param(description='Mention the server member.'),
        reason: str = Param(
            description='Give a reason for the softban.', default='No reason provided.'
        ),
        daycount: int = Param(
            description='The amount of days to check for deleting messages. Defaults to 7.',
            default=7,
            choices=[
                OptionChoice('1d', 1),
                OptionChoice('2d', 2),
                OptionChoice('3d', 3),
                OptionChoice('4d', 4),
                OptionChoice('5d', 5),
                OptionChoice('6d', 6),
                OptionChoice('7d', 7),
            ],
        ),
    ):
        await self._softban_backend(inter, member, days=daycount, reason=reason)

    # softban (user)
    @commands.user_command(name='Wipe (Softban)', dm_permission=False)
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _softban_user(self, inter: disnake.CommandInter, member: disnake.Member) -> None:
        await self._softban_backend(inter, member)

    # kick
    @commands.slash_command(
        name='kick',
        description='Kicks a member from the server.',
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _kick(
        self,
        inter: disnake.CommandInter,
        member: disnake.Member = Param(description='Mention the server member.'),
        reason: str = Param(
            description='Give a reason for the kick.', default='No reason provided.'
        ),
    ) -> None:
        await inter.guild.kick(member, reason=reason)
        await inter.send(f'Member **{member.display_name}** has been kicked! Reason: {reason}')

    # timeout
    @commands.slash_command(
        name='timeout',
        description='Timeouts a member.',
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _timeout(
        self,
        inter: disnake.CommandInter,
        member: disnake.Member = Param(description='Mention the server member.'),
        duration: int = Param(
            description='Give a duration for the timeout in seconds. Defaults to 30.',
            default=30,
            min_value=1,
        ),
        reason: str = Param(
            description='Give a reason for the timeout.', default='No reason provided.'
        ),
    ) -> None:
        await member.timeout(duration=duration, reason=reason)
        await inter.send(f'Member **{member.display_name}** has been timed out! Reason: {reason}')

    # unban
    @commands.slash_command(
        name='unban',
        description='Unbans a member from the server.',
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _unban(
        self,
        inter: disnake.CommandInter,
        id: int = Param(description='The identifier of the user to unban.', large=True),
        reason: str = Param(
            description='Give a reason for the unban.', default='No reason provided.'
        ),
    ) -> None:
        user = await self.bot.getch_user(id)
        await inter.guild.unban(user, reason=reason)
        await inter.send(f'User **{user.display_name}** has been unbanned!')

    # purge
    @commands.slash_command(
        name='purge',
        description='Clears messages within the given index.',
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _purge(
        self,
        inter: disnake.CommandInter,
        amount: int = Param(
            description='The amount of messages to purge. Defaults to 1.', default=1, min_value=1
        ),
        onlyme: bool = Param(
            description='Only deletes messages sent by me. Defaults to false.', default=False
        ),
    ) -> None:
        await inter.response.defer(ephemeral=True)

        def is_me(message: disnake.Message) -> bool:
            return message.author == self.bot.user

        amount += 1

        if onlyme:
            await inter.channel.purge(limit=amount, check=is_me)
        else:
            await inter.channel.purge(limit=amount)

    # Common backend for ripplepurge-labelled commands.
    # Do not use it within other commands unless really necessary.
    async def _ripplepurge_backend(
        self,
        inter: disnake.CommandInter,
        member: disnake.Member,
        amount: int = 10,
    ) -> None:
        await inter.response.defer(ephemeral=True)

        messages = []
        async for msg in inter.channel.history():
            if len(messages) == amount:
                break

            if msg.author == member:
                messages.append(msg)

        await inter.channel.delete_messages(messages)
        await inter.send(
            f'Purged {len(messages)} messages that were sent by **{member.display_name}.**',
        )

    # ripplepurge (slash)
    @commands.slash_command(
        name='ripplepurge',
        description='Clears messages that are sent by a specific user within the given index.',
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _ripplepurge(
        self,
        inter: disnake.CommandInter,
        member: disnake.Member = Param(description='Mention the server member.'),
        amount: int = Param(
            description='The amount of messages to purge. Defaults to 10.', default=10, min_value=1
        ),
    ) -> None:
        await self._ripplepurge_backend(inter, member, amount)

    # ripplepurge (user)
    @commands.user_command(name='Ripple Purge', dm_permission=False)
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _ripplepurge_user(self, inter: disnake.CommandInter, member: disnake.Member) -> None:
        await self._ripplepurge_backend(inter, member)

    # ripplepurge (message)
    @commands.message_command(name='Ripple Purge', dm_permission=False)
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _ripplepurge_message(
        self, inter: disnake.CommandInter, message: disnake.Message
    ) -> None:
        await self._ripplepurge_backend(inter, message.author)

    # snipe
    @commands.slash_command(
        name='snipe',
        description='Snipes messages within 25 seconds of their deletion.',
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _snipe(
        self,
        inter: disnake.CommandInter,
        author: disnake.Member = Param(
            description='Mention the author of the messages to snipe. Defaults to none.',
            default=None,
        ),
    ) -> None:
        await inter.response.defer(ephemeral=True)

        sniped_count: int = 0
        snipeables = sorted(
            [
                snipeable
                for snipeable in keychain.snipeables
                if (snipeable.guild == inter.guild) and (snipeable.channel == inter.channel)
            ],
            key=lambda x: x.created_at.timestamp(),
        )

        if not snipeables:
            return await inter.send('No messages were found in my list.')

        webhooks: List[disnake.Webhook] = []

        def find_hook(name: str) -> disnake.Webhook | None:
            for webhook in webhooks:
                if webhook.name == name:
                    return webhook

        for snipeable in snipeables:
            if (author and snipeable.author == author) or (not author):
                webhook = find_hook(snipeable.author.display_name)

                if not webhook:
                    webhook = await inter.channel.create_webhook(name=snipeable.author.display_name)
                    webhooks.append(webhook)

                await webhook.send(
                    content=snipeable.content,
                    username=snipeable.author.display_name,
                    avatar_url=snipeable.author.avatar,
                )
                sniped_count += 1

            else:
                pass

        for webhook in await inter.channel.webhooks():
            if webhook.user == self.bot.user:
                await webhook.delete()

        await inter.send(
            (
                f'Sniped **{sniped_count}** messages'
                + ('.' if not author else f' sent by {author.mention}.')
            ),
        )

    # senddm
    @commands.slash_command(
        name='senddm',
        description='Send DM to specific users.',
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def senddm(
        self,
        inter: disnake.CommandInter,
        member: disnake.Member = Param(description='Mention the server member.'),
        msg: str = Param(description='The message you want to send.'),
    ) -> None:
        await inter.response.defer(ephemeral=True)

        embed = (
            core.TypicalEmbed(
                inter=inter, title=f'{inter.author.display_name} has sent you a message!'
            )
            .add_field('Message: ', msg)
            .set_thumbnail(url=inter.author.avatar.url)
        )

        await member.send(embed=embed)
        await inter.send('Your message has been delivered!')

    # pins
    @commands.slash_command(
        name='pins',
        description='Shows all pinned messages in the current channel.',
        dm_permission=False,
    )
    async def _pins(self, inter: disnake.CommandInter) -> None:
        await inter.response.defer()

        pins = await inter.channel.pins()
        if not pins:
            await inter.send('There are no pinned messages in this channel.', ephemeral=True)
        else:
            embed = core.TypicalEmbed(inter=inter, title='Pinned Messages  📌')

            for count, pin in enumerate(pins):
                embed.add_field(
                    name=f'{count}. {pin.author.name}',
                    value=f'{pin.content} \n\n',
                    inline=False,
                )

            await inter.send(embed=embed)

    # clearpins
    @commands.slash_command(
        name='clearpins',
        description='Clears all pinned messages in the current channel.',
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _clearpins(self, inter: disnake.CommandInter) -> None:
        await inter.response.defer(ephemeral=True)

        pins = await inter.channel.pins()

        if pins:
            for pin in pins:
                await pin.unpin()

            return await inter.send('All pins have been cleared!')

        await inter.send('There are no pins to clear!')

    # banword
    @commands.slash_command(
        name='banword',
        description='Add keywords to ban.',
        dm_permission=False,
    )
    @commands.has_role(LockRoles.admin)
    async def _banword(
        self,
        inter: disnake.CommandInter,
        keywords: str = Param(description='The keywords you want to ban, separated by commas.'),
    ) -> None:
        await inter.response.defer(ephemeral=True)

        keywords = keywords.split(',')

        try:
            for item in await inter.guild.fetch_automod_rules():
                if item.name == 'IgKnite Banwords':
                    rule = item
                    break
            else:
                rule = None

        except disnake.NotFound:
            rule = None

        if not rule:
            rule = await inter.guild.create_automod_rule(
                name='IgKnite Banwords',
                event_type=disnake.AutoModEventType.message_send,
                trigger_type=disnake.AutoModTriggerType.keyword,
                trigger_metadata=disnake.AutoModTriggerMetadata(keyword_filter=[]),
                actions=[disnake.AutoModBlockMessageAction()],
                enabled=True,
                reason=f'Banwords added by: {inter.author}',
            )

        meta = rule.trigger_metadata
        await rule.edit(
            trigger_metadata=meta.with_changes(
                keyword_filter=meta.keyword_filter + keywords,
            ),
        )

        embed = core.TypicalEmbed(
            inter, title='Added these words to banned list:', description=', '.join(keywords)
        )
        await inter.send(embed=embed)

    # clearbannedwords
    @commands.slash_command(
        name='clearbannedwords',
        description='Clears the list of banned keywords added by me.',
        dm_permission=False,
    )
    @commands.has_role(LockRoles.admin)
    async def _clearbannedwords(self, inter: disnake.CommandInter) -> None:
        await inter.response.defer(ephemeral=True)

        try:
            for rule in await inter.guild.fetch_automod_rules():
                if rule.name == 'IgKnite Banwords':
                    await rule.delete(reason=f'Banwords removed by: {inter.author}')

        except disnake.NotFound:
            await inter.send('No banned words were found.')

        else:
            await inter.send('Banwords removed!')

    # showbannedwords
    @commands.slash_command(
        name='showbannedwords',
        description='Shows the list of banned keywords added by me.',
        dm_permission=False,
    )
    @commands.has_role(LockRoles.admin)
    async def _showbannedwords(self, inter: disnake.CommandInter) -> None:
        await inter.response.defer(ephemeral=True)

        try:
            words = ''

            for rule in await inter.guild.fetch_automod_rules():
                if rule.name == 'IgKnite Banwords':
                    words += (f'{item} \n' for item in rule.trigger_metadata.keyword_filter)
                    embed = core.TypicalEmbed(
                        inter, title='Here\'s the list of banned words:', description=words
                    )
                    await inter.send(embed=embed)

        except disnake.NotFound:
            await inter.send('No banned words were found.')

    # clearnicks
    @commands.slash_command(
        name='resetnicks',
        description='Clear every nickname on the server.',
        dm_permission=False,
    )
    @commands.has_role(LockRoles.admin)
    async def _clearnicks(self, inter: disnake.CommandInter) -> None:
        await inter.response.defer(ephemeral=True)

        deletion_count = 0

        for member in inter.guild.members:
            try:
                await member.edit(nick=None)
                deletion_count += 1
            except disnake.errors.Forbidden:
                pass

        await inter.send(
            f'Cleared the nicks for **{deletion_count} out of {inter.guild.member_count}** users.'
        )


# The setup() function for the cog.
def setup(bot: core.IgKnite) -> None:
    bot.add_cog(Moderation(bot))
