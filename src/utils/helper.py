import yt_dlp
import validators
import os
import ffmpeg


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
        if is_supported(url) and ('fb.watch' in url or 'facebook' in url):
            print(69)
            if url.find('facebook') or url.find('fb'):
                return True

    return False


def download_fb_video(url):
    ydl_opts_sep = {
        'format': 'bestvideo+worstaudio',
        'quiet': True,
        #'verbose': True,
        'nooverwrites': False,
        'merge_output_format': 'mp4',
        'outtmpl': f'./temp/temp_fb.%(ext)s'
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts_sep) as ydl:
            ydl.download(url)

    except yt_dlp.DownloadError as error:
        if "Requested format is not available" in error.msg:
            try:
                ydl_opts_sep['format'] = 'best'
                with yt_dlp.YoutubeDL(ydl_opts_sep) as ydl:
                    ydl.download(url)
                return True
            except yt_dlp.DownloadError:
                pass
        return False

    except Exception as error:
        print(error.msg)
        return False

    return True


def get_direct_fb_video_link(url):
    compress_video('./temp/temp_fb.mp4', './temp/temp_fb_compressed.mp4', 8 * 1000)


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