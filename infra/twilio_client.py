from twilio.rest import Client
from config import settings

_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

def send_whatsapp(to_number: str, body: str | None = None, media_urls: list[str] | None = None):
    kwargs = {
        'from_': settings.TWILIO_WHATSAPP_FROM,
        'to': to_number,
    }
    if body:
        kwargs['body'] = body
    if media_urls:
        kwargs['media_url'] = media_urls
    return _client.messages.create(**kwargs)