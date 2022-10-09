'''
The `General` cog for IgKnite.
---

License can be found here:
https://github.com/IgKniteDev/IgKnite/blob/main/LICENSE
'''


# Imports.
import time

import disnake
from disnake import Option, OptionType
from disnake.ext import commands

import core


# The actual cog.
class General(commands.Cog):
    def __init__(
        self,
        bot: core.IgKnite
    ) -> None:
        self.bot = bot

    # Backend for userinfo-labelled commands.
    # Do not use it within other commands unless really necessary.
    async def _avatar_backend(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member = None
    ) -> None:
        member = inter.author if not member else member

        embed = core.TypicalEmbed(inter).set_title(
            value='Here\'s what I found!'
        ).set_image(
            url=member.avatar
        )
        await inter.send(embed=embed)

    @commands.slash_command(
        name='avatar',
        description='Displays your avatar / the avatar of a server member.',
        options=[
            Option(
                'member',
                'Mention the server member.',
                OptionType.user
            )
        ],
        dm_permission=False
    )
    async def _avatar(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member = None
    ) -> None:
        await self._avatar_backend(inter, member)

    # avatar (user)
    @commands.user_command(
        name='Show Avatar'
    )
    async def _avatar_user(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member
    ) -> None:
        await self._avatar_backend(inter, member)

    # ping
    @commands.slash_command(
        name='ping',
        description='Shows my current response time.'
    )
    async def _ping(
        self,
        inter: disnake.CommandInteraction
    ) -> None:
        system_latency = round(self.bot.latency * 1000)

        start_time = time.time()
        await inter.response.defer()
        end_time = time.time()

        api_latency = round((end_time - start_time) * 1000)
        
        cpu_usage = round(self.bot.process.cpu_percent())
        
        ram_usage = round(self.bot.process.memory_full_info().uss / 1024 / 1024)
        
        embed = core.TypicalEmbed(inter).add_field(
            name='System Latency',
            value=f'{system_latency}ms [{self.bot.shard_count} shard(s)]',
            inline=False
        ).add_field(
            name='API Latency',
            value=f'{api_latency}ms'
        ).add_field(
            name='uptime',
            value=f'{round(self.bot.uptime / 3600)}h {round(self.bot.uptime / 60)}m {round(self.bot.uptime % 60)}s'
        ).add_field(
            name='performance',
            value=f'{cpu_usage}% CPU usage, {ram_usage}MB RAM usage'
        )
        
        await inter.send(embed=embed)


# The setup() function for the cog.
def setup(bot: core.IgKnite) -> None:
    bot.add_cog(General(bot))
