import datetime

import mysql.connector.errors
import requests
import yt_dlp
import validators
import os
import ffmpeg
import re
import discord

MAX_VIDEO_UPLOAD_SIZE_MB = 8


def is_supported(url):
    extractors = yt_dlp.extractor.gen_extractors()
    for e in extractors:
        if e.suitable(url) and e.IE_NAME != 'generic':
            return True
    return False


def to_playable(query):
    if validators.url(query):
        if is_supported(query) or query[:-4] in ['.mp3', '.wav', '.ogg']:
            pass
    pass


def is_fb_video(url):
    if validators.url(url):
        # is supported doesn't catch all facebook cases
        if ('fb.watch' in url or 'facebook' in url) or (is_supported(url) and ('fb.watch' in url or 'facebook' in url)):
            if url.find('facebook') or url.find('fb'):
                return True

    return False


def download_video(url):
    ydl_opts_sep = {
        'format': 'bestvideo+worstaudio',
        'quiet': True,
        #'verbose': True,
        'nooverwrites': False,
        'merge_output_format': 'mp4',
        'outtmpl': f'./temp/temp_video.%(ext)s'
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts_sep) as ydl:
            print(1)
            ydl.download(url)

    except yt_dlp.DownloadError as error:
        if "Requested format is not available" in error.msg:
            try:
                ydl_opts_sep['format'] = 'best'
                with yt_dlp.YoutubeDL(ydl_opts_sep) as ydl:
                    ydl.download(url)
                return True
            except yt_dlp.DownloadError as error:
                print(error.msg)
                pass
            except yt_dlp.utils.YoutubeDLError as error:
                print(error.msg)
        return False

    except Exception as error:
        print(error.msg)
        return False

    return True


def compress_video(video_full_path, output_file_name, target_size):
    # Reference: https://stackoverflow.com/questions/64430805/how-to-compress-video-to-target-size-by-python
    # Reference: https://en.wikipedia.org/wiki/Bit_rate#Encoding_bit_rate
    probe = ffmpeg.probe(video_full_path)
    # Video duration, in s.
    duration = float(probe['format']['duration'])
    # Audio bitrate, in bps.
    audio_bitrate = float(next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)['bit_rate'])
    # Target total bitrate, in bps.
    target_total_bitrate = (target_size * 1024 * 8) / (1.073741824 * duration)

    audio_bitrate = 32000
    # Target video bitrate, in bps.
    video_bitrate = target_total_bitrate - audio_bitrate

    i = ffmpeg.input(video_full_path)
    ffmpeg.output(i, os.devnull,
                  **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 1, 'f': 'mp4'}
                  ).overwrite_output().global_args('-loglevel', 'error').run()
    ffmpeg.output(i, output_file_name,
                  **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 2, 'c:a': 'aac', 'b:a': audio_bitrate}
                  ).overwrite_output().global_args('-loglevel', 'error').run()


async def reply_with_video(ctx, url):
    await ctx.message.edit(suppress=True)
    downloaded = download_video(url)
    if not downloaded:
        return

    size = os.path.getsize("./temp/temp_video.mp4")
    if size > MAX_VIDEO_UPLOAD_SIZE_MB * 1024 * 1024:
        compress_video('./temp/temp_video.mp4', './temp/temp_video_compressed.mp4', MAX_VIDEO_UPLOAD_SIZE_MB * 1000)
        await ctx.message.reply(file=discord.File("./temp/temp_video_compressed.mp4"))
    else:
        await ctx.message.reply(file=discord.File("./temp/temp_video.mp4"))


def has_emoji(msg):
    emojis = re.findall(r':\w+:', msg.content)
    return emojis


def get_emoji_urls(client, guild_id, emojis):
    emoji_urls = []
    try:
        for emoji in emojis:
            client.sql_cursor.execute(f"SELECT url FROM emojis WHERE emoji_name = '{emoji}' AND guild_id = {guild_id}")
            if client.sql_cursor.rowcount > 0:
                emoji_urls.append(client.sql_cursor.fetchone()[0])
    except mysql.connector.errors.ProgrammingError as err:
        return []
    else:
        return emoji_urls


async def embed_generator(ctx, color: int | discord.Color = None, title: str = None, desc: str = '', url: str = None,
                          img_url: str = None, footer: str = None, reactions: list = [], timestamp: datetime.datetime = None):
    embed = discord.Embed(color=color, title=title, description=desc, url=url, timestamp=timestamp)
    if img_url is not None:
        embed.set_image(url=img_url)
    if footer is not None:
        embed.set_footer(text=footer)

    embed_msg = await ctx.send(embed=embed)

    for reaction in reactions:
        await embed_msg.add_reaction(reaction)


def gif_url_checker(url):
    r = requests.head(url)
    if r.headers["content-type"] == "image/gif":
        return True
    return False
