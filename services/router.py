from llm.chain import classify_intent

def route(user_text: str) -> dict:
    return classify_intent(user_text)