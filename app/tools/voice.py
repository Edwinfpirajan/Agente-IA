from dotenv import load_dotenv
from openai import OpenAI
import os
import io 

load_dotenv()

key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=key)

def transcribe_and_cleanup(audio_bytes: bytes) -> str:
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "audio.mp3"
    transcription = client.audio.transcriptions.create(
        model="gpt-4o-transcribe", 
        file=audio_file
    )

    return transcription.text

