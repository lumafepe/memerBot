import youtube_dl
import os
def safeMp3File(url,id,outname):
    video_info = youtube_dl.YoutubeDL().extract_info(url=url,download=False)
    filename = f"{id}/audioFiles/{outname}.mp3"
    options={
        'format':'bestaudio/best',
        'keepvideo':False,
        'outtmpl':filename,
    }
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([video_info["webpage_url"]])
    return filename




