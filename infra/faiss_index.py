import json
import faiss
import numpy as np
from typing import Dict, Any, List
from domain.models import Property
from config import settings


class PropertyIndex:
    def __init__(self, index_path: str, meta_json: str):
        # Загружаем faiss-индекс
        self.index = faiss.read_index(index_path)

        # Загружаем метаданные
        with open(meta_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.meta: Dict[str, Property] = {}

        def to_prop(pid: str, payload: Dict[str, Any]) -> Property:
            """Гарантируем, что в payload есть id, и строим Property."""
            if "id" not in payload:
                payload = {"id": pid, **payload}
            return Property(**payload)

        if isinstance(data, list):
            # Формат: [ {...}, {...} ]
            for i, item in enumerate(data):
                if not isinstance(item, dict):
                    continue
                pid = str(item.get("id") or i)
                try:
                    self.meta[pid] = to_prop(pid, item)
                except Exception:
                    # Пропускаем битые записи, чтобы не валить приложение
                    continue
        elif isinstance(data, dict):
            # Формат: { "<id>": {...}, ... }
            for pid, payload in data.items():
                if not isinstance(payload, dict):
                    continue
                try:
                    self.meta[str(pid)] = to_prop(str(pid), payload)
                except Exception:
                    continue
        else:
            raise ValueError(f"Unsupported meta JSON structure: {type(data)}")

        if not self.meta:
            raise ValueError("PropertyIndex meta is empty after parsing; check meta JSON structure.")

    def search(self, vector: np.ndarray, k: int = 3) -> List[Property]:
        # Приводим вход к float32 и форме (1, d)
        vec = np.asarray(vector, dtype="float32").reshape(1, -1)
        D, I = self.index.search(vec, k)

        results: List[Property] = []
        for idx in I[0]:
            # FAISS может вернуть -1 если нет соседа
            if idx == -1:
                continue
            pid = str(idx)
            prop = self.meta.get(pid)
            if prop:
                results.append(prop)
        return results
