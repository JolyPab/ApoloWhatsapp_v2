from domain import templates_es as T
from infra.twilio_client import send_whatsapp
from services.property_matcher import Matcher
from llm.chain import draft_reply
from domain.models import Lead

class Conversation:
    def __init__(self, matcher: Matcher):
        self.matcher = matcher
        self._state: dict[str, dict] = {}

    def _get_state(self, phone: str) -> dict:
        return self._state.get(phone) or {}

    def _set_state(self, phone: str, st: dict):
        self._state[phone] = st

    def handle(self, from_number: str, text: str):
        state = self._get_state(from_number)
        link = self.matcher.detect_link(text)

        if link:
            msg = ("¿Quieres agendar una *visita* para esta propiedad? "
                   "Puedo compartir tus datos al asesor para confirmar.")
            send_whatsapp(from_number, msg)
            state.update({"stage":"visit_link","link":link})
            self._set_state(from_number, state)
            return

        suggestions = self.matcher.suggest(text, k=3)
        if suggestions:
            lines = [T.SUGGESTIONS_HEADER]
            media = []
            for p in suggestions:
                lines.append(T.PROPERTY_LINE.format(title=p.title, location=p.location, price=p.price, url=p.url))
                if p.photos:
                    media.append(p.photos[0])
            send_whatsapp(from_number, "\n".join(lines))
            if media:
                send_whatsapp(from_number, None, media_urls=media)
            send_whatsapp(from_number, T.CONFIRM_VISIT)
            state.update({"stage":"suggested"})
            self._set_state(from_number, state)
            return

        reply = draft_reply("Sin resultados directos.", text)
        send_whatsapp(from_number, reply)
        self._set_state(from_number, state)

    def capture_visit(self, from_number: str, text: str) -> Lead | None:
        lead = Lead(phone=from_number, intent='visita', note=text)
        send_whatsapp(from_number, "¡Listo! Un asesor te contactará para confirmar la visita.")
        return lead