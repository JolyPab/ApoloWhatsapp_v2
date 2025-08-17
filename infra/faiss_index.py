import json
import faiss
import numpy as np
from typing import List
from domain.models import Property
from config import settings

class PropertyIndex:
    def __init__(self, index_path: str, meta_json: str):
        self.index = faiss.read_index(index_path)
        with open(meta_json, 'r', encoding='utf-8') as f:
            self.meta = {p['id']: Property(**p) for p in json.load(f)}

    def search(self, vector: np.ndarray, k: int = 3) -> List[Property]:
        D, I = self.index.search(vector.astype('float32'), k)
        results = []
        for idx in I[0]:
            pid = str(idx)
            if pid in self.meta:
                results.append(self.meta[pid])
        return results