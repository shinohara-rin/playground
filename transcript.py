import json
from youtube_transcript_api import YouTubeTranscriptApi
from os import environ, listdir
from dotenv import load_dotenv
import requests
from requests.exceptions import ConnectionError

load_dotenv(override=True)

video_list = [
    "5C_HPTJg5ek",
    "2hXNd6x9sZs",
    "IwjlCxwcuIc",
    "qq-Iid6EEkc",
    "f4s1h2YETNY"
]


def get_transcript_with_retry(video_id, max_retry=3):
    for i in range(max_retry):
        try:
            t = YouTubeTranscriptApi.get_transcript(video_id, proxies={
                'http': environ['http_proxy']} if environ.get('http_proxy') else None)
            break
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            if i == max_retry - 1:
                raise
    else:
        raise RuntimeError("Failed to get transcript")

    return t


existing_files = [f for f in listdir('./transcripts')]

for video_id in video_list:

    if f'{video_id}.json' in existing_files:
        print(f"Skipping {video_id}")
        continue

    t = get_transcript_with_retry(video_id)

    print(f"Writing transcript of {video_id}")
    with open(f'./transcripts/{video_id}.json', 'w+') as f:
        json.dump(t, f, ensure_ascii=False, indent=4)

    plaintext = " ".join([i['text'] for i in t])
    with open(f'./transcripts/{video_id}.txt', 'w+') as f:
        f.write(plaintext)
