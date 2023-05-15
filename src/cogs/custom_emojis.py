import asyncio
import validators
from discord.ext import commands
import utils.helper as helper
import json
import re


class CustomEmojis(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.is_owner()
    async def importemojisbackup(self, ctx):
        attachments = ctx.message.attachments
        counter = 0
        if len(attachments) != 1:
            await ctx.send("Too many or too few attachment(s).")
            return

        if attachments[0].content_type[:16] != "application/json":
            await ctx.send("Wrong backup file format.")
            return

        try:
            if await attachments[0].save("./temp/backup.json") > 0:
                with open("./temp/backup.json", 'r') as f:
                    data = json.load(f)
                    emojis = data['emojis']

                for guild in emojis:
                    for emoji in emojis[guild]:
                        self.add_new_emoji(ctx, emoji, int(guild), emojis[guild][emoji], confirm_overwrite=False,
                                           autocommit=False)
                        counter += 1
                self.client.sqldb.commit()
        except Exception as err:
            raise err
        else:
            await ctx.send(f"Restored {counter} emojis from backup.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addemoji(self, ctx, emoji, url):
        if not validators.url(url):
            await ctx.send("Invalid URL")
        elif len(emoji) > 22:
            await ctx.send("Emoji name is too long (larger than 20 characters)")
        elif len(re.findall(r'^:\w+:$', emoji)) == 0:
            await ctx.send("Invalid emoji name format")
        elif not helper.gif_url_checker(url):
            await ctx.send("Url does not lead to a gif")
        else:
            await self.add_new_emoji(ctx, emoji, ctx.guild.id, url, confirm_overwrite=True, autocommit=True)

    async def add_new_emoji(self, ctx, emoji: str, guild_id: int, url: str, confirm_overwrite: bool, autocommit: bool):
        existing_emoji = helper.get_emoji_urls(self.client, guild_id, [emoji])
        # emojis already in table, UPDATE
        if len(existing_emoji) > 0:
            if confirm_overwrite:
                await helper.embed_generator(ctx=ctx,
                                             title=f"An emoji with similar name {emoji} already existed",
                                             desc=f"Replace {emoji}?",
                                             img_url=existing_emoji[0],
                                             footer="React with ✅ to overwrite, x to keep the old emoji. Timeout in 30s.",
                                             reactions=['✅', '❌'])

                try:
                    reactions = await self.client.wait_for("reaction_add", timeout=30.0,
                                                           check=lambda react, user: str(react) in ['✅',
                                                                                                    '❌'] and user == ctx.message.author)
                except asyncio.TimeoutError as err:
                    return
                else:
                    if str(reactions[0]) == '❌':
                        return
            self.client.sql_cursor.execute(f"UPDATE emojis SET url = '{url}' "
                                           f"WHERE guild_id = {guild_id} AND emoji_name = '{emoji}'")
        # new emojis, INSERT
        else:
            self.client.sql_cursor.execute(f"INSERT INTO emojis (emoji_name, guild_id, url) "
                                           f"VALUES ('{emoji}', {guild_id}, '{url}')")
        if autocommit:
            self.client.sqldb.commit()
            await helper.embed_generator(ctx=ctx,
                                         title=f"{emoji} has been set as",
                                         img_url=url,
                                         footer=f"by {ctx.author.name}#{ctx.author.discriminator}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def deleteemoji(self, ctx, emoji):
        if len(re.findall(r'^:\w+:$', emoji)) == 0:
            await ctx.send("Invalid emoji name format")
            return

        existing_emoji = helper.get_emoji_urls(self.client, ctx.guild.id, [emoji])
        if len(existing_emoji) > 0:
            await helper.embed_generator(ctx=ctx,
                                         title=f"Delete {emoji}?",
                                         img_url=existing_emoji[0],
                                         footer="React with ✅ to overwrite, x to keep the old emoji. Timeout in 30s.",
                                         reactions=['✅', '❌'])
            try:
                reactions = await self.client.wait_for("reaction_add", timeout=30.0,
                                                       check=lambda react, user: str(react) in ['✅',
                                                                                                '❌'] and user == ctx.message.author)
            except asyncio.TimeoutError as err:
                return
            else:
                if str(reactions[0]) == '❌':
                    return
            self.client.sql_cursor.execute(f"DELETE FROM emojis WHERE emoji_name='{emoji}' AND guild_id={ctx.guild.id}")
            self.client.sqldb.commit()
            await helper.embed_generator(ctx=ctx,
                                         title=f"{emoji} has been deleted",
                                         img_url=existing_emoji[0],
                                         footer=f"by {ctx.author.name}#{ctx.author.discriminator}")


async def setup(client):
    await client.add_cog(CustomEmojis(client))
