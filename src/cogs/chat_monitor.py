from discord.ext import commands
import discord
import os
import utils.helper as helper


class ChatMonitor(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        text = message.content

        # FB downloader
        if helper.is_fb_video(text):
            await message.edit(suppress=True)
            downloaded = helper.download_fb_video(text)
            if not downloaded:
                return

            size = os.path.getsize("./temp/temp_fb.mp4")
            if size > 8388608:
                helper.get_direct_fb_video_link(text)
                await message.reply(file=discord.File("./temp/temp_fb_compressed.mp4"))
            else:
                await message.reply(file=discord.File("./temp/temp_fb.mp4"))


async def setup(client):
    await client.add_cog(ChatMonitor(client))
