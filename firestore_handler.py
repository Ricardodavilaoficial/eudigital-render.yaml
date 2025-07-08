import os
from google.cloud import firestore
from dotenv import load_dotenv

load_dotenv()

# Inicializa o cliente do Firestore
db = firestore.Client()

def salvar_historico(usuario, entrada, resposta):
    try:
        doc_ref = db.collection("historicos").document()
        doc_ref.set({
            "usuario": usuario,
            "entrada": entrada,
            "resposta": resposta
        })
        print(f"💾 Histórico salvo para {usuario}")
    except Exception as e:
        print("❌ Erro ao salvar histórico:", e)

# (outros handlers futuros como buscar_usuario_por_identificador podem ficar aqui)
