# SPDX-License-Identifier: MIT


# Imports.


from disnake.ext import commands
from disnake.ext.commands import errors

import core


class Admin(commands.Cog):
    @commands.command(name='reloadext')
    async def reload_extension(
        self, ctx: commands.Context[core.IgKnite], name: str
    ) -> None:
        try:
            ctx.bot.reload_extension(name)
        except Exception as e:
            if isinstance(e, errors.ExtensionNotLoaded):
                msg = f'`{name}` extension is not loaded.'
            elif isinstance(e, errors.ExtensionNotFound):
                msg = f'No extension with name `{name}` exists.'
            elif isinstance(e, errors.ExtensionFailed):
                msg = f'Failed to load `{name}` extension.'
            elif isinstance(e, errors.NoEntryPointError):
                msg = f'Setup function is not defined in `{name}` file.'
            # getting here shouldnt happen, just making sure msg
            # doesnt have an Unbound type.
            else:
                msg = f'Something went wrong while loading `{name}` extension.'

            embed = core.TypicalEmbed(description=msg, is_error=True)
            await ctx.send(embed=embed)
        else:
            embed = core.TypicalEmbed(
                description=f'Successfully reloaded `{name}` extension.'
            )
            await ctx.send(embed=embed)

    @reload_extension.error
    async def reload_ext(
        self, ctx: commands.Context[core.IgKnite], error: errors.CommandError
    ) -> None:
        if isinstance(error, errors.MissingRequiredArgument):
            embed = core.TypicalEmbed(
                description='Please provide an extension name.', is_error=True
            )
            await ctx.send(embed=embed)
        # a check failure would be raised when someone who is not
        # an owner uses the command but we dont wanna catch it,
        # since we dont wanna send any messages if someone who
        # isn't an owner uses the command.

    async def cog_check(self, ctx: commands.Context[core.IgKnite]) -> bool:
        return await ctx.bot.is_owner(ctx.author)


def setup(bot: core.IgKnite) -> None:
    bot.add_cog(Admin())
