from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    # Azure OpenAI Chat
    AZURE_OPENAI_CHAT_KEY: str = Field(...)
    AZURE_OPENAI_CHAT_ENDPOINT: str = Field(...)
    AZURE_OPENAI_CHAT_DEPLOYMENT: str = Field(...)

    # Azure OpenAI Embeddings
    AZURE_OPENAI_EMB_KEY: str = Field(...)
    AZURE_OPENAI_EMB_ENDPOINT: str = Field(...)
    AZURE_OPENAI_EMB_DEPLOYMENT: str = Field(...)

    # Twilio
    TWILIO_ACCOUNT_SID: str = Field(...)
    TWILIO_AUTH_TOKEN: str = Field(...)
    TWILIO_WHATSAPP_FROM: str = Field(..., description='whatsapp:+1234567890')
    # Webhook security
    TWILIO_WEBHOOK_URL: str = Field(..., description='https://your.domain/twilio/webhook')
    # Data layer
    FAISS_INDEX_PATH: str = Field(...)
    PROPERTIES_META_JSON: str = Field(...)

settings = Settings(
    AZURE_OPENAI_CHAT_KEY=os.getenv('AZURE_OPENAI_CHAT_KEY'),
    AZURE_OPENAI_CHAT_ENDPOINT=os.getenv('AZURE_OPENAI_CHAT_ENDPOINT'),
    AZURE_OPENAI_CHAT_DEPLOYMENT=os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT'),
    AZURE_OPENAI_EMB_KEY=os.getenv('AZURE_OPENAI_EMB_KEY'),
    AZURE_OPENAI_EMB_ENDPOINT=os.getenv('AZURE_OPENAI_EMB_ENDPOINT'),
    AZURE_OPENAI_EMB_DEPLOYMENT=os.getenv('AZURE_OPENAI_EMB_DEPLOYMENT'),
    TWILIO_ACCOUNT_SID=os.getenv('TWILIO_ACCOUNT_SID'),
    TWILIO_AUTH_TOKEN=os.getenv('TWILIO_AUTH_TOKEN'),
    TWILIO_WHATSAPP_FROM=os.getenv('TWILIO_WHATSAPP_FROM'),
    TWILIO_WEBHOOK_URL=os.getenv('TWILIO_WEBHOOK_URL'),
    FAISS_INDEX_PATH=os.getenv('FAISS_INDEX_PATH', 'data/index.faiss'),
    PROPERTIES_META_JSON=os.getenv('PROPERTIES_META_JSON', 'data/properties.json'),
)