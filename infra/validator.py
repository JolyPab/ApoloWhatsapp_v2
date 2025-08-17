from twilio.request_validator import RequestValidator
from config import settings

_validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)

def validate_twilio_signature(headers: dict, url: str, params: dict) -> bool:
    signature = headers.get('X-Twilio-Signature') or headers.get('x-twilio-signature')
    if not signature:
        return False
    return _validator.validate(url, params, signature)