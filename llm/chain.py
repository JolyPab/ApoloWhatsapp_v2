from openai import AzureOpenAI
from config import settings

# Клиент для чата
_chat_client = AzureOpenAI(
    api_key=settings.AZURE_OPENAI_CHAT_KEY,
    api_version="2024-06-01",
    azure_endpoint=settings.AZURE_OPENAI_CHAT_ENDPOINT,
)

# Клиент для эмбеддингов
_emb_client = AzureOpenAI(
    api_key=settings.AZURE_OPENAI_EMB_KEY,
    api_version="2024-06-01",
    azure_endpoint=settings.AZURE_OPENAI_EMB_ENDPOINT,
)

def classify_intent(user_text: str) -> dict:
    prompt = [
        {"role":"system","content": "Eres un asistente para una inmobiliaria. Clasifica el mensaje del usuario en: 'venta', 'renta', 'visita', 'consulta', 'desconocido'. Devuelve JSON: {\\"intent\\": str, \\"zona\\": str|null, \\"presupuesto\\": float|null, \\"link\\": str|null}"},
        {"role":"user","content": user_text},
    ]
    resp = _chat_client.chat.completions.create(
        model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
        messages=prompt,
        temperature=0,
    )
    raw = resp.choices[0].message.content
    start = raw.find('{'); end = raw.rfind('}')
    if start == -1 or end == -1:
        return {"intent":"desconocido","zona":None,"presupuesto":None,"link":None}
    import json
    try:
        return json.loads(raw[start:end+1])
    except Exception:
        return {"intent":"desconocido","zona":None,"presupuesto":None,"link":None}

def draft_reply(context: str, user_text: str) -> str:
    msgs = [
        {"role":"system","content": "Eres un asesor amable y claro de una inmobiliaria en CDMX. Responde SIEMPRE en español neutro. Enfócate en agendar visitas y pedir datos mínimos útiles (zona, presupuesto, recámaras)."},
        {"role":"user","content": f"Contexto:\n{context}\n\nMensaje del cliente: {user_text}"}
    ]
    resp = _chat_client.chat.completions.create(
        model=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
        messages=msgs,
        temperature=0.4,
    )
    return resp.choices[0].message.content.strip()

def embed_text(text: str):
    resp = _emb_client.embeddings.create(
        model=settings.AZURE_OPENAI_EMB_DEPLOYMENT,
        input=text
    )
    return resp.data[0].embedding