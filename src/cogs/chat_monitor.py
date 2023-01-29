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
            helper.download_fb_video(text)
            await message.edit(suppress=True)
            size = os.path.getsize("./temp/temp_fb.mp4")
            if size > 8388608:
                # await message.reply("Video too large.")
                pass
            else:
                await message.reply(file=discord.File("./temp/temp_fb.mp4"))


async def setup(client):
    await client.add_cog(ChatMonitor(client))
