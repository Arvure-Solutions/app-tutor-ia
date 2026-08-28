"""Catálogo de la plataforma Tutor IA (F3 — portal multi-dominio).

Carga catalogo.json (dominios disponibles) y resuelve la ruta de un curso
generado para un tema dado. Los cursos generados viven en cursos_generados/<slug>.json
para no pisar los cursos curados (como curso_premiere.json).
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
CATALOGO_PATH = RAIZ.parent / "catalogo.json"
GEN_DIR = RAIZ.parent / "cursos_generados"


def slug(texto: str) -> str:
    """Sanitiza un tema a un slug de archivo (minúsculas, guiones)."""
    s = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s or "curso"


def cargar_catalogo() -> dict:
    return json.loads(CATALOGO_PATH.read_text(encoding="utf-8"))


def dominios() -> list[dict]:
    return cargar_catalogo()["dominios"]


def ruta_curso(slug: str) -> Path:
    GEN_DIR.mkdir(exist_ok=True)
    return GEN_DIR / f"{slug}.json"


def existe_curso(slug: str) -> bool:
    return ruta_curso(slug).exists()


def guardar_curso(slug: str, curso: dict) -> Path:
    GEN_DIR.mkdir(exist_ok=True)
    ruta = ruta_curso(slug)
    ruta.write_text(json.dumps(curso, ensure_ascii=False, indent=2), encoding="utf-8")
    return ruta


def cargar_curso(slug: str) -> dict | None:
    r = ruta_curso(slug)
    if not r.exists():
        return None
    return json.loads(r.read_text(encoding="utf-8"))


def estado_path(slug: str) -> Path:
    return RAIZ / f"estado_{slug}.json"
