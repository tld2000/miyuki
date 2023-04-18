import asyncio
from discord.ext import tasks, commands
import nacl
from utils.ytdlsource import YTDLSource


class AudioPlayer(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.event_loop = None
        self.queue = {}
        self.loop = {}
        self.stop_task.start()

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
        await self.stop_guild_id(ctx.guild.id)

    async def stop_guild_id(self, guild_id):
        voice_client = self.client.get_guild(int(guild_id)).voice_client
        if voice_client is not None:
            await voice_client.disconnect()
            self.queue[str(guild_id)] = []
            self.loop[str(guild_id)] = False

    @commands.command(aliases=['pley', 'Play', 'PLAY', 'plya'])
    async def play(self, ctx, *, url, added_options=""):
        """Streams from an url (same as yt, but doesn't predownload)"""

        player_list = await YTDLSource.from_url(url, loop=self.client.loop, stream=True, added_options=added_options)

        try:
            self.queue[str(ctx.guild.id)].extend(player_list)
        except KeyError:
            self.queue[str(ctx.guild.id)] = player_list
            self.loop[str(ctx.guild.id)] = False

        # or paused
        if not (ctx.voice_client.is_playing()):
            self.event_loop = asyncio.new_event_loop()
            self.play_queue(ctx)

    @commands.command()
    async def loop(self, ctx):
        self.loop[str(ctx.guild.id)] = not self.loop[str(ctx.guild.id)]

    @commands.command()
    async def skip(self, ctx):
        ctx.voice_client.stop()
        if len(self.queue[str(ctx.guild.id)]) == 0:
            await self.stop(ctx)

    @commands.command()
    async def seek(self, ctx, arg):
        time_list = list(map(int, arg.split(":")))[::-1]
        time_s = sum([time_list[i]*(60**i) for i in range(len(time_list))])
        url = self.queue[str(ctx.guild.id)][0].data['webpage_url']
        player_list = await YTDLSource.from_url(url, loop=self.client.loop, stream=True, added_options=f' -ss {time_s}')
        self.queue[str(ctx.guild.id)].insert(1, player_list[0])
        await self.skip(ctx)

    @commands.command()
    async def queue(self, ctx):
        for item in self.queue[str(ctx.guild.id)]:
            print(item.title)
            pass

    async def play_from_url(self, ctx, url):
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.client.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.send(f'Now playing: {player.title}')

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")

    def play_queue(self, ctx):
        if len(self.queue[str(ctx.guild.id)]) == 0:
            return
        player = self.queue[str(ctx.guild.id)][0]

        def after_play(e):
            if e:
                print('Player error: %s' % e)
            else:
                if not self.loop[str(ctx.guild.id)]:
                    try:
                        self.queue[str(ctx.guild.id)].pop(0)
                    except IndexError:
                        pass
                print(1)
                self.play_queue(ctx)

        ctx.voice_client.play(player, after=lambda e: after_play(e))

    @tasks.loop(minutes=5.0)
    async def stop_task(self):
        for guild_id in self.queue:
            if len(self.queue[guild_id]) == 0:
                await self.stop_guild_id(guild_id)


async def setup(client):
    await client.add_cog(AudioPlayer(client))
