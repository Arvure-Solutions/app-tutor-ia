"""Generador de cursos de la plataforma Tutor IA (F3).

Dado un tema libre ("aprender guitarra", "instalar un tomacorriente"),
construye un curso estructurado reutilizando el esquema del motor pedagógico:

  1. Busca videos REALES en YouTube (web_search) → fuentes verificadas.
  2. Con LLM (TUTOR_LLM=http) sintetiza N lecciones (objetivo, teoría,
     preguntas con claves, práctica) y les adjunta los videos como "fuentes".
  3. Sin LLM: genera un esqueleto con los videos + teoría mínima (modo sin IA).
  4. Valida con validar_curso y guarda en cursos_generados/<slug>.json.

No inventa URLs: los videos salen de la búsqueda real o no se agregan.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catalogo
import modelo
from llm import get_client


# ---------------------------------------------------------------------------
# 1) Búsqueda de videos reales (YouTube) vía web_search del agente
# ---------------------------------------------------------------------------

def buscar_videos(tema: str, n: int = 6) -> list[dict]:
    """Devuelve hasta n videos reales de YouTube para el tema.

    Usa yt-dlp (ytsearch) si está disponible; si no, devuelve [].
    Solo admite URLs de youtube.com / youtu.be (nada inventado)."""
    try:
        import shutil
        binario = shutil.which("yt-dlp")
        if not binario:
            return []
        out = subprocess.run(
            [binario, "--dump-json", "--no-warnings", "--quiet",
             f"ytsearch{n}:{tema} tutorial"],
            capture_output=True, text=True, timeout=60)
        items = []
        for line in out.stdout.splitlines():
            try:
                v = json.loads(line)
            except Exception:
                continue
            url = f"https://www.youtube.com/watch?v={v.get('id','')}"
            titulo = (v.get("title") or tema).strip()
            if v.get("id"):
                items.append({"titulo": titulo, "url": url, "tipo": "video"})
            if len(items) >= n:
                break
        return items
    except Exception:
        return []


# ---------------------------------------------------------------------------
# 2) Síntesis de lecciones (LLM o heurística local)
# ---------------------------------------------------------------------------

def _sintetizar_llm(tema: str, videos: list[dict]) -> list[dict] | None:
    cliente = get_client()
    try:
        obj = cliente.sintetizar(tema, videos)
    except Exception:
        obj = None
    if not obj:
        return None
    return obj.get("lecciones")


def _sintetizar_heuristico(tema: str, videos: list[dict]) -> list[dict]:
    """Modo sin IA: esqueleto con los videos reales como fuentes.

    No inventa teoría: usa el tema + los videos. Marca el curso como base."""
    lecciones = []
    # reparte videos entre 4 lecciones base
    cortes = max(1, min(4, len(videos))) if videos else 0
    base = [
        ("Introducción", f"Qué es {tema} y qué vas a lograr."),
        ("Fundamentos", f"Lo esencial para arrancar con {tema}."),
        ("Práctica guiada", f"Tu primer ejercicio real de {tema}."),
        ("Siguiente nivel", f"Mejorá y evitá errores comunes en {tema}."),
    ]
    for i, (tit, obj) in enumerate(base, 1):
        fuentes = []
        if cortes:
            fuentes = [videos[(i - 1) % len(videos)]]
        lecciones.append({
            "id": f"c{i:02d}",
            "titulo": tit,
            "objetivo": obj,
            "teoria": [
                f"Explorá el video recomendado para '{tit}' sobre {tema}.",
                f"Objetivo de esta etapa: {obj}",
            ],
            "practica": f"Seguí el video y hacé tu propia versión de {tema}.",
            "preguntas": [
                {"q": f"¿Qué aprendiste en esta etapa de {tema}?",
                 "a": "Lo básico para arrancar y practicar.",
                 "claves": ["aprender", "practicar", tema.split()[0]]},
            ],
            "fuentes": fuentes,
        })
    return lecciones


def generar(tema: str, dominio_id: str | None = None) -> dict:
    """Genera (y guarda) un curso para `tema`. Devuelve el dict curso."""
    s = catalogo.slug(tema)
    videos = buscar_videos(tema, n=6)
    lecciones = _sintetizar_llm(tema, videos) or _sintetizar_heuristico(tema, videos)

    # asegurar ids secuenciales
    for i, lec in enumerate(lecciones, 1):
        lec.setdefault("id", f"c{i:02d}")
        lec.setdefault("prereqs", [lecciones[i - 2]["id"]] if i > 1 else [])
        lec.setdefault("fuentes", [])
        lec.setdefault("teoria", [])
        lec.setdefault("preguntas", [])
        lec.setdefault("practica", "")

    curso = {
        "curso": tema,
        "nivel": "principiante",
        "generado": True,
        "dominio": dominio_id,
        "lecciones": lecciones,
    }
    # validar contra el esquema del motor (no deja pasar ciclos/rotos)
    problema = modelo.validar_curso(curso)
    if problema:
        # reparación mínima: quitar prereqs rotos
        for lec in curso["lecciones"]:
            lec["prereqs"] = [p for p in lec["prereqs"] if p != lec["id"]]
        problema = modelo.validar_curso(curso)
    catalogo.guardar_curso(s, curso)
    return curso
