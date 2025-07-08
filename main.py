from flask import Flask, request, send_file, render_template_string, jsonify
from services.openai_handler import obter_resposta_openai
from services.text_to_speech import gerar_audio_google, gerar_audio_elevenlabs
from services.audio_processing import transcrever_audio_google
from pydub import AudioSegment
import os
import uuid
import traceback
from dotenv import load_dotenv
from interfaces.web_interface import html_index

load_dotenv()

app = Flask(__name__)

# Registra rotas externas
from routes.routes import routes

app.register_blueprint(routes)


@app.route("/", methods=["GET"])
def index():
    return html_index()


# ⚠️ Esta linha estava indentada errada (estava *dentro* da função `index`)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
