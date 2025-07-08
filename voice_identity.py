import os
import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav
from pathlib import Path
from dotenv import load_dotenv
import pickle
import re

load_dotenv()

# Caminho onde salvaremos os embeddings
BASE_DIR = os.getenv("USER_PROFILES_DIR", "./voice_profiles")
os.makedirs(BASE_DIR, exist_ok=True)

encoder = VoiceEncoder()


def gerar_embedding(caminho_audio_wav):
    wav = preprocess_wav(Path(caminho_audio_wav))
    embedding = encoder.embed_utterance(wav)
    return embedding


def salvar_embedding(nome_usuario, embedding):
    caminho = os.path.join(BASE_DIR, f"{nome_usuario}.pkl")
    with open(caminho, "wb") as f:
        pickle.dump(embedding, f)


def carregar_embeddings():
    embeddings = {}
    for arquivo in os.listdir(BASE_DIR):
        if arquivo.endswith(".pkl"):
            nome = arquivo.replace(".pkl", "")
            with open(os.path.join(BASE_DIR, arquivo), "rb") as f:
                embeddings[nome] = pickle.load(f)
    return embeddings


def identificar_usuario(embedding):
    todos = carregar_embeddings()
    melhor_nome = None
    melhor_similaridade = 0.0

    for nome, emb_salvo in todos.items():
        sim = np.inner(embedding, emb_salvo)
        if sim > melhor_similaridade:
            melhor_similaridade = sim
            melhor_nome = nome

    if melhor_similaridade > 0.85:
        return melhor_nome
    return None


# NOVO: Função central que trata tudo
def identificar_ou_registrar_usuario(caminho_wav, texto_transcrito):
    embedding = gerar_embedding(caminho_wav)

    nome_identificado = identificar_usuario(embedding)
    if nome_identificado:
        return nome_identificado

    # Se não identificou, tentar extrair o nome do texto
    nome_possivel = extrair_nome(texto_transcrito)

    if nome_possivel:
        salvar_embedding(nome_possivel, embedding)
        return nome_possivel

    # Se nem isso, retorna "desconhecido"
    return "desconhecido"


# 🧠 Tentativa simples de extrair nome do texto
def extrair_nome(texto):
    texto = texto.lower()

    # Padrões simples de extração
    padroes = [
        r"meu nome é (\w+)",
        r"aqui é (\w+)",
        r"quem fala é (\w+)",
        r"eu sou o (\w+)",
        r"eu sou a (\w+)",
    ]

    for padrao in padroes:
        match = re.search(padrao, texto)
        if match:
            return match.group(1).capitalize()

    return None
