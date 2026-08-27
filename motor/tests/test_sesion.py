import json
from pathlib import Path

import pytest

import modelo
from modelo import nuevo_estado, leccion_siguiente
import sesion

RAIZ = Path(__file__).resolve().parent.parent
CURSO = json.loads((RAIZ / "curso_premiere.json").read_text(encoding="utf-8"))


@pytest.fixture
def curso():
    return json.loads(json.dumps(CURSO))


def test_armar_cola_prioriza_vencidas(curso):
    estado = nuevo_estado()
    modelo.marcar_vista(estado, "c01")
    for i in range(len(curso["lecciones"][0]["preguntas"])):
        k = modelo.clave_tarjeta("c01", i)
        estado["tarjetas"][k] = modelo.tarjeta_nueva()
    cola, lec = sesion.armar_cola(curso, estado)
    assert cola
    assert all(c == "c01" for c, _ in cola[:4])


def test_responder_acierto_clave(curso):
    estado = nuevo_estado()
    r = sesion.responder(curso, estado, "c01", 0, "contiene referencia al archivo")
    assert r["acierto"] is True
    assert modelo.clave_tarjeta("c01", 0) in estado["tarjetas"]


def test_responder_falla_da_pista(curso):
    estado = nuevo_estado()
    r = sesion.responder(curso, estado, "c01", 0, "el cielo es azul")
    assert r["acierto"] is False
    assert "pista" in r and r["pista"]


def test_segundo_intento_revela_si_falla(curso):
    estado = nuevo_estado()
    sesion.responder(curso, estado, "c01", 0, "x")
    r2 = sesion.segundo_intento(curso, estado, "c01", 0, "otra vez mal")
    assert r2["acierto"] is False
    assert "Respuesta" in r2["mensaje"]


def test_segundo_intento_acierta_grado1(curso):
    estado = nuevo_estado()
    sesion.responder(curso, estado, "c01", 0, "x")
    r2 = sesion.segundo_intento(curso, estado, "c01", 0, "contiene referencia")
    assert r2["acierto"] is True
    assert r2["grado"] == 1


def test_briefing_sin_estado():
    b = sesion.briefing(CURSO, None)
    assert isinstance(b, str) and b


def test_reporte_con_estado(curso):
    estado = nuevo_estado()
    modelo.marcar_vista(estado, "c01")
    rep = sesion.reporte(CURSO, estado)
    assert "Lecciones" in rep


def test_abrir_clase_marca_vista(curso):
    estado = nuevo_estado()
    lec, estado = sesion.abrir_clase(CURSO, estado)
    assert lec is not None
    assert estado["conceptos"][lec["id"]]["visto"] is True


def test_voz_hablar_no_rompe():
    sesion.voz_hablar("hola mundo", vel=200)


def test_loop_diario_devuelve_pasos(curso):
    estado = nuevo_estado()
    out = sesion.loop_diario(CURSO, estado, hablar=False)
    nombres = [n for n, _ in out["pasos"]]
    assert "briefing" in nombres
    assert "reporte" in nombres


# ---------------------------------------------------------------------------
# Smoke test de la web (headless, sin navegador)
# ---------------------------------------------------------------------------

def test_web_api_headless():
    import threading
    import urllib.request
    import web
    from http.server import ThreadingHTTPServer

    srv = ThreadingHTTPServer(("127.0.0.1", 0), web.Handler)
    port = srv.server_address[1]
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    base = f"http://127.0.0.1:{port}"
    try:
        # '/api/estado' responde JSON
        with urllib.request.urlopen(f"{base}/api/estado", timeout=5) as r:
            data = json.loads(r.read())
        assert "lecciones" in data
        # '/api/clase' abre una lección
        req = urllib.request.Request(f"{base}/api/clase", data=b"{}",
                                     headers={"Content-Type": "application/json"},
                                     method="POST")
        with urllib.request.urlopen(req, timeout=5) as r:
            clase = json.loads(r.read())
        assert "leccion" in clase
        # '/api/sesion' devuelve cola
        req2 = urllib.request.Request(f"{base}/api/sesion", data=b"{}",
                                      headers={"Content-Type": "application/json"},
                                      method="POST")
        with urllib.request.urlopen(req2, timeout=5) as r:
            ses = json.loads(r.read())
        assert "cola" in ses
    finally:
        srv.shutdown()
