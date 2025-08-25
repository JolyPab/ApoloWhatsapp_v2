# infra/faiss_index.py
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Dict, Tuple

import faiss
import numpy as np


@dataclass
class Property:
    # Поля из твоего JSON
    title: str
    address: str
    price_usd: float | int | None = None
    price_rub: float | int | None = None
    rooms: float | int | None = None
    area: float | int | None = None
    url: str | None = None
    photos: list[str] | None = None

    # допускаем лишние ключи в JSON — они игнорируются
    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Property":
        return Property(
            title=d.get("title") or "",
            address=d.get("address") or "",
            price_usd=d.get("price_usd"),
            price_rub=d.get("price_rub"),
            rooms=d.get("rooms"),
            area=d.get("area"),
            url=d.get("url"),
            photos=d.get("photos") or d.get("images") or None,
        )


class PropertyIndex:
    """
    Обёртка над FAISS + метаданные объявлений.
    Предполагаем, что порядок эмбеддингов в FAISS совпадает с порядком объектов в meta JSON.
    Если в объекте есть 'id' и это целое из диапазона [0..N-1], он будет тоже учтён.
    """

    def __init__(self, faiss_index_path: str | Path, meta_json_path: str | Path):
        self.faiss_index_path = Path(faiss_index_path)
        self.meta_json_path = Path(meta_json_path)

        # --- загрузка меты
        self.meta_list: List[Property] = self._load_meta(self.meta_json_path)
        if not self.meta_list:
            raise ValueError(
                "PropertyIndex meta is empty after parsing; check meta JSON structure."
            )

        # --- загрузка faiss
        if not self.faiss_index_path.exists():
            raise FileNotFoundError(f"FAISS index not found: {self.faiss_index_path}")
        self.index = faiss.read_index(str(self.faiss_index_path))

        # --- валидация размеров
        faiss_size = self.index.ntotal
        if faiss_size != len(self.meta_list):
            raise ValueError(
                f"FAISS index size ({faiss_size}) != meta size ({len(self.meta_list)}). "
                "Проверь, что эмбеддинги строились из того же списка и в том же порядке."
            )

        # Быстрый доступ: faiss_id(int) -> Property
        # Для обычного IndexFlat* faiss_id == позиция в массиве эмбеддингов.
        self._by_faiss_id: Dict[int, Property] = {i: p for i, p in enumerate(self.meta_list)}

        # Опционально поддержим user 'id' если он есть и выглядит как 0..N-1
        self._by_user_id: Dict[int, Property] = {}
        for i, raw in enumerate(self._raw_meta_items):
            if isinstance(raw, dict) and "id" in raw:
                try:
                    uid = int(raw["id"])
                    if 0 <= uid < len(self.meta_list):
                        self._by_user_id[uid] = self.meta_list[i]
                except Exception:
                    # пропускаем некорректные id
                    pass

    # ---------- public API ----------

    def search(self, query_vec: np.ndarray, k: int = 5) -> List[Tuple[float, Property]]:
        """
        query_vec: shape (dim,)
        return: список (distance, Property), где distance — L2 для IndexFlatL2 (меньше — ближе)
        """
        if query_vec.ndim == 1:
            query_vec = query_vec.reshape(1, -1)
        if query_vec.dtype != np.float32:
            query_vec = query_vec.astype(np.float32)

        distances, indices = self.index.search(query_vec, k)
        res: List[Tuple[float, Property]] = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            prop = self._by_faiss_id.get(int(idx))
            if prop is not None:
                res.append((float(dist), prop))
        return res

    def get_by_faiss_id(self, idx: int) -> Property | None:
        return self._by_faiss_id.get(idx)

    def get_by_user_id(self, uid: int) -> Property | None:
        return self._by_user_id.get(uid)

    # ---------- internals ----------

    def _load_meta(self, path: Path) -> List[Property]:
        """
        Поддерживаем форматы:
        - [ {...}, {...}, ... ]
        - { "data": [...]} / {"items":[...]} / {"results":[...]}
        """
        with path.open("r", encoding="utf-8") as f:
            raw = json.load(f)

        # Запомним исходные элементы (для разбора user 'id')
        if isinstance(raw, list):
            items = raw
        elif isinstance(raw, dict):
            # ищем наиболее вероятные ключи со списком
            for key in ("data", "items", "results", "listings", "properties"):
                val = raw.get(key)
                if isinstance(val, list):
                    items = val
                    break
            else:
                # если не нашли — возможно, это словарь вида {"0": {...}, "1": {...}}
                maybe_items = list(raw.values())
                if maybe_items and all(isinstance(x, dict) for x in maybe_items):
                    items = maybe_items
                else:
                    items = []
        else:
            items = []

        self._raw_meta_items = items  # для последующего извлечения user 'id'
        return [Property.from_dict(d) for d in items if isinstance(d, dict)]
