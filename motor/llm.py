"""Capa LLM del Tutor IA (F1) — pluggable y con default offline.

Presupuesto cero / sin cargar la máquina: por defecto se usa `MockLLMClient`,
una heurística offline sobre el contenido del curso. No consume red ni recursos.

Para conectar un modelo real (Ollama local, Groq, OpenAI, Together...), todas
OpenAI-compatible, basta con setear variables de entorno — sin tocar código:

    TUTOR_LLM=http            # activa el cliente HTTP
    TUTOR_LLM_BASE_URL=http://localhost:11434/v1   # Ollama
    TUTOR_LLM_MODEL=llama3.1
    TUTOR_LLM_API_KEY=sk-...  # opcional (Ollama no la requiere)
    TUTOR_LLM_TIMEOUT=20

Si la llamada HTTP falla (sin red, key inválida, modelo ausente) el motor
cae automáticamente al matcher por claves para no quedarse mudo.
"""
from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass, field
from typing import Optional

from modelo import normalizar

SYS_GRADING = (
    "Sos un tutor experto de edición de video. Vas a recibir la teoría de una "
    "lección, la pregunta, la respuesta correcta esperada y la respuesta de un "
    "alumno. Tu trabajo: decidir si el alumno demostró entender el concepto "
    "(no si copió palabra por palabra), y si no, dar una pista socrática breve "
    "que lo ayude a llegar solo. Responde SOLO JSON con esta forma:\n"
    '{"acierto": true|false, "confianza": 0.0-1.0, "razon": "..."}'
)


@dataclass
class GradeResult:
    acierto: bool
    confianza: float
    razon: str
    pista: Optional[str] = None
    fuente: str = "mock"  # 'mock' | 'http' | 'matcher-fallback'


class LLMClient:
    """Interfaz de cliente LLM. Subclases: MockLLMClient, HTTPLLMClient."""

    def grade(self, leccion, pregunta, respuesta_alumno) -> GradeResult:
        raise NotImplementedError

    def pista(self, leccion, pregunta, respuesta_alumno) -> str:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Mock: heurística offline, cero red, cero recursos
# ---------------------------------------------------------------------------


class MockLLMClient(LLMClient):
    """Imita un tutor usando los datos del curso (teoría + claves + respuesta).
    No es perfecto, pero da grading semántico barato sin salir del proceso."""

    def grade(self, leccion, pregunta, respuesta_alumno) -> GradeResult:
        texto = normalizar(respuesta_alumno)
        if not texto:
            return GradeResult(False, 0.6, "respuesta vacía", fuente="mock")

        claves = pregunta.get("claves", [])
        claves_hit = [c for c in claves if normalizar(c) in texto]
        # coincidencia de claves (igual que el matcher, pero con reporte)
        if claves_hit:
            return GradeResult(
                True, 0.9,
                f"menciona el concepto clave ({claves_hit[0]})",
                fuente="mock",
            )

        # heurística semántica barata: ¿la respuesta del alumno comparte
        # palabras sustantivas con la respuesta esperada o la teoría?
        # (filtramos stopwords para no casar sobre "el/es/de/...")
        stop = {"el", "la", "los", "las", "un", "una", "de", "del", "que", "es",
                "son", "se", "su", "sus", "y", "o", "a", "en", "por", "para", "con",
                "no", "si", "lo", "le", "al", "una", "como", "pero", "muy", "mas"}
        ref = normalizar(pregunta.get("a", ""))
        teoria = " ".join(normalizar(t) for t in leccion.get("teoria", []))
        palabras_ref = {w for w in set(ref.split()) | set(teoria.split()) if len(w) >= 4}
        palabras_ref -= stop
        palabras_alumno = {w for w in texto.split() if len(w) >= 4} - stop
        solap = palabras_alumno & palabras_ref
        if solap:
            # coincidencia parcial de vocabulario → probablemente entendió
            return GradeResult(
                True, 0.6,
                f"usa vocabulario correcto ({', '.join(sorted(solap)[:3])})",
                fuente="mock",
            )
        return GradeResult(
            False, 0.7,
            "no coincide con el concepto esperado",
            fuente="mock",
        )

    def pista(self, leccion, pregunta, respuesta_alumno) -> str:
        # preferencia: pista currada del curso, si existe
        if pregunta.get("pistas"):
            return pregunta["pistas"][0]
        # si no, deriva una pista del primer punto de teoría relevante
        return f"Repasá este punto: {leccion['teoria'][0]}"


# ---------------------------------------------------------------------------
# HTTP: OpenAI-compatible, opt-in por env vars
# ---------------------------------------------------------------------------


class HTTPLLMClient(LLMClient):
    def __init__(self, base_url, model, api_key="", timeout=20):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout = timeout

    def _chat(self, system, user):
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.0,
            "response_format": {"type": "json_object"},
        }
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]

    def grade(self, leccion, pregunta, respuesta_alumno) -> GradeResult:
        user = (
            f"TEORÍA:\n{chr(10).join('- ' + t for t in leccion['teoria'])}\n\n"
            f"PREGUNTA: {pregunta['q']}\n"
            f"RESPUESTA ESPERADA: {pregunta.get('a', '')}\n"
            f"RESPUESTA DEL ALUMNO: {respuesta_alumno}\n\n"
            "Decidí: ¿el alumno entendió el concepto?"
        )
        raw = self._chat(SYS_GRADING, user)
        obj = json.loads(raw)
        return GradeResult(
            bool(obj.get("acierto", False)),
            float(obj.get("confianza", 0.5)),
            str(obj.get("razon", "")),
            fuente="http",
        )

    def pista(self, leccion, pregunta, respuesta_alumno) -> str:
        if pregunta.get("pistas"):
            return pregunta["pistas"][0]
        try:
            user = (
                f"LECCIÓN: {leccion['titulo']}\n"
                f"PREGUNTA: {pregunta['q']}\n"
                f"RESPUESTA ESPERADA: {pregunta.get('a', '')}\n"
                f"RESPUESTA INCORRECTA DEL ALUMNO: {respuesta_alumno}\n\n"
                "Dá una pista socrática de UNA frase que lo ayude a llegar solo, "
                "sin dar la respuesta."
            )
            return self._chat(
                "Sos un tutor que guía con preguntas, nunca da la respuesta directa.",
                user,
            ).strip()
        except Exception:
            return leccion["teoria"][0]


# ---------------------------------------------------------------------------
# Factory: elige el cliente según env (default mock)
# ---------------------------------------------------------------------------


def get_client() -> LLMClient:
    if os.environ.get("TUTOR_LLM", "").lower() == "http":
        return HTTPLLMClient(
            base_url=os.environ.get("TUTOR_LLM_BASE_URL", "http://localhost:11434/v1"),
            model=os.environ.get("TUTOR_LLM_MODEL", "llama3.1"),
            api_key=os.environ.get("TUTOR_LLM_API_KEY", ""),
            timeout=int(os.environ.get("TUTOR_LLM_TIMEOUT", "20")),
        )
    return MockLLMClient()
