import json
from youtube_transcript_api import YouTubeTranscriptApi
from os import environ
from dotenv import load_dotenv

load_dotenv(override=True)

video_list = [
    "5C_HPTJg5ek"
]

for video_id in video_list:
    t = YouTubeTranscriptApi.get_transcript(video_id, proxies={
                                            'http': environ['http_proxy']} if environ.get('http_proxy') else None)
    with open(f'./transcripts/{video_id}.json', 'w+') as f:
        json.dump(t, f, ensure_ascii=False, indent=4)

    plaintext = " ".join([i['text'] for i in t])
    with open(f'./transcripts/{video_id}.txt', 'w+') as f:
        f.write(plaintext)
