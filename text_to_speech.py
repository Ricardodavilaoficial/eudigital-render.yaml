import os
import uuid
import tempfile
from google.cloud import texttospeech
from elevenlabs import generate, save, set_api_key

set_api_key(os.getenv("ELEVEN_API_KEY"))

# Inicializa o cliente do Google TTS
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(
    "gcloud-key.json")
tts_client = texttospeech.TextToSpeechClient(credentials=credentials)


def gerar_audio_google(texto):
    synthesis_input = texttospeech.SynthesisInput(text=texto)

    voice = texttospeech.VoiceSelectionParams(
        language_code="pt-BR",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3)

    response = tts_client.synthesize_speech(input=synthesis_input,
                                            voice=voice,
                                            audio_config=audio_config)

    caminho_audio = f"/tmp/audio_{uuid.uuid4()}.mp3"
    with open(caminho_audio, "wb") as out:
        out.write(response.audio_content)

    return caminho_audio


def gerar_audio_elevenlabs(texto):
    audio = generate(
        text=texto,
        voice="Ricardo Original",
        model="eleven_multilingual_v2"
    )
    caminho_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    save(audio, caminho_temp.name)
    return caminho_temp.name