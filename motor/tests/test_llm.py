import json

import pytest

from llm import LLMClient, MockLLMClient, HTTPLLMClient, get_client, SYS_GRADING
import llm as llm_mod


LECCION = {
    "id": "c01", "titulo": "Interfaz", "objetivo": "o",
    "prereqs": [], "teoria": ["El .prproj solo guarda referencias a los archivos."],
    "practica": "p",
    "preguntas": [
        {"q": "¿El .prproj contiene el video?", "a": "No, solo referencias.",
         "claves": ["referencia", "no"], "pistas": ["¿Qué pasa si movés el archivo?"]},
    ],
}


# ---------------------------------------------------------------------------
# MockLLMClient (default offline)
# ---------------------------------------------------------------------------

def test_mock_acierta_con_clave():
    c = MockLLMClient()
    g = c.grade(LECCION, LECCION["preguntas"][0], "contiene referencias")
    assert g.acierto is True
    assert g.fuente == "mock"


def test_mock_falla_sin_relacion():
    c = MockLLMClient()
    g = c.grade(LECCION, LECCION["preguntas"][0], "el cielo es azul")
    assert g.acierto is False
    assert g.fuente == "mock"


def test_mock_semantico_por_vocabulario():
    # respuesta sin la clave literal 'referencia' pero con vocabulario de la teoría
    c = MockLLMClient()
    g = c.grade(LECCION, LECCION["preguntas"][0], "guarda las direcciones de los archivos")
    # 'archivos' aparece en la teoría -> solap parcial -> acierto heurístico
    assert g.acierto is True
    assert g.confianza < 0.9  # menor que el match directo de clave


def test_mock_pista_usa_curso_sino_teoria():
    c = MockLLMClient()
    p = c.pista(LECCION, LECCION["preguntas"][0], "x")
    assert "movés" in p  # viene de 'pistas'
    # sin pistas en la pregunta -> usa teoría
    lec2 = {"teoria": ["Punto de teoría de respaldo."]}
    p2 = c.pista(lec2, {"q": "q", "a": "a"}, "x")
    assert "Punto de teoría" in p2


def test_mock_respuesta_vacia():
    c = MockLLMClient()
    g = c.grade(LECCION, LECCION["preguntas"][0], "   ")
    assert g.acierto is False


# ---------------------------------------------------------------------------
# get_client factory
# ---------------------------------------------------------------------------

def test_get_client_default_es_mock(monkeypatch):
    monkeypatch.delenv("TUTOR_LLM", raising=False)
    assert isinstance(get_client(), MockLLMClient)


def test_get_client_http_cuando_env(monkeypatch):
    monkeypatch.setenv("TUTOR_LLM", "http")
    monkeypatch.setenv("TUTOR_LLM_BASE_URL", "http://x/v1")
    monkeypatch.setenv("TUTOR_LLM_MODEL", "m")
    cliente = get_client()
    assert isinstance(cliente, HTTPLLMClient)
    assert cliente.base_url == "http://x/v1"
    assert cliente.model == "m"


# ---------------------------------------------------------------------------
# HTTPLLMClient: parsing sin red (inyectamos _chat)
# ---------------------------------------------------------------------------

def test_http_grade_parsea_json_sin_red():
    c = HTTPLLMClient("http://x/v1", "m")
    c._chat = lambda sys_p, user: json.dumps(
        {"acierto": True, "confianza": 0.95, "razon": "bien"})
    g = c.grade(LECCION, LECCION["preguntas"][0], "resp")
    assert g.acierto is True
    assert g.confianza == 0.95
    assert g.fuente == "http"


def test_http_pista_usa_curso_sino_llm(monkeypatch):
    c = HTTPLLMClient("http://x/v1", "m")
    # sin pistas -> llama al LLM
    calls = {}
    c._chat = lambda s, u: calls.setdefault("r", "Pista generada por modelo")
    p = c.pista({"titulo": "T", "teoria": ["t"]}, {"q": "q", "a": "a"}, "x")
    assert p == "Pista generada por modelo"
    # con pistas -> usa la del curso, no llama al LLM
    c._chat = lambda s, u: "NO DEBERIA LLAMAR"
    p2 = c.pista({"titulo": "T", "teoria": ["t"]},
                 {"q": "q", "a": "a", "pistas": ["pista fija"]}, "x")
    assert p2 == "pista fija"


# ---------------------------------------------------------------------------
# EstrategiaLLM con fallback (en modelo.py)
# ---------------------------------------------------------------------------

def test_estrategia_llm_usa_client(monkeypatch):
    from modelo import EstrategiaLLM
    cliente = MockLLMClient()
    estr = EstrategiaLLM(client=cliente)
    res = estr.evaluar(LECCION["preguntas"][0], "contiene referencias", LECCION)
    assert res[0] is True
    assert res[3] == "mock"


def test_estrategia_llm_fallback_en_error(monkeypatch):
    from modelo import EstrategiaLLM, MatcherClaves

    class Roto(LLMClient):
        def grade(self, leccion, pregunta, respuesta_alumno):
            raise RuntimeError("red caída")

        def pista(self, leccion, pregunta, respuesta_alumno):
            raise RuntimeError("x")

    estr = EstrategiaLLM(client=Roto(), matcher=MatcherClaves())
    res = estr.evaluar({"q": "q", "a": "a", "claves": ["referencia"]},
                       "contiene referencia", LECCION)
    # cae al matcher: acierto True, fuente matcher-fallback
    assert res[0] is True
    assert res[3].startswith("matcher-fallback")
    # pista también cae al matcher/curso
    p = estr.pista(LECCION, LECCION["preguntas"][0], "x")
    assert "movés" in p
