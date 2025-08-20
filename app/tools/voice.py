from dotenv import load_dotenv
from openai import OpenAI
import os


# Cargar las variables de entorno desde el archivo .env
load_dotenv()
key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=key)



def transcribe_and_cleanup(file_path: bytes) -> str:
    """
    Transcribe un audio a texto para contextualizar la respuesta del agente.
    """
    with open(file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="gpt-4o-transcribe", 
            file=audio_file
        )

    # Eliminar el archivo después de la transcripción
    os.remove(file_path)
    return transcription.text


# def transcribe_and_cleanup(audio_data: bytes) -> str:
#     """
#     Transcribe audio bytes a texto usando un archivo temporal
#     """
#     # Crear un archivo temporal
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
#         tmp_file.write(audio_data)
#         tmp_file_path = tmp_file.name

#     try:
#         # Usar la ruta del archivo temporal para la transcripción
#         with open(tmp_file_path, "rb") as audio_file:
#             transcription = client.audio.transcriptions.create(
#                 model="gpt-4o-transcribe", 
#                 file=audio_file
#             )
#         return transcription.text
#     finally:
#         # Eliminar el archivo temporal siempre
#         os.unlink(tmp_file_path)
