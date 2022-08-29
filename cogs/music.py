'''
The `Music` cog for IgKnite.
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
import math
import random
import asyncio
from async_timeout import timeout
import functools
import itertools
from typing import Any, Tuple

import youtube_dl
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import discord
from discord import app_commands
from discord.ext import commands

import core
from core import global_


# Bug reports message.
youtube_dl.utils.bug_reports_message = lambda: ''

# Creating a spotipy.Spotify instance.
spotify = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=global_.identifiers['spotify_client'],
        client_secret=global_.tokens['spotify']
    )
)


# Custom exceptions for music commands.
class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass


# YTDLSource class for handling sources.
class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)
    ytdl.cache.remove()

    def __init__(
        self,
        inter: discord.Interaction,
        source: discord.FFmpegPCMAudio,
        *,
        data: dict,
        volume: float = 0.5
    ) -> None:
        super().__init__(source, volume)

        self.requester = inter.user
        self.channel = inter.channel
        self.data = data

        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')

        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]

        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return '**{0.title}** by **[{0.uploader}]({0.uploader_url})**'.format(self)

    @classmethod
    async def create_source(
        cls,
        inter: discord.Interaction,
        search: str,
        *,
        loop: asyncio.BaseEventLoop
    ):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError(f'Anything matching **{search}** couldn\'t be found.')

        if 'entries' not in data:
            process_info = data

        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError(f'Anything matching **{search}** couldn\'t be found.')

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError(f'Couldn\'t fetch **{webpage_url}**')

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None

            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError(f'Any matches for {webpage_url} couldn\'t be retrieved.')

        return cls(inter, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

    @staticmethod
    def parse_duration(duration: int) -> str:
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append(f'{days} days')
        if hours > 0:
            duration.append(f'{hours} hours')
        if minutes > 0:
            duration.append(f'{minutes} minutes')
        if seconds > 0:
            duration.append(f'{seconds} seconds')

        return ', '.join(duration)


# Base class for interacting with the Spotify API.
class Spotify:
    @classmethod
    def get_track_id(
        self,
        track: Any
    ):
        track = spotify.track(track)
        return track['id']

    @classmethod
    def get_playlist_track_ids(
        self,
        playlist_id: Any
    ):
        ids = []
        playlist = spotify.playlist(playlist_id)

        for item in playlist['tracks']['items']:
            track = item['track']
            ids.append(track['id'])

        return ids

    @classmethod
    def get_album(
        self,
        album_id: Any
    ):
        album = spotify.album_tracks(album_id)
        return [item['id'] for item in album['items']]

    @classmethod
    def get_album_id(
        self,
        id: Any
    ):
        return spotify.album(id)

    @classmethod
    def get_track_features(
        self,
        id: Any
    ) -> str:
        meta = spotify.track(id)
        album = meta['album']['name']
        artist = meta['album']['artists'][0]['name']
        return f'{artist} - {album}'


# View for the `now` command.
class NowCommandView(discord.ui.View):
    message: discord.Message

    def __init__(
        self,
        inter: discord.Interaction,
        url: str,
        timeout: float = 35
    ) -> None:
        super().__init__(timeout=timeout)

        self.inter = inter
        self.add_item(discord.ui.Button(label='Redirect', url=url))

    @discord.ui.button(label='Toggle Loop', style=discord.ButtonStyle.gray)
    async def loop(
        self,
        button: discord.ui.Button,
        inter: discord.MessageInteraction
    ) -> None:
        self.inter.voice_state.loop = not self.inter.voice_state.loop

        if not self.inter.voice_state.loop:
            button.label = 'Enable Loop'
            button.style = discord.ButtonStyle.green
        else:
            button.label = 'Disable Loop'
            button.style = discord.ButtonStyle.red

        await inter.response.edit_message(view=self)

    async def on_timeout(self) -> None:
        for children in self.children:
            if 'Loop' in children.label:
                children.disabled = True

        await self.message.edit(view=self)


# View for the `play` command.
class PlayCommandView(discord.ui.View):
    def __init__(
        self,
        url: str,
        timeout: float = 35
    ) -> None:
        super().__init__(timeout=timeout)

        self.add_item(discord.ui.Button(label='Redirect', url=url))


# View for the `queue` command.
class QueueCommandView(discord.ui.View):
    message: discord.Message

    def __init__(
        self,
        inter: discord.Interaction,
        timeout: float = 35
    ) -> None:
        super().__init__(timeout=timeout)
        self.inter = inter

    @discord.ui.button(label='Clear Queue', style=discord.ButtonStyle.danger)
    async def clear(
        self,
        button: discord.ui.Button,
        inter: discord.MessageInteraction
    ) -> None:
        self.inter.voice_state.songs.clear()

        button.label = 'Cleared'
        button.style = discord.ButtonStyle.gray

        for children in self.children:
            children.disabled = True

        await inter.response.edit_message(
            embed=self.inter.voice_state.songs.get_queue_embed(self.inter, page=1),
            view=self
        )

    @discord.ui.button(label='Shuffle', style=discord.ButtonStyle.gray)
    async def shuffle(
        self,
        button: discord.ui.Button,
        inter: discord.MessageInteraction
    ) -> None:
        self.inter.voice_state.songs.shuffle()

        button.label = 'Shuffled'
        button.disabled = True

        await inter.response.edit_message(
            embed=self.inter.voice_state.songs.get_queue_embed(self.inter, page=1),
            view=self
        )

    async def on_timeout(self) -> None:
        for children in self.children:
            children.disabled = True

        await self.message.edit(view=self)


# The Song class which represents the instance of a song.
class Song:
    __slots__ = ('source', 'requester')

    def __init__(
        self,
        source: YTDLSource
    ) -> None:
        self.source = source
        self.requester = source.requester

    def create_embed(
        self,
        inter: discord.Interaction
    ) -> Tuple[discord.Embed, discord.ui.View]:
        duration = 'Live' if not self.source.duration else self.source.duration

        embed = core.embeds.ClassicEmbed(inter).add_field(
            name='Duration',
            value=duration
        ).add_field(
            name='Requester',
            value=self.requester.mention
        ).set_image(
            url=self.source.thumbnail
        )
        embed.title = self.source.title
        view = NowCommandView(inter=inter, url=self.source.url)

        return embed, view


# The SongQueue class, which represents the queue of songs for a particular Discord server.
class SongQueue(asyncio.Queue):
    def __getitem__(
        self,
        item: Any
    ) -> Any | list:
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self) -> Any:
        return self._queue.__iter__()

    def __len__(self) -> int:
        return self.qsize()

    def clear(self) -> None:
        self._queue.clear()

    def shuffle(self) -> None:
        random.shuffle(self._queue)

    def remove(
        self,
        index: int
    ) -> None:
        del self._queue[index]

    def get_queue_embed(
        self,
        inter: discord.Interaction,
        page: int = 1
    ) -> discord.Embed:
        items_per_page = 10
        pages = math.ceil(len(inter.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue_str = ''.join(
            '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)
            for i, song in enumerate(inter.voice_state.songs[start:end], start=start)
        )

        embed = core.embeds.ClassicEmbed(inter).set_footer(
            text=f'Viewing page {page}/{pages}'
        )
        embed.description = f'**{len(inter.voice_state.songs)} tracks:**\n\n{queue_str}'

        return embed


# The VoiceState class, which represents the playback status of songs.
class VoiceState:
    def __init__(
        self,
        bot: core.IgKnite,
        inter: discord.Interaction
    ) -> None:
        self.bot = bot
        self._inter = inter

        self.current = None
        self.voice = None
        self.exists = True
        self.next = asyncio.Event()
        self.songs = SongQueue()

        self._loop = False
        self._volume = 0.5
        self.skip_votes = set()

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self) -> None:
        self.audio_player.cancel()

    @property
    def loop(self) -> bool:
        return self._loop

    @loop.setter
    def loop(
        self,
        value: bool
    ) -> None:
        self._loop = value

    @property
    def volume(self) -> float:
        return self._volume

    @volume.setter
    def volume(
        self,
        value: float
    ) -> None:
        self._volume = value

    @property
    def is_playing(self) -> Any:
        return self.voice and self.current

    async def audio_player_task(self) -> None:
        while True:
            self.next.clear()
            self.now = None

            if not self.loop:
                try:
                    async with timeout(180):
                        self.current = await self.songs.get()

                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    self.exists = False
                    return

                self.current.source.volume = self._volume
                self.voice.play(self.current.source, after=self.play_next_song)

            elif self.loop:
                self.now = discord.FFmpegPCMAudio(self.current.source.stream_url, **YTDLSource.FFMPEG_OPTIONS)
                self.voice.play(self.now, after=self.play_next_song)

            await self.next.wait()

    def play_next_song(
        self,
        error=None
    ) -> None:
        if error:
            raise VoiceError(str(error))

        self.next.set()

    def skip(self) -> None:
        self.skip_votes.clear()

        if self.is_playing:
            self.voice.stop()

    async def stop(self) -> None:
        self.songs.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None


# Music commands.
class Music(commands.Cog):
    def __init__(
        self,
        bot: core.IgKnite
    ) -> None:
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(
        self,
        inter: discord.Interaction
    ) -> VoiceState:
        state = self.voice_states.get(inter.guild.id)

        if (
            not state
            or not state.exists
        ):
            state = VoiceState(self.bot, inter)
            self.voice_states[inter.guild.id] = state

        return state

    def cog_unload(self) -> None:
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def ensure_voice_state(func):
        @functools.wraps(func)
        async def callback(
            self,
            inter: discord.Interaction,
            *args,
            **kwargs
        ) -> None:
            inter.extras['voice_state'] = self.get_voice_state(inter)
            await inter.response.defer()
            await func(self, inter, *args, **kwargs)

        return callback

    @app_commands.command(
        name='join',
        description='Joins the voice channel that you\'re in.',
    )
    @app_commands.guild_only()
    @ensure_voice_state
    async def _join(
        self,
        inter: discord.Interaction
    ) -> None:
        destination = inter.user.voice.channel
        state = inter.extras['voice_state']

        if state.voice:
            await state.voice.move_to(destination)
        else:
            state.voice = await destination.connect()

        await inter.followup.send(f'Joined **{destination}.**')


# The setup() function for the cog.
async def setup(bot: core.IgKnite) -> None:
    await bot.add_cog(Music(bot))
