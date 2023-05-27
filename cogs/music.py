'''
The `Music` cog for IgKnite.
---

License can be found here:
https://github.com/IgKniteDev/IgKnite/blob/main/LICENSE
'''


# Imports.
import asyncio
import functools
import itertools
import math
import random
from typing import Any, Self, Tuple

import disnake
import spotipy
import yt_dlp
from async_timeout import timeout
from disnake import ChannelType
from disnake.ext import commands
from disnake.ext.commands import Param
from disnake.utils import MISSING
from spotipy.oauth2 import SpotifyClientCredentials

import core
from core.chain import keychain

# Suppress noise about console usage from errors.
yt_dlp.utils.bug_reports_message = lambda: ''

# Creating a spotipy.Spotify instance.
spotify = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=keychain.spotify_client_id, client_secret=keychain.spotify_client_secret
    )
)


# Custom exceptions for music commands.
class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass


# YTDLSource class for handling sources.
class YTDLSource(disnake.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
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

    ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)
    ytdl.cache.remove()

    def __init__(
        self,
        inter: disnake.CommandInteraction,
        source: disnake.FFmpegPCMAudio,
        *,
        data: dict,
        volume: float = 0.5,
    ) -> None:
        super().__init__(source, volume)

        self.requester = inter.author
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
        inter: disnake.CommandInteraction,
        search: str,
        *,
        loop: asyncio.BaseEventLoop,
    ) -> Self:
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

        return cls(inter, disnake.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

    @staticmethod
    def parse_duration(duration: int) -> str:
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append(f'{days}')
        if hours > 0:
            duration.append(f'{hours}')
        if minutes > 0:
            duration.append(f'{minutes}')
        if seconds > 0:
            duration.append(f'{seconds}')

        return ':'.join(duration)


# YTDLSource class with equalized playback.
# Note: This feature is still work-in-progress and the audio filters need to be improved.
class YTDLSourceBoosted(YTDLSource):
    '''
    A child class of `YTDLSource` for serving equalized playback.
    '''

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn -af "equalizer=f=60:g=2,bass=f=120:g=10.8,equalizer=f=150:g=1,'
        + 'treble=f=400:t=q:w=4:g=-2"',
    }


# Base class for interacting with the Spotify API.
class Spotify:
    @staticmethod
    def get_track_id(track: Any):
        track = spotify.track(track)
        return track['id']

    @staticmethod
    def get_playlist_track_ids(playlist_id: Any):
        ids = []
        playlist = spotify.playlist(playlist_id)

        for item in playlist['tracks']['items']:
            track = item['track']
            ids.append(track['id'])

        return ids

    @staticmethod
    def get_album(album_id: Any):
        album = spotify.album_tracks(album_id)
        return [item['id'] for item in album['items']]

    @staticmethod
    def get_album_id(id: Any):
        return spotify.album(id)

    @staticmethod
    def get_track_features(id: Any) -> str:
        meta = spotify.track(id)
        name = meta['name']
        album = meta['album']['name']
        artist = meta['album']['artists'][0]['name']
        return f'{artist} - {name} ({album})'


# The Song class which represents the instance of a song.
class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource) -> None:
        self.source = source
        self.requester = source.requester

    def create_embed(
        self, inter: disnake.CommandInteraction
    ) -> Tuple[core.TypicalEmbed, disnake.ui.View]:
        duration = self.source.duration or 'Live'

        embed = (
            core.TypicalEmbed(inter)
            .set_title(self.source.title)
            .add_field(name='Duration', value=duration)
            .add_field(name='Requester', value=self.requester.mention)
            .set_image(url=self.source.thumbnail)
        )
        view = NowCommandView(url=self.source.url, volume=inter.voice_state.volume)

        return embed, view


# The SongQueue class, which represents the queue of songs for a particular Discord server.
class SongQueue(asyncio.Queue):
    def __getitem__(self, item: Any) -> Any | list:
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

    def remove(self, index: int) -> None:
        del self._queue[index]


# The VoiceState class, which represents the playback status of songs.
class VoiceState:
    def __init__(self, bot: core.IgKnite) -> None:
        self.bot = bot

        self.current = None
        self.voice: disnake.VoiceProtocol | None = None
        self.exists = True
        self.next = asyncio.Event()
        self.songs = SongQueue()

        self._loop = False
        self._volume = 0.5
        self._boosted = False
        self.skip_votes = set()

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self) -> None:
        self.audio_player.cancel()

    @property
    def loop(self) -> bool:
        return self._loop

    @loop.setter
    def loop(self, value: bool) -> None:
        self._loop = value

    @property
    def volume(self) -> float:
        return self._volume

    @volume.setter
    def volume(self, value: float) -> None:
        self._volume = value

    @property
    def boosted(self) -> bool:
        return self._boosted

    @boosted.setter
    def boosted(self, value: bool) -> None:
        self._boosted = value

    @property
    def is_playing(self) -> Any:
        return self.voice and self.voice.is_playing()

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
                self.now = disnake.FFmpegPCMAudio(
                    self.current.source.stream_url,
                    **(
                        YTDLSource.FFMPEG_OPTIONS
                        if not self._boosted
                        else YTDLSourceBoosted.FFMPEG_OPTIONS
                    ),
                )
                self.voice.play(self.now, after=self.play_next_song)

            await self.next.wait()

    async def play_song(self, song_index) -> None:
        removed_songs = []
        songs = self.songs
        songs = list(songs)

        for idx, _ in enumerate(songs):
            if idx != song_index:
                removed_songs.append(await self.songs.get())
            else:
                break

        for removed in removed_songs:
            await self.songs.put(removed)

        self.skip()

    def play_next_song(self, error=None) -> None:
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


# View for the `now` command.
class NowCommandView(disnake.ui.View):
    def __init__(self, *, url: str, volume: float, timeout: float = 60) -> None:
        super().__init__(timeout=timeout)

        self.add_item(disnake.ui.Button(label='Redirect', url=url))
        self.add_item(disnake.ui.Button(label=f'Volume: {int(volume*100)}'))


# View for the `queue` command.
class QueueCommandView(disnake.ui.View):
    def __init__(
        self,
        inter: disnake.CommandInteraction,
        *,
        page_loader,
        top_page: int = 1,
        page: int = 1,
        timeout: float = 60,
    ) -> None:
        super().__init__(timeout=timeout)
        self.inter = inter
        self.cleared = False

        self.page_loader = page_loader
        self.top_page = top_page
        self.page = page

        if self.page + 1 > self.top_page:
            self.children[2].disabled = True

    def paginator_logic(self) -> None:
        if self.page == 1:
            self.children[0].disabled = True
        else:
            self.children[0].disabled = False

        if self.page + 1 > self.top_page:
            self.children[2].disabled = True
        else:
            self.children[2].disabled = False

    @disnake.ui.button(label='< Previous', style=disnake.ButtonStyle.gray, disabled=True)
    async def previous(self, _: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.page -= 1
        self.paginator_logic()

        embed = await self.page_loader(self.page)
        await inter.response.edit_message(
            embed=embed,
            view=self,
        )

    @disnake.ui.button(label='Clear Queue!', style=disnake.ButtonStyle.danger)
    async def clear_queue(self, _: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.inter.voice_state.songs.clear()
        self.cleared = True

        await inter.response.edit_message(
            'Your queue has been cleared!',
            embed=None,
            view=None,
        )

    @disnake.ui.button(label='Next >', style=disnake.ButtonStyle.gray)
    async def next(self, _: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.page += 1
        self.paginator_logic()

        embed = await self.page_loader(self.page)
        await inter.response.edit_message(
            embed=embed,
            view=self,
        )

    async def on_timeout(self) -> None:
        if not self.cleared:
            for child in self.children:
                child.disabled = True

            await self.inter.edit_original_message(view=self)


# The actual cog.
class Music(commands.Cog):
    def __init__(self, bot: core.IgKnite) -> None:
        self.bot = bot
        self.voice_states = {}

    def cog_unload(self) -> None:
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def init_voice_state(self, inter: disnake.CommandInteraction) -> VoiceState:
        '''
        A method that initializes the `VoiceState` object for a specific guild.
        '''

        state = self.voice_states.get(inter.guild.id)

        if not state or not state.exists:
            state = VoiceState(self.bot)
            self.voice_states[inter.guild.id] = state

        return state

    def get_voice_state(self, guild_id: int) -> VoiceState | None:
        '''
        A method that returns the `VoiceState` object for the given guild ID (if any).
        '''

        try:
            return self.voice_states[guild_id]
        except KeyError:
            pass

    @commands.Cog.listener()
    async def on_voice_state_update(
        self, member: disnake.Member, before: disnake.VoiceState, after: disnake.VoiceState
    ) -> None:
        if not (state := self.get_voice_state(member.guild.id)):
            return

        if member != self.bot.user:
            if (
                before.channel
                and not after.channel
                and self.bot.user in before.channel.members
                and len(before.channel.members) == 1
                and state.is_playing
            ):
                state.voice.pause()
                await member.send('Playback has been paused since nobody\'s in the voice channel.')

            elif (
                not before.channel
                and after.channel
                and self.bot.user in after.channel.members
                and len(after.channel.members) == 2
                and state.voice.is_paused()
            ):
                state.voice.resume()
                await member.send('Playback from a previous listening session has been resumed.')

        else:
            if not member.voice:
                try:
                    state.voice.cleanup()
                except AttributeError:
                    pass

                await state.stop()
                del self.voice_states[member.guild.id]

            elif not before.mute and after.mute and state.is_playing:
                state.voice.pause()

            elif before.mute and not after.mute and state.voice.is_paused():
                state.voice.resume()

    async def cog_before_slash_command_invoke(self, inter: disnake.CommandInteraction) -> None:
        inter.voice_state = self.init_voice_state(inter)
        return await inter.response.defer()

    async def cog_before_message_command_invoke(self, inter: disnake.CommandInteraction) -> None:
        inter.voice_state = self.init_voice_state(inter)
        return await inter.response.defer()

    async def cog_before_user_command_invoke(self, inter: disnake.CommandInteraction) -> None:
        inter.voice_state = self.init_voice_state(inter)
        return await inter.response.defer()

    # A coroutine for ensuring proper voice safety during playback.
    async def _ensure_voice_safety(
        self, inter: disnake.CommandInteraction, skip_self: bool = False
    ) -> Any | None:
        if (not skip_self) and (not inter.voice_state.voice):
            return await inter.send('I\'m not inside any voice channel.', ephemeral=True)
        elif (
            not inter.author.voice or inter.author.voice.channel != inter.voice_state.voice.channel
        ):
            return await inter.send('You\'re not in my voice channel.', ephemeral=True)
        else:
            return True

    # A coroutine for commands which sets the destination voice channel of the bot
    # as needed. Commonly used in play-labelled commands.
    async def _join_logic(
        self,
        inter: disnake.CommandInteraction,
        channel: disnake.VoiceChannel | disnake.StageChannel | None = None,
    ) -> Any | None:
        destination = channel or (inter.author.voice and inter.author.voice.channel)

        try:
            if inter.voice_state.voice:
                await inter.voice_state.voice.move_to(destination)
            else:
                inter.voice_state.voice = await destination.connect()

            return destination

        except AttributeError:
            await inter.send(
                'Please switch to a voice or stage channel to use this command.', ephemeral=True
            )

    # join
    @commands.slash_command(
        name='join',
        description='Joins the voice channel you\'re in. '
        + 'You can also specify which channel to join.',
        dm_permission=False,
    )
    async def _join(
        self,
        inter: disnake.CommandInteraction,
        channel: disnake.VoiceChannel
        | disnake.StageChannel = Param(
            description='Specify a channel to join.',
            default=None,
            channel_types=[ChannelType.voice, ChannelType.stage_voice],
        ),
    ) -> None:
        destination = await self._join_logic(inter, channel)
        await inter.send(
            f'Joined **{destination}.**'
            if destination is not channel
            else f'Got booped to **{destination}.**'
        )

    # leave
    @commands.slash_command(
        name='leave',
        description='Clears the queue and leaves the voice channel.',
        dm_permission=False,
    )
    async def _leave(self, inter: disnake.CommandInteraction) -> None:
        if not await self._ensure_voice_safety(inter):
            return

        await inter.voice_state.stop()
        del self.voice_states[inter.guild.id]
        await inter.send('Left voice state.')

    # volume
    @commands.slash_command(
        name='volume',
        description='Sets the volume of the current track.',
        dm_permission=False,
    )
    async def _volume(
        self,
        inter: disnake.CommandInteraction,
        volume: float = Param(
            description='The amount of volume to set in percentage.', min_value=1, max_value=200
        ),
    ) -> None:
        if not await self._ensure_voice_safety(inter):
            return
        elif not inter.voice_state.is_playing:
            return await inter.send('There\'s nothing being played at the moment.', ephemeral=True)

        inter.voice_state.current.source.volume = (vol_mod := volume / 100)
        inter.voice_state.volume = vol_mod

        await inter.send(
            f'Volume of the player is now set to **{volume}%**'
            + (' (⚠️ reduced quality) ' if volume > 100 else '')
        )

    # now
    @commands.slash_command(
        name='now',
        description='Displays an interactive control view for the current song.',
        dm_permission=False,
    )
    async def _now(self, inter: disnake.CommandInteraction) -> None:
        if inter.voice_state.is_playing:
            embed, view = inter.voice_state.current.create_embed(inter)
            await inter.send(embed=embed, view=view)

        else:
            await inter.send('There\'s nothing being played at the moment.', ephemeral=True)

    # pause
    @commands.slash_command(
        name='pause',
        description='Pauses the currently playing song.',
        dm_permission=False,
    )
    async def _pause(self, inter: disnake.CommandInteraction) -> None:
        if not await self._ensure_voice_safety(inter):
            return

        if inter.voice_state.is_playing:
            inter.voice_state.voice.pause()
            await inter.send('Paused voice state.')
        else:
            await inter.send('There\'s nothing being played at the moment.', ephemeral=True)

    # resume
    @commands.slash_command(
        name='resume',
        description='Resumes the currently paused song.',
        dm_permission=False,
    )
    async def _resume(self, inter: disnake.CommandInteraction) -> None:
        if not await self._ensure_voice_safety(inter):
            return

        if inter.voice_state.voice.is_paused():
            inter.voice_state.voice.resume()
            await inter.send('Resumed voice state.')
        else:
            await inter.send(
                'Playback isn\'t paused to be resumed in the first place.', ephemeral=True
            )

    # stop
    @commands.slash_command(
        name='stop',
        description='Stops playing song and clears the queue.',
        dm_permission=False,
    )
    async def _stop(self, inter: disnake.CommandInteraction) -> None:
        if not await self._ensure_voice_safety(inter):
            return

        inter.voice_state.songs.clear()

        if inter.voice_state.is_playing:
            if inter.voice_state.loop:
                inter.voice_state.loop = not inter.voice_state.loop

            inter.voice_state.voice.stop()
            await inter.send('Stopped voice state.')

    # skip
    @commands.slash_command(
        name='skip',
        description='Vote to skip a song. The requester can automatically skip.',
        dm_permission=False,
    )
    async def _skip(self, inter: disnake.CommandInteraction) -> None:
        if not await self._ensure_voice_safety(inter):
            return
        elif not inter.voice_state.is_playing:
            return await inter.send('There\'s nothing being played at the moment.', ephemeral=True)

        if inter.voice_state.loop:
            inter.voice_state.loop = not inter.voice_state.loop

        voter = inter.author

        if (
            voter == inter.voice_state.current.requester
            or len(inter.voice_state.voice.channel.members) == 2
        ):
            await inter.send('Skipped!')
            inter.voice_state.skip()

        elif voter.id not in inter.voice_state.skip_votes:
            inter.voice_state.skip_votes.add(voter.id)
            total_votes = len(inter.voice_state.skip_votes)
            required_votes = round(len(inter.voice_state.voice.channel.members) / 2)

            if total_votes >= required_votes:
                await inter.send('Skipped!')
                inter.voice_state.skip()
            else:
                await inter.send(
                    f'Skip vote added, currently at **{total_votes}/{required_votes}** votes.'
                )

        else:
            await inter.send('You have already voted to skip this song.', ephemeral=True)

    # queue
    @commands.slash_command(
        name='queue', description='Shows the player\'s queue.', dm_permission=False
    )
    async def _queue(self, inter: disnake.CommandInteraction) -> None:
        if not await self._ensure_voice_safety(inter):
            return
        elif len(songs := inter.voice_state.songs) == 0:
            return await inter.send('The queue is empty.', ephemeral=True)

        page = 1
        songs_per_page = 5
        top_page = math.ceil(len(songs) / songs_per_page)

        async def page_loader(page_num: int) -> core.TypicalEmbed:
            page = page_num

            embed = (
                core.TypicalEmbed(inter)
                .set_title('Current Queue')
                .set_footer(text=f'{page}/{top_page}')
            )

            for i in range(
                (page_num * songs_per_page) - songs_per_page,
                page_num * songs_per_page,
            ):
                if i < len(songs):
                    source = songs[i].source

                    embed.add_field(
                        name=f'{i + 1} - `{source.title}`',
                        value=f'🔗 [Redirect]({songs[i].source.url}) '
                        f' **|** 🕑 {source.duration} \n\n',
                        inline=False,
                    )

            return embed

        embed = await page_loader(page)
        await inter.send(
            embed=embed,
            view=QueueCommandView(
                inter,
                page_loader=page_loader,
                top_page=top_page,
                page=page,
            )
            if songs
            else MISSING,
        )

    # rmqueue
    @commands.slash_command(
        name='rmqueue',
        description='Removes a song from the queue at a given index.',
        dm_permission=False,
    )
    async def _rmqueue(
        self,
        inter: disnake.CommandInteraction,
        index: int = Param(
            description='Specify the index of the song to remove. Defaults to the first song.',
            default=1,
        ),
    ):
        if not await self._ensure_voice_safety(inter):
            return
        elif len(inter.voice_state.songs) == 0:
            return await inter.send('The queue is empty, so nothing to be removed.', ephemeral=True)

        inter.voice_state.songs.remove(index - 1)
        await inter.send('Removed item from queue.')

    # shuffle
    @commands.slash_command(
        name='shuffle', description='Shuffles the current queue.', dm_permission=False
    )
    async def _shuffle(self, inter: disnake.CommandInteraction) -> None:
        if not await self._ensure_voice_safety(inter):
            return

        inter.voice_state.songs.shuffle()
        await inter.send('Shuffled your queue!')

    # loop
    @commands.slash_command(
        name='loop', description='Toggles loop for the current song.', dm_permission=False
    )
    async def _loop(self, inter: disnake.CommandInteraction) -> None:
        if not await self._ensure_voice_safety(inter):
            return

        inter.voice_state.loop = not inter.voice_state.loop
        await inter.send(f"Loop has been {'enabled' if inter.voice_state.loop else 'disabled'}!")

    # Common backend for play-labelled commands.
    # Do not use it within other commands unless really necessary.
    async def _play_backend(
        self,
        inter: disnake.CommandInteraction,
        keyword: str,
        *,
        send_embed: bool = True,
        boosted: bool = False,
    ) -> None:
        try:
            source = await (YTDLSource if not boosted else YTDLSourceBoosted).create_source(
                inter, keyword, loop=self.bot.loop
            )

        except Exception as e:
            if isinstance(e, YTDLError):
                await inter.send(
                    f'An error occurred while processing this request: {str(e)}',
                    ephemeral=True,
                )
            else:
                pass

        else:
            song = Song(source)
            await inter.voice_state.songs.put(song)

            if send_embed:
                embed = core.TypicalEmbed(inter).set_title(
                    value=f'Enqueued {song.source.title} from YouTube.'
                )
                view = core.SmallView(inter).add_button(label='Redirect', url=song.source.url)
                await inter.send(embed=embed, view=view)

    # Separate coroutine for ensuring voice safety especially for play-labelled commands.
    # Note: This coroutine is used in conjunction with _ensure_voice_safety() and _join_logic().
    async def _ensure_play_safety(self, inter: disnake.CommandInteraction) -> True | False:
        if (not inter.voice_state.voice) and (not await self._join_logic(inter)):
            return False
        elif not await self._ensure_voice_safety(inter, skip_self=True):
            return False
        else:
            return True

    # play (slash)
    @commands.slash_command(
        name='play',
        description='Enqueues playable stuff (basically sings you songs).',
        dm_permission=False,
    )
    async def _play(
        self,
        inter: disnake.CommandInteraction,
        keyword: str = Param(
            description='The link / keyword to search for. Supports YouTube and Spotify links.'
        ),
        boosted: bool = Param(
            description='Increases bass and slightly reduces the volume for high-frequency sounds.',
            default=False,
        ),
    ) -> None:
        if not await self._ensure_play_safety(inter):
            return

        inter.voice_state.boosted = boosted

        async def process_spotify_tracks(ids, tracks) -> None:
            for i in range(len(ids)):
                track = Spotify.get_track_features(ids[i])
                tracks.append(track)

            for track in tracks:
                await self._play_backend(inter, track, send_embed=False, boosted=boosted)

            embed = core.TypicalEmbed(inter).set_title(
                value=f'{len(tracks)} tracks have been queued!'
            )
            await inter.send(embed=embed)

        if 'https://open.spotify.com/playlist/' in keyword or 'spotify:playlist:' in keyword:
            ids = Spotify.get_playlist_track_ids(keyword)
            tracks = []

            await process_spotify_tracks(ids, tracks)

        elif 'https://open.spotify.com/album/' in keyword or 'spotify:album:' in keyword:
            ids = Spotify.get_album(keyword)
            tracks = []

            await process_spotify_tracks(ids, tracks)

        elif 'https://open.spotify.com/track/' in keyword or 'spotify:track:' in keyword:
            id = Spotify.get_track_id(keyword)
            track = Spotify.get_track_features(id)
            await self._play_backend(inter, track, boosted=boosted)

        else:
            keyword = (
                'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
                if keyword.strip() == 'rick'
                else keyword
            )
            await self._play_backend(inter, keyword, boosted=boosted)

    # play (message)
    @commands.message_command(name='Search & Play', dm_permission=False)
    async def _play_message(
        self, inter: disnake.CommandInteraction, message: disnake.Message
    ) -> None:
        if not await self._ensure_play_safety(inter):
            return

        await self._play_backend(inter, message.content)

    # Common backend for playrich-labelled commands.
    # Do not use it within other commands unless really necessary.
    # Note: This backend is used in conjunction with _play_backend().
    async def _playrich_backend(
        self, inter: disnake.CommandInteraction, member: disnake.Member
    ) -> None:
        if not await self._ensure_play_safety(inter):
            return

        for activity in member.activities:
            if isinstance(activity, disnake.Spotify):
                track = Spotify.get_track_features(activity.track_id)
                await self._play_backend(inter, track, send_embed=False)

                embed = disnake.Embed(
                    title='Fetched from Spotify!',
                    description=f'Now attempting to search for **"{track}"** on YouTube'
                    + ' and enqueue it.',
                    color=1824608,
                ).set_image(url=activity.album_cover_url)

                return await inter.send(embed=embed)

        await inter.send('Nothing is being played on Spotify!', ephemeral=True)

    # playrich (slash)
    @commands.slash_command(
        name='playrich',
        description='Tries to enqueue a song from one\'s Spotify rich presence.',
        dm_permission=False,
    )
    async def _playrich(
        self,
        inter: disnake.CommandInteraction,
        member: disnake.Member = Param(
            description='Mention the server member.', default=lambda inter: inter.author
        ),
    ) -> None:
        await self._playrich_backend(inter, member)

    # playrich (user)
    @commands.user_command(name='Rich Play', dm_permission=False)
    async def _playrich_user(
        self, inter: disnake.CommandInteraction, member: disnake.Member
    ) -> None:
        await self._playrich_backend(inter, member)


# The setup() function for the cog.
def setup(bot: core.IgKnite) -> None:
    bot.add_cog(Music(bot))
