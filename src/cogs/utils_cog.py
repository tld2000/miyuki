from discord.ext import commands
import utils.helper as helper
import validators




class UtilityCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def sendvideo(self, ctx, url):
        if validators.url(url):
            print('a')
            if helper.is_supported(url):
                await helper.reply_with_video(ctx, url)

    @commands.command()
    async def s(self, ctx):
        # view = confirmation_button_view(ctx.author, ConfirmationType.DELETE)
        # await ctx.send(view=view)


async def setup(client):
    await client.add_cog(UtilityCog(client))
