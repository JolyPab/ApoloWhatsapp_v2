import re
import numpy as np
from infra.faiss_index import PropertyIndex
from domain.models import Property
from llm.chain import embed_text

_URL_RE = re.compile(r"https?://(www\.)?inmuebles24\.[^\s]+", re.I)

class Matcher:
    def __init__(self, pindex: PropertyIndex):
        self.idx = pindex

    def detect_link(self, text: str) -> str | None:
        m = _URL_RE.search(text)
        return m.group(0) if m else None

    def suggest(self, text: str, k: int = 3) -> list[Property]:
        vec = np.array([embed_text(text)], dtype='float32')
        return self.idx.search(vec, k=k)