import yt_dlp
import validators


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
        if is_supported(url) or url.find('fb.watch') or url.find('facebook'):
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
    with yt_dlp.YoutubeDL(ydl_opts_sep) as ydl:
        ydl.download(url)