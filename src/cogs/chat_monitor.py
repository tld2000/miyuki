from discord.ext import commands
import utils.helper as helper
from urlextract import URLExtract


class ChatMonitor(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.url_extractor = URLExtract()

    @commands.Cog.listener()
    async def on_message(self, message):
        # only check messages from human
        if message.author.bot:
            return

        # excludes commands
        ctx = await self.client.get_context(message)
        if ctx.valid:
            return

        # FB downloader
        urls = self.url_extractor.find_urls(message.content)
        if len(urls) > 0:
            ctx = None
            for url in urls:
                if helper.is_fb_video(url):
                    if ctx is None:
                        ctx = await self.client.get_context(message)
                    await helper.reply_with_video(ctx, url)

        # emoji uploader
        emojis = helper.has_emoji(message)
        if len(emojis) > 0:
            emojis_urls = helper.get_emoji_urls(self.client, message.guild.id, emojis)
            for emoji_url in emojis_urls:
                await message.channel.send(emoji_url)


async def setup(client):
    await client.add_cog(ChatMonitor(client))
