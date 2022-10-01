# Contribution Guidelines

We're glad to have you here with us in this project. Hope your ideas will shine in the whole workspace, and to do just that, we have written this comprehensive guide to help you set up, initialize and properly code on IgKnite.

When contributing to this repository, make sure to first discuss the change you wish to implement via [GitHub Issues](https://github.com/IgKniteDev/IgKnite/issues), [GitHub Discussions](https://github.com/IgKniteDev/IgKnite/discussions), email, the official [Discord server](https://discord.gg/ftVPgrw54A) or directly with me ([**@hitblast**](https://github.com/hitblast)) before actually pushing it to your own fork or copy.

We also have a [Code of Conduct](./CODE_OF_CONDUCT.md) in place so make sure to follow the given set of guidelines and thresholds while you interact with the project.

<br><br>

## Development Setup

If you'd like to have a complete walk-through on setting up the development environment for IgKnite, consider having a look at [this section (in progress)](https://igknition.ml/) of the official documentation. Once done, you can proceed with the next steps mentioned below.

<br><br>

## Add New Commands

As most of you Discord bot users have noticed already, the primary way of interacting with IgKnite is through commands. In order to add your ideas by implementing new commands, you'll have to follow through three steps accordingly:

<br>

### 1. Choose your "Cog"

On both [discord.py](https://github.com/Rapptz/discord.py) and [disnake](https://github.com/DisnakeDev/disnake), categories of commands are referred to as "cogs". There are six different cogs which come built-in with IgKnite located in the **cogs** subdirectory. Navigate to your chosen one and have a look at the source code before making any changes.

<br>

### 2. Create the command

Okay, now once you have decided which cog to add your command to, we can start writing some code now! 

Discord has three types of commands:

- **Slash commands** can be used by pressing `/` and then typing the command.
- **User commands** can be used by right-clicking on a user's avatar and then selecting 'Apps'.
- **Message commands** are similar to user commands but need you to click on a message instead of someone's avatar.

Below is an example of a very basic slash command which greets a server member. You'll be using such syntax in most of your commands.

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

<br>

On the other hand, you can also write code and deploy to all three types of commands at once! In the example given below, we've tried to make a ban command that uses the very same logic for deploying itself in three forms:

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

<br>

### 3. Test and deploy

IgKnite's source code follows the style guide provided by the [flake8](https://flake8.pycqa.org) linter. In order to minimize the tinkering, we have placed [GitHub Actions](https://github.com/features/actions) workflows to automatically lint and check your code for styling issues. 

We highly recommend using this workflow by enabling GitHub Actions inside your fork of IgKnite. You can do this via the repository settings and hopefully it'll greatly increase the overhead on you while coding!

Once you are done making your changes, push them to your fork and create a valid pull request. [Here's](https://github.com/IgKniteDev/IgKnite/pull/36) an example pull request which you can have a look at to learn about the pattern.
