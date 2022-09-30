# Contribution Guidelines

When contributing to this repository, make sure to first discuss the change you wish to implement via [GitHub Issues](https://github.com/IgKniteDev/IgKnite/issues), [GitHub Discussions](https://github.com/IgKniteDev/IgKnite/discussions), email, the official [Discord server](https://discord.gg/ftVPgrw54A) or directly with me ([**@hitblast**](https://github.com/hitblast)) before actually pushing it to your own fork or copy.

We also have a [Code of Conduct](./CODE_OF_CONDUCT.md) in place so make sure to follow the given set of guidelines and thresholds while you interact with the project!

<br><br>

## Adding a New Command

As most of you Discord bot users have noticed already, the primary way of interacting with IgKnite is through commands. And by commands, there are actually three types of commands which the project mainly focuses on: **slash commands, message commands and user commands.**

In order to add your ideas by implementing new commands, you'll have to follow through three steps accordingly:

<br>

### 1. Choosing your "Cog"

On both [discord.py](https://github.com/Rapptz/discord.py) and [disnake](https://github.com/DisnakeDev/disnake), categories of commands are referred to as "cogs". There are six different cogs which come built-in with IgKnite located in the **cogs** subdirectory. Navigate to your chosen one and have a look at the source code before making any changes.

<br>

### 2. Adding the actual command

Okay, now once you have decided which cog to add your command to, we can start writing some code now! Below is an example of a very basic slash command which greets a server member. You'll be using such syntax in most of your commands.

```python
class SomeCog(commands.Cog):
    ...

    @commands.slash_command(
        name='greet',
        description='Greets a member!',
        options=[
            Option(
                'member',
                'Mention the server member.',
                OptionType.user,  # disnake.OptionType
                required=True  # not needed if False
            )
        ],
        dm_permission=False  # cannot be used in DMs
    )
    async def _greet(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member
    ) -> None:
        await member.send(
            f'Hey there! Welcome to {inter.guild.name}.'  
        )

    
```

On the other hand, if you'd like to add all three types of commands with the very same logic, you can do something similar to this example given below:

Things to note here:

- Slash commands can be used by pressing `/` and then typing the command.
- User commands can be used by right-clicking on a user's avatar and then selecting 'Apps'.
- Message commands are similar to user commands but need you to click on a message instead of someone's avatar.

```python
    # Backend for ban-labelled commands.
    # Do not use it within other commands unless really necessary.
    async def _ban_backend(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member,
        reason: str = 'No reason provided.'
    ) -> None:
        await inter.guild.ban(
            member,
            reason=reason
        )
        await inter.send(f'Member **{member.display_name}** has been banned! Reason: {reason}')
    
    # ban (slash)
    @commands.slash_command(
        name='ban',
        description='Bans a member.',
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
    async def _ban(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member,
        reason: str = 'No reason provided.'
    ):
        await self._ban_backend(inter, member, reason=reason)

    # ban (user)
    @commands.user_command(
        name='Ban',
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _ban_user(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member
    ) -> None:
        await self._ban_backend(inter, member)

    # ban (message)
    @commands.message_command(
        name='Ban',
        dm_permission=False
    )
    @commands.has_any_role(LockRoles.mod, LockRoles.admin)
    async def _ban_message(
        self,
        inter: disnake.CommandInteraction,
        message: disnake.Message
    ) -> None:
        await self._ban_backend(inter, message.author)
    ...
```