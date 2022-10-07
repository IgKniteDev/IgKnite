'''
The `ExceptionHandler` cog for IgKnite.
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
from typing import Any

import disnake
from disnake.ext import commands

import core


# The actual cog.
class ExceptionHandler(commands.Cog):
    def __init__(
        self,
        bot: core.IgKnite
    ) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_slash_command_error(
        self,
        inter: disnake.CommandInteraction,
        error: Any
    ) -> None:
        error = getattr(error, 'original', error)
        embed = core.TypicalEmbed(inter, is_error=True)


        # BadLiteralArgument
        if isinstance(error, commands.errors.BadLiteralArgument):
            embed.set_title('Sorry, I couldn\'t read your input.')

        # ChannelNotFound
        if isinstance(error, commands.errors.ChannelNotFound):
            embed.set_title('Uh oh! It looks like that channel doesn\'t exist.')

        # LargeIntConversionFailure
        if isinstance(error, commands.errors.LargeIntConversionFailure):
            embed.set_title('Sorry, I can\'t count that high.')

        # MemberNotFound
        if isinstance(error, commands.errors.MemberNotFound):
            embed.set_title('I couldn\'t find a member with that name.')

        # MissingPermissions
        if isinstance(error, commands.errors.MissingPermissions):
            embed.set_title('Nice try! You don\'t have permission to do that.')

        # MissingRequiredArgument
        if isinstance(error, commands.errors.MissingRequiredArgument):
            embed.set_title('Don\'t leave me hanging. It looks like you\'re missing a field.')

        # MissingRole
        if (
            isinstance(error, commands.errors.MissingRole)
            or isinstance(error, commands.errors.MissingAnyRole)
        ):
            embed.set_title('Whoops! You\'re missing a role.')

        # RoleNotFound
        if isinstance(error, commands.errors.RoleNotFound):
            embed.set_title('I couldn\'t find that role.')

        # UserNotFound
        if isinstance(error, commands.errors.UserNotFound):
            embed.set_title('I don\'t know who that is.')

        else:
            embed.set_title('Whoops! An alien error occured.')

        embed.set_description(str(error))
        await inter.send(embed=embed, ephemeral=True)


# The setup() function for the cog.
def setup(bot: core.IgKnite) -> None:
    bot.add_cog(ExceptionHandler(bot))
