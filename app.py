from flask import Flask, request, abort, jsonify
from config import settings
from infra.validator import validate_twilio_signature
from infra.faiss_index import PropertyIndex
from services.property_matcher import Matcher
from services.conversation import Conversation

app = Flask(__name__)

# инициализация как было
_pindex = PropertyIndex(settings.FAISS_INDEX_PATH, settings.PROPERTIES_META_JSON)
_matcher = Matcher(_pindex)
_conv = Conversation(_matcher)

@app.get("/")   # <-- добавлен
def root():
    return "OK", 200

@app.get("/health")   # <-- добавлен
def health():
    return jsonify(status="ok"), 200

@app.post("/twilio/webhook")
def twilio_webhook():
    if not validate_twilio_signature(request.headers, settings.TWILIO_WEBHOOK_URL, request.form):
        abort(403)
    from_number = request.form.get('From')
    body = (request.form.get('Body') or '').strip()
    if not from_number:
        abort(400)
    _conv.handle(from_number, body)
    return ('', 200)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
