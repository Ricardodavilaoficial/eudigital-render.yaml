from flask import Blueprint, request, send_file, jsonify
from services.audio_processing import transcrever_audio_google
from services.text_to_speech import gerar_audio_elevenlabs
from services.openai_handler import obter_resposta_openai
from interfaces.web_interface import html_index
from services.voice_identity import identificar_ou_registrar_usuario
from services.firestore_handler import salvar_historico
import uuid
import traceback
from pydub import AudioSegment

routes = Blueprint('routes', __name__)

@routes.route("/", methods=["GET"])
def index():
    return html_index()

@routes.route("/audio", methods=["POST"])
def handle_audio():
    try:
        audio_file = request.files.get("file")
        if not audio_file:
            print("🚫 Nenhum arquivo de áudio recebido.")
            return jsonify({"error": "Nenhum arquivo de áudio enviado"}), 400

        unique_id = str(uuid.uuid4())
        caminho_original = f"/tmp/{unique_id}_original.webm"
        caminho_wav = f"/tmp/{unique_id}.wav"

        # Salvar o arquivo original
        with open(caminho_original, "wb") as f:
            f.write(audio_file.read())

        print("📥 Áudio recebido. Convertendo para WAV...")

        audio = AudioSegment.from_file(caminho_original)
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        audio.export(caminho_wav, format="wav")

        print("🔄 Conversão concluída. Enviando para transcrição...")

        texto = transcrever_audio_google(caminho_wav)

        if not texto:
            print("⚠️ NADA FOI TRANSCRITO.")
            return jsonify({"error": "Não foi possível transcrever o áudio"}), 400

        print("📝 Texto transcrito:", texto)

        # 🔐 Identificação ou registro automático do usuário
        usuario = identificar_ou_registrar_usuario(caminho_wav, texto)
        print(f"👤 Usuário identificado (ou registrado): {usuario}")

        # 🤖 Se não conseguimos identificar a pessoa, pedimos que se identifique
        if usuario == "desconhecido":
            resposta = "Opa, tudo bem? Quem está falando, por favor?"
        else:
            resposta = obter_resposta_openai(f"{usuario}: {texto}")
            print("💬 Resposta da IA:", resposta)

            # 💾 SALVA NO FIRESTORE
            salvar_historico(usuario, texto, resposta)

        caminho_resposta_audio = gerar_audio_elevenlabs(resposta)
        print("🔊 Resposta de áudio gerada. Enviando...")

        return send_file(caminho_resposta_audio, mimetype="audio/mpeg")

    except Exception as e:
        print("❌ ERRO AO PROCESSAR O ÁUDIO:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
