from email import message
from json import load
from langchain.chat_models import ChatOpenAI
import os
from langchain.schema import AIMessage, HumanMessage, SystemMessage
import openai
from transcript import get_transcript, get_prompt_for_transcript
import gradio as gr
from dotenv import load_dotenv

load_dotenv()

os.environ["no_proxy"] = "localhost,127.0.0.1,::1"

llm = ChatOpenAI(temperature=1.0, model='gpt-3.5-turbo',
                 base_url=os.environ['BASE_URL'])

sysprompt = ""


def predict(message, history):
    history_langchain_format = []
    history_langchain_format.append(HumanMessage(content=sysprompt))
    for human, ai in history:
        history_langchain_format.append(HumanMessage(content=human))
        history_langchain_format.append(AIMessage(content=ai))
    history_langchain_format.append(HumanMessage(content=message))
    gpt_response = llm(history_langchain_format)
    return history + [(message, gpt_response.content)]


def load_video(video_id):
    global sysprompt
    transcript = get_transcript(video_id)
    sysprompt = f"""
You are AskVid Bot, a helpful assistant that can help user better understand the content of a video.
A transcript of the video is provided below, in the XML tag, answer the user's questions according to the transcript.

Make sure your answer is closly related to the transcript, only mention facts stated in the video. If the video doesn't explicitly mention what the user asked about, just say that you don't know.

Each line in the transcript is a timestamp followed by spoken text in that 30 seconds timeframe.

<transcript>
{transcript}
</transcript>"""


with gr.Blocks() as demo:
    videoId = gr.Textbox(label="Video ID")
    loadbtn = gr.Button("Load Video")
    loadbtn.click(load_video, inputs=videoId, outputs=None)
    chat = gr.Chatbot()
    message = gr.Textbox(label="Message")
    message.submit(predict, inputs=[message, chat], outputs=chat)

demo.launch()
