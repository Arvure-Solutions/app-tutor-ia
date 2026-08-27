import json
import random
from pathlib import Path

import pytest

import modelo
from modelo import (bkt_actualizar, fsrs_lite_programar, tarjeta_nueva,
                    validar_curso, validar_estado, orden_topologico,
                    diagnosticar, MatcherClaves, normalizar,
                    leccion_siguiente, prereqs_cumplidos, nuevo_estado)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

CURSO_MIN = {
    "curso": "test",
    "lecciones": [
        {"id": "a", "titulo": "A", "objetivo": "oa",
         "prereqs": [], "teoria": ["t"], "practica": "p",
         "preguntas": [{"q": "qa", "a": "aa", "claves": ["x"]}]},
        {"id": "b", "titulo": "B", "objetivo": "ob",
         "prereqs": ["a"], "teoria": ["t"], "practica": "p",
         "preguntas": [{"q": "qb", "a": "ab", "claves": ["y"]}]},
    ],
}


@pytest.fixture
def curso():
    return json.loads(json.dumps(CURSO_MIN))


# ---------------------------------------------------------------------------
# BKT
# ---------------------------------------------------------------------------

def test_bkt_acierto_subey_techo():
    p = bkt_actualizar(0.5, True)
    assert p > 0.5
    assert p <= 0.99


def test_bkt_error_baja_y_piso():
    p = bkt_actualizar(0.7, False)
    assert p < 0.7
    assert p >= 0.0


def test_bkt_deterministico():
    assert bkt_actualizar(0.3, True) == bkt_actualizar(0.3, True)


# ---------------------------------------------------------------------------
# FSRS-lite
# ---------------------------------------------------------------------------

def test_fsrs_again_resetea():
    t = tarjeta_nueva()
    t["reps"] = 3
    t["intervalo_d"] = 10.0
    fsrs_lite_programar(t, 0)
    assert t["reps"] == 0
    assert t["lapsus"] == 1
    assert t["intervalo_d"] == 0.007


def test_fsrs_good_crece_intervalo():
    t = tarjeta_nueva()
    t["intervalo_d"] = 1.0
    before = t["intervalo_d"]
    fsrs_lite_programar(t, 2)
    assert t["intervalo_d"] > before


def test_fsrs_intervalo_tiene_techo():
    t = tarjeta_nueva()
    t["intervalo_d"] = 999.0
    t["ease"] = 3.0
    fsrs_lite_programar(t, 3)
    assert t["intervalo_d"] <= 180.0


# ---------------------------------------------------------------------------
# Validación de curso
# ---------------------------------------------------------------------------

def test_curso_valido_pasa(curso):
    assert validar_curso(curso) is None


def test_curso_faltan_preguntas(curso):
    del curso["lecciones"][0]["preguntas"]
    assert validar_curso(curso) is not None


def test_curso_id_duplicado(curso):
    curso["lecciones"].append(dict(curso["lecciones"][0]))
    curso["lecciones"][-1]["id"] = "a"
    assert "duplicado" in validar_curso(curso)


def test_curso_prereq_inexistente(curso):
    curso["lecciones"][1]["prereqs"] = ["zzz"]
    assert "no existe" in validar_curso(curso)


def test_curso_ciclo_detectado():
    curso = {
        "lecciones": [
            {"id": "a", "titulo": "A", "objetivo": "oa", "prereqs": ["b"],
             "teoria": ["t"], "practica": "p", "preguntas": [{"q": "qa", "a": "aa"}]},
            {"id": "b", "titulo": "B", "objetivo": "ob", "prereqs": ["a"],
             "teoria": ["t"], "practica": "p", "preguntas": [{"q": "qb", "a": "ab"}]},
        ]
    }
    msg = validar_curso(curso)
    assert msg is not None
    assert "ciclo" in msg


def test_orden_topologico_ciclo_lanza():
    curso = {
        "lecciones": [
            {"id": "a", "titulo": "A", "objetivo": "oa", "prereqs": ["b"],
             "teoria": ["t"], "practica": "p", "preguntas": [{"q": "qa", "a": "aa"}]},
            {"id": "b", "titulo": "B", "objetivo": "ob", "prereqs": ["a"],
             "teoria": ["t"], "practica": "p", "preguntas": [{"q": "qb", "a": "ab"}]},
        ]
    }
    with pytest.raises(ValueError):
        orden_topologico(curso)


def test_orden_topologico_respeta_prereqs():
    orden = orden_topologico(CURSO_MIN)
    assert orden.index("a") < orden.index("b")


# ---------------------------------------------------------------------------
# Matcher / evaluación enchufable
# ---------------------------------------------------------------------------

def test_matcher_acierta_con_clave():
    p = {"q": "q", "a": "a", "claves": ["referencia"]}
    ok, conf, _ = MatcherClaves().evaluar(p, "contiene referencia al archivo")
    assert ok is True
    assert 0 <= conf <= 1


def test_matcher_falla_sin_clave():
    p = {"q": "q", "a": "a", "claves": ["referencia"]}
    ok, _, _ = MatcherClaves().evaluar(p, "no tiene nada que ver")
    assert ok is False


def test_normalizar_quita_tildes_y_signos():
    assert "referencia" in normalizar("¡Referencia!")


# ---------------------------------------------------------------------------
# Diagnóstico de placement
# ---------------------------------------------------------------------------

def _evaluar_todo_falso(lec, p):
    return {"acierto": False}


def _evaluar_todo_verdadero(lec, p):
    return {"acierto": True}


def test_diagnostico_marca_dominadas():
    estado = nuevo_estado()
    res = diagnosticar(CURSO_MIN, estado, _evaluar_todo_verdadero, rng=random)
    assert all(a for *_, a in res)
    # a dominada => b desbloquea
    assert prereqs_cumplidos(CURSO_MIN, estado, CURSO_MIN["lecciones"][1])


def test_diagnostico_no_propagas_si_falla():
    estado = nuevo_estado()
    diagnosticar(CURSO_MIN, estado, _evaluar_todo_falso, rng=random)
    # nada dominado => siguiente sigue siendo la primera
    assert leccion_siguiente(CURSO_MIN, estado)["id"] == "a"


# ---------------------------------------------------------------------------
# Robustez de guardado/carga (con path aislado)
# ---------------------------------------------------------------------------

def test_guardar_cargar_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(modelo, "ESTADO_PATH", tmp_path / "estado.json")
    from modelo import guardar_estado, cargar_estado
    e = nuevo_estado("x")
    guardar_estado(e)
    e2 = cargar_estado()
    assert e2["alumno"] == "x"


def test_cargar_json_corrupto_lanza(tmp_path, monkeypatch):
    monkeypatch.setattr(modelo, "ESTADO_PATH", tmp_path / "estado.json")
    from modelo import guardar_estado, cargar_estado
    tmp_path.joinpath("estado.json").write_text("{esto no es json", encoding="utf-8")
    with pytest.raises(RuntimeError):
        cargar_estado()


def test_validar_estado_falta_clave():
    assert validar_estado({"alumno": "x"}) is not None
    assert validar_estado(nuevo_estado()) is None
