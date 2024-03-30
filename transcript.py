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


def get_transcript(video_id, max_retry=3, proxy=None):
    if not proxy and environ.get('http_proxy'):
        proxy = environ['http_proxy']

    for i in range(max_retry):
        try:
            t = YouTubeTranscriptApi.get_transcript(
                video_id, proxies={'http': proxy})
            break
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            if i == max_retry - 1:
                raise
    else:
        raise RuntimeError("Failed to get transcript")

    return t


# existing_files = [f for f in listdir('./transcripts')]

# for video_id in video_list:

#     if f'{video_id}.json' in existing_files:
#         print(f"Skipping {video_id}")
#         continue

#     t = get_transcript_with_retry(video_id)

#     print(f"Writing transcript of {video_id}")
#     with open(f'./transcripts/{video_id}.json', 'w+') as f:
#         json.dump(t, f, ensure_ascii=False, indent=4)

#     plaintext = " ".join([i['text'] for i in t])
#     with open(f'./transcripts/{video_id}.txt', 'w+') as f:
#         f.write(plaintext)

def chunk_transcript(transcript, duration=30):
    """
    Generates chunks of a transcript based on a time interval.

    Args:
        transcript (list): A list of dictionaries representing the transcript. Each dictionary contains the 'start' timestamp and the 'text' of a transcript entry.

    Returns:
        list: A list of dictionaries representing the chunks of the transcript. Each dictionary contains the 'chunk' (the text of the chunk) and the 'timestamp' (the start timestamp of the chunk).

    Example:
        transcript = [
            {'start': 0, 'text': 'Hello'},
            {'start': 5, 'text': 'world'},
            {'start': 10, 'text': '!'},
            {'start': 15, 'text': 'How are you?'},
            {'start': 20, 'text': 'I am fine.'}
        ]
        chunk_transcript(transcript)
        # Output:
        [
            {'chunk': 'Hello world !', 'timestamp': 0},
            {'chunk': 'How are you? I am fine.', 'timestamp': 10}
        ]
    """
    chunks = []
    chunk = ""
    timestamp = int(transcript[0]['start'])
    for e in transcript:
        if e['start'] - timestamp > duration:
            chunks.append({'chunk': chunk, 'timestamp': timestamp})
            chunk = ""
            timestamp = int(e['start'])
        else:
            chunk += e['text'] + " "

    return chunks


def get_prompt_for_transcript(transcript):
    chunks = chunk_transcript(transcript)
    prompt = ""
    # check if the transcript is longer than 1 hour (thus need hours in timestamp)
    if chunks[-1]['timestamp'] > 3600:
        for c in chunks:
            # Generate prompt in the format "[hh:mm:ss]: {text}"
            hours, tseconds = divmod(c['timestamp'], 3600)
            minutes, seconds = divmod(tseconds, 60)
            prompt += f"[{hours:02d}:{minutes:02d}:{seconds:02d}]: {c['chunk']}\n"
    else:
        for c in chunks:
            # Generate prompt “[mm:ss]: {text}”
            minutes, seconds = divmod(c['timestamp'], 60)
            prompt += f"[{minutes:02d}:{seconds:02d}]: {c['chunk']}\n"
    return prompt
