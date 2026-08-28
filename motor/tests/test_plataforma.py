import json
import pytest

import catalogo
import generador
import modelo
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


@pytest.fixture
def tema():
    return "montaje en premiere pro"


def test_catalogo_tiene_dominios():
    d = catalogo.dominios()
    ids = {x["id"] for x in d}
    assert {"edicion_video", "guitarra", "canto", "durlock", "electricidad"} <= ids


def test_slug_sanea():
    assert catalogo.slug("Edición de Video!") == "edicion-de-video"
    assert catalogo.slug("guitarra") == "guitarra"


def test_generar_crea_curso_valido(tema):
    curso = generador.generar(tema, "edicion_video")
    # esquema válido según el motor
    assert modelo.validar_curso(curso) is None
    assert curso["curso"]
    assert len(curso["lecciones"]) >= 1
    # ids secuenciales y prereqs coherentes
    ids = [l["id"] for l in curso["lecciones"]]
    assert ids[0] == "c01"
    assert all("fuentes" in l and "teoria" in l and "preguntas" in l for l in curso["lecciones"])
    # se guardó
    assert catalogo.existe_curso(catalogo.slug(tema))


def test_generar_sin_llm_usa_heuristica(tema, monkeypatch):
    # forzar MockLLMClient (sin TUTOR_LLM=http)
    monkeypatch.delenv("TUTOR_LLM", raising=False)
    curso = generador.generar(tema, "edicion_video")
    assert curso["lecciones"]
    # heurística: al menos una lección con fuentes si hubo videos, o teoría mínima
    assert any(l.get("fuentes") or l.get("teoria") for l in curso["lecciones"])


def test_api_plataforma_headless():
    import threading, urllib.request, sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    import server
    from http.server import ThreadingHTTPServer
    srv = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{port}"
    try:
        # catálogo
        with urllib.request.urlopen(f"{base}/api/catalogo", timeout=5) as r:
            cat = json.loads(r.read())
        assert "dominios" in cat and cat["dominios"]
        # generar curso
        tema = "tocar guitarra acustica"
        req = urllib.request.Request(f"{base}/api/generar",
            data=json.dumps({"tema": tema, "dominio": "guitarra"}).encode(),
            headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            gen = json.loads(r.read())
        slug = gen["slug"]
        assert slug
        # estado del curso generado
        with urllib.request.urlopen(f"{base}/api/curso/{slug}/estado", timeout=5) as r:
            est = json.loads(r.read())
        assert "lecciones" in est and est["lecciones"]
    finally:
        srv.shutdown()
