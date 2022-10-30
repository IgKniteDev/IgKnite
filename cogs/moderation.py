'''
The `Moderation` cog for IgKnite.
---

License can be found here:
https://github.com/IgKniteDev/IgKnite/blob/main/LICENSE
'''


# Imports.
import disnake
from disnake import Option, OptionType, OptionChoice
from disnake.ext import commands

import core
from core import global_
from core.datacls import LockRoles


# The actual cog.
class Moderation(commands.Cog):
    def __init__(self, bot: core.IgKnite) -> None:
        self.bot = bot

    async def cog_before_slash_command_invoke(self, inter: disnake.CommandInteraction) -> None:
        return await inter.response.defer()

    # ban
    @commands.slash_command(
        name='ban',
        description='Bans a member from the server.',
        options=[
            Option('member', 'Mention the server member.', OptionType.user, required=True),
            Option('reason', 'Give a reason for the ban.', OptionType.string),
        ],
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _ban(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member,
        reason: str = 'No reason provided.',
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
        reason: str = 'No reason provided.',
    ) -> None:
        await inter.guild.ban(member, delete_message_days=days, reason=reason)
        await inter.guild.unban(member)
        await inter.send(f'Member **{member.display_name}** has been softbanned! Reason: {reason}')

    # softban (slash)
    @commands.slash_command(
        name='softban',
        description='Temporarily bans members to delete their messages.',
        options=[
            Option('member', 'Mention the server member.', OptionType.user, required=True),
            Option('reason', 'Give a reason for the softban.', OptionType.string),
        ],
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _softban(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member,
        reason: str = 'No reason provided.',
    ):
        await self._softban_backend(inter, member, reason=reason)

    # softban (user)
    @commands.user_command(name='Wipe (Softban)', dm_permission=False)
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _softban_user(
        self, inter: disnake.CommandInteraction, member: disnake.Member
    ) -> None:
        await self._softban_backend(inter, member)

    # kick
    @commands.slash_command(
        name='kick',
        description='Kicks a member from the server.',
        options=[
            Option('member', 'Mention the server member.', OptionType.user, required=True),
            Option('reason', 'Give a reason for the kick.', OptionType.string),
        ],
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _kick(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member,
        reason: str = 'No reason provided.',
    ) -> None:
        await inter.guild.kick(member, reason=reason)
        await inter.send(f'Member **{member.display_name}** has been kicked! Reason: {reason}')

    # timeout
    @commands.slash_command(
        name='timeout',
        description='Timeouts a member.',
        options=[
            Option('member', 'Mention the server member.', OptionType.user, required=True),
            Option(
                'duration',
                'Give a duration for the timeout in seconds. Defaults to 30 seconds.',
                OptionType.integer,
                min_value=1,
            ),
            Option('reason', 'Give a reason for the timeout.', OptionType.string),
        ],
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _timeout(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member,
        duration: int = 30,
        reason: str = 'No reason provided.',
    ) -> None:
        await member.timeout(duration=duration, reason=reason)
        await inter.send(f'Member **{member.display_name}** has been timed out! Reason: {reason}')

    # unban
    @commands.slash_command(
        name='unban',
        description='Unbans a member from the server.',
        options=[Option('member', 'Mention the server member.', OptionType.user, required=True)],
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _unban(self, inter: disnake.CommandInteraction, member: disnake.Member) -> None:
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
                min_value=1,
            )
        ],
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _purge(self, inter: disnake.CommandInteraction, amount: int = 1) -> None:
        await inter.channel.purge(limit=amount + 1)
        await inter.send(f'Purged **{amount}** messages.', ephemeral=True)

    # Backend for ripplepurge-labelled commands.
    # Do not use it within other commands unless really necessary.
    async def _ripplepurge_backend(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member,
        amount: int = 10,
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
            ephemeral=True,
        )

    # ripplepurge (slash)
    @commands.slash_command(
        name='ripplepurge',
        description='Clears messages that are sent by a specific user within the given index.',
        options=[
            Option('member', 'Mention the server member.', OptionType.user, required=True),
            Option(
                'amount',
                'The amount of messages to purge. Defaults to 10.',
                OptionType.integer,
                min_value=1,
            ),
        ],
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _ripplepurge(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member,
        amount: int = 10,
    ) -> None:
        await self._ripplepurge_backend(inter, member, amount)

    # ripplepurge (user)
    @commands.user_command(name='Ripple Purge', dm_permission=False)
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _ripplepurge_user(
        self, inter: disnake.CommandInteraction, member: disnake.Member
    ) -> None:
        await self._ripplepurge_backend(inter, member)

    # ripplepurge (message)
    @commands.message_command(name='Ripple Purge', dm_permission=False)
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _ripplepurge_message(
        self, inter: disnake.CommandInteraction, message: disnake.Message
    ) -> None:
        await self._ripplepurge_backend(inter, message.author)

    # snipe
    @commands.slash_command(
        name='snipe',
        description='Snipes messages within 25 seconds of their deletion.',
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _snipe(self, inter: disnake.CommandInteraction) -> None:
        webhook: disnake.Webhook = None
        sniped_count: int = 0

        if global_.snipeables:
            for snipeable in global_.snipeables:
                if snipeable.guild == inter.guild:
                    if webhook and webhook.name == snipeable.author.display_name:
                        pass

                    else:
                        webhook = await inter.channel.create_webhook(name=snipeable.author)

                    await webhook.send(
                        content=snipeable.content,
                        username=snipeable.author.display_name,
                        avatar_url=snipeable.author.avatar,
                    )
                    sniped_count += 1

            await webhook.delete()
            await inter.send(f'Sniped **{sniped_count}** messages.', ephemeral=True)

        else:
            await inter.send('No messages were found in my list.', ephemeral=True)

    # senddm
    @commands.slash_command(
        name='senddm',
        description='Send DM to specific users.',
        options=[
            Option('member', 'Mention the server member.', OptionType.user, required=True),
            Option('msg', 'Message you want to send.', OptionType.string, required=True),
        ],
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def senddm(
        self, inter: disnake.CommandInteraction, member: disnake.Member, msg: str
    ) -> None:
        embed = (
            core.TypicalEmbed(inter)
            .add_field('Message: ', msg)
            .set_title(value=f'{inter.author.display_name} has sent you a message!')
            .set_thumbnail(url=inter.author.avatar.url)
        )

        await member.send(embed=embed)
        await inter.send('Your message has been delivered!', ephemeral=True)

    # pins
    @commands.slash_command(
        name='pins',
        description='Shows all pinned messages in the current channel.',
        dm_permission=False,
    )
    async def _pins(self, inter: disnake.CommandInteraction) -> None:
        embed = core.TypicalEmbed(inter).set_title(value='Pinned Messages  📌')
        pins = await inter.channel.pins()
        if pins:
            for count, pin in enumerate(pins):
                embed.add_field(
                    name=f'{count}. {pin.author.name}',
                    value=f'{pin.content} \n\n',
                    inline=False,
                )
        else:
            embed.set_description(value='There are no pinned messages in this channel.')

        await inter.send(embed=embed)

    # clearpins
    @commands.slash_command(
        name='clearpins',
        description='Clears all pinned messages in the current channel.',
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _clearpins(self, inter: disnake.CommandInteraction) -> None:
        pins = await inter.channel.pins()
        if pins:
            for pin in pins:
                await pin.unpin()
            await inter.send('All pins have been cleared!', ephemeral=True)
        else:
            await inter.send('There are no pins to clear!', ephemeral=True)

    # slowmode
    @commands.slash_command(
        name='slowmode',
        description='Sets slowmode for the current channel.',
        options=[
            Option(
                'seconds',
                'The amount of seconds to set the slowmode to. Set 0 to disable.',
                OptionType.integer,
                min_value=0,
                max_value=21600,
                choices=[
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
                required=True,
            )
        ],
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _slowmode(self, inter: disnake.CommandInteraction, seconds: int) -> None:
        await inter.channel.edit(slowmode_delay=seconds)
        await inter.send(f'Slowmode has been set to **{seconds}** seconds.')

    # add keyword to automod rule
    @commands.slash_command(
        name='banword',
        description='Add keywords to ban.',
        options=[
            Option(
                'keywords',
                'The keywords you want to add to the automod rule, separated by comma.',
                OptionType.string,
                required=True,
            )
        ],
        dm_permission=False,
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _banword(self, inter: disnake.CommandInteraction, keywords: str) -> None:

        keywords = keywords.split(',')
        try:
            rules = await inter.guild.fetch_automod_rules()
            for i in rules:
                if i.name == 'Igknite Banwords':
                    rule = i
                    break
            else:
                rule = None
        except disnake.NotFound:
            rule = None

        if rule is None:
            rule = await inter.guild.create_automod_rule(
                name='Igknite Banwords',
                event_type=disnake.AutoModEventType.message_send,
                trigger_type=disnake.AutoModTriggerType.keyword,
                trigger_metadata=disnake.AutoModTriggerMetadata(keyword_filter=[]),
                actions=[disnake.AutoModBlockMessageAction()],
                enabled=True,
            )
        meta = rule.trigger_metadata
        await rule.edit(
            trigger_metadata=meta.with_changes(
                keyword_filter=meta.keyword_filter + keywords,
            ),
        )
        await inter.send(f'Added `{keywords}` to the banword list.')


# The setup() function for the cog.
def setup(bot: core.IgKnite) -> None:
    bot.add_cog(Moderation(bot))
