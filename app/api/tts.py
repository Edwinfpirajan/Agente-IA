# app/api/tts.py
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
import requests
import io
import os

router = APIRouter()

# Puedes poner esta variable en tu .env
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = "EXAVITQu4vr4xnSDxMaL"  

@router.post("/tts")
async def text_to_speech(request: Request):
    data = await request.json()
    text = data.get("text")

    if not text:
        raise HTTPException(status_code=400, detail="Texto faltante")

    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        },
    )

    # 🔍 Mostrar el error exacto que viene de ElevenLabs
    if response.status_code != 200:
        print("❌ Error ElevenLabs:", response.status_code, response.text)
        raise HTTPException(status_code=response.status_code, detail=response.text)

    audio_stream = io.BytesIO(response.content)
    return StreamingResponse(audio_stream, media_type="audio/mpeg")

