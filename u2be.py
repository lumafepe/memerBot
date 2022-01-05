import youtube_dl
import os
def safeMp3File(url,outname):
    video_info = youtube_dl.YoutubeDL().extract_info(url=url,download=False)
    filename = f"audioFiles/{outname}.mp3"
    options={
        'format':'bestaudio/best',
        'keepvideo':False,
        'outtmpl':filename,
    }
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([video_info["webpage_url"]])
    return filename




