from openai import OpenAI
from dotenv import load_dotenv
from typing import Optional
import os
import base64

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

def encode_image(image_bytes: bytes) -> str:
    print("Encoding image to base64")
    return base64.b64encode(image_bytes).decode("utf-8")



def analyze_image(image_path: bytes) -> str:
    base64_image = encode_image(image_path)

    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {
                "role": "user",
                "content": [
                    { "type": "input_text", "text": "Vas a describir muy bien la imagen ya que la pasaras a otro modelo donde le va responder a un usuario y no tan largo el texto"},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            }
        ],
    )
    return response.output[0].content[0].text