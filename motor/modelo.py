import json
import random
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

BKT_INICIO = 0.15
BKT_APRENDE = 0.12
BKT_ERROR_HUMANO = 0.12
BKT_ADIVINA = 0.20
UMBRAL_MAESTRIA = 0.80

RAIZ = Path(__file__).resolve().parent
ESTADO_PATH = RAIZ / "estado_alumno.json"

# ---------------------------------------------------------------------------
# BKT — Bayesian Knowledge Tracing
# ---------------------------------------------------------------------------


def _ahora():
    return datetime.now().astimezone()


def bkt_actualizar(p, correcto):
    if correcto:
        num = p * (1 - BKT_ERROR_HUMANO)
        den = num + (1 - p) * BKT_ADIVINA
    else:
        num = p * BKT_ERROR_HUMANO
        den = num + (1 - p) * (1 - BKT_ADIVINA)
    pc = num / den if den else 0.0
    return min(pc + (1 - pc) * BKT_APRENDE, 0.99)


# ---------------------------------------------------------------------------
# FSRS-lite — planificación de repaso espaciado (grados again/hard/good/easy)
# ---------------------------------------------------------------------------


def tarjeta_nueva():
    return {"ease": 2.5, "intervalo_d": 0.007, "reps": 0, "lapsus": 0,
            "due": _ahora().isoformat()}


def fsrs_lite_programar(tarjeta, grado):
    if grado == 0:  # again
        tarjeta["reps"] = 0
        tarjeta["lapsus"] += 1
        tarjeta["ease"] = max(1.3, tarjeta["ease"] - 0.20)
        tarjeta["intervalo_d"] = 0.007
    elif grado == 1:  # hard
        tarjeta["reps"] += 1
        tarjeta["ease"] = max(1.3, tarjeta["ease"] - 0.15)
        tarjeta["intervalo_d"] = max(0.02, tarjeta["intervalo_d"] * 1.2)
    elif grado == 2:  # good
        tarjeta["reps"] += 1
        tarjeta["intervalo_d"] = min(180.0, max(0.02,
                                                tarjeta["intervalo_d"] * tarjeta["ease"]))
    else:  # grade 3: easy
        tarjeta["reps"] += 1
        tarjeta["ease"] = min(3.0, tarjeta["ease"] + 0.15)
        tarjeta["intervalo_d"] = min(180.0, tarjeta["intervalo_d"] * tarjeta["ease"] * 1.3)
    tarjeta["due"] = (_ahora() + timedelta(days=tarjeta["intervalo_d"])).isoformat()
    return tarjeta


# ---------------------------------------------------------------------------
# Estado del alumno
# ---------------------------------------------------------------------------


def concepto_nuevo():
    return {"bkt": BKT_INICIO, "visto": False, "intentos": 0, "aciertos": 0}


def nuevo_estado(alumno="alumno"):
    return {"alumno": alumno, "creado": _ahora().isoformat(),
            "conceptos": {}, "tarjetas": {}, "historia": []}


def cargar_estado():
    if ESTADO_PATH.exists():
        try:
            raw = json.loads(ESTADO_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise RuntimeError(
                f"estado_alumno.json corrupto: {exc}. Borralo o restaura un backup."
            ) from exc
        problema = validar_estado(raw)
        if problema:
            raise RuntimeError(
                f"estado_alumno.json inválido: {problema}. Borralo o restaura un backup."
            )
        return raw
    return None


def guardar_estado(estado):
    """Escritura atómica: escribe a temp y renombra, para no dejar JSON roto
    si el proceso muere a mitad de escritura."""
    tmp = None
    try:
        fh = tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=str(ESTADO_PATH.parent),
            prefix=".estado_tmp_", suffix=".json", delete=False)
        tmp = fh.name
        json.dump(estado, fh, indent=2, ensure_ascii=False)
        fh.flush()
        Path(tmp).replace(ESTADO_PATH)  # atómico en POSIX
    finally:
        if tmp and Path(tmp).exists():
            try:
                Path(tmp).unlink()
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Tarjetas / conceptos
# ---------------------------------------------------------------------------


def clave_tarjeta(cid, idx):
    return f"{cid}::{idx}"


def asegurar_concepto(estado, cid):
    return estado["conceptos"].setdefault(cid, concepto_nuevo())


def marcar_vista(estado, cid):
    c = asegurar_concepto(estado, cid)
    c["visto"] = True


def registrar_respuesta(estado, cid, idx, correcto, grado=None):
    c = asegurar_concepto(estado, cid)
    c["intentos"] += 1
    c["aciertos"] += 1 if correcto else 0
    c["bkt"] = bkt_actualizar(c["bkt"], correcto)
    k = clave_tarjeta(cid, idx)
    t = estado["tarjetas"].setdefault(k, tarjeta_nueva())
    if grado is None:
        grado = 2 if correcto else 0
    fsrs_lite_programar(t, grado)
    estado["historia"].append({
        "t": _ahora().isoformat(), "tarjeta": k,
        "correcto": correcto, "grado": grado, "bkt": round(c["bkt"], 3),
    })
    return estado


# ---------------------------------------------------------------------------
# Grafo de prerrequisitos + planificación
# ---------------------------------------------------------------------------


def prereqs_cumplidos(curso, estado, leccion):
    return all(estado.get("conceptos", {}).get(p, {}).get("bkt", 0) >= UMBRAL_MAESTRIA
               for p in leccion["prereqs"])


def leccion_siguiente(curso, estado):
    for lec in curso["lecciones"]:
        c = estado["conceptos"].get(lec["id"])
        dominada = c and c["bkt"] >= UMBRAL_MAESTRIA
        if not dominada and prereqs_cumplidos(curso, estado, lec):
            return lec
    return None


def tarjetas_vencidas(curso, estado, limite=50):
    ahora = _ahora()
    vencidas = []
    for lec in curso["lecciones"]:
        for i, _ in enumerate(lec["preguntas"]):
            k = clave_tarjeta(lec["id"], i)
            t = estado["tarjetas"].get(k)
            if t and datetime.fromisoformat(t["due"]) <= ahora:
                vencidas.append((lec["id"], i))
                if len(vencidas) >= limite:
                    return vencidas
    vencidas.sort(key=lambda ci: estado["tarjetas"][clave_tarjeta(*ci)]["due"])
    return vencidas


def preguntas_de_leccion(curso, estado, lec, cantidad=3):
    candidatas = []
    for i, _ in enumerate(lec["preguntas"]):
        k = clave_tarjeta(lec["id"], i)
        t = estado["tarjetas"].get(k)
        prioridad = 0 if t is None else (1 if t["lapsus"] > 0 else 2)
        candidatas.append((prioridad, i))
    candidatas.sort(key=lambda x: x[0])
    return [i for _, i in candidatas[:cantidad]]


def resumen_alumno(curso, estado):
    total_l = len(curso["lecciones"])
    vistas = sum(1 for l in curso["lecciones"]
                 if estado["conceptos"].get(l["id"], {}).get("visto"))
    dominadas = sum(1 for l in curso["lecciones"]
                    if estado["conceptos"].get(l["id"], {}).get("bkt", 0) >= UMBRAL_MAESTRIA)
    h = estado["historia"]
    aciertos = sum(1 for r in h if r["correcto"])
    proxima = leccion_siguiente(curso, estado)
    return {
        "lecciones": f"{vistas}/{total_l} vistas · {dominadas}/{total_l} dominadas",
        "respuestas": f"{len(h)} respuestas · {100 * aciertos // len(h)}% acierto" if h
                      else "sin respuestas aún",
        "vencidas": len(tarjetas_vencidas(curso, estado)),
        "proxima": proxima["titulo"] if proxima else "(curso completado o bloqueado)",
    }


# ---------------------------------------------------------------------------
# Validación de curso y estado (robustez: detecta JSON mal formado / ciclos)
# ---------------------------------------------------------------------------


def validar_curso(curso):
    """Devuelve None si el curso es válido, o un mensaje de error (str)."""
    if not isinstance(curso, dict):
        return "el curso no es un objeto JSON"
    if "lecciones" not in curso:
        return "falta la clave 'lecciones'"
    lecciones = curso["lecciones"]
    if not isinstance(lecciones, list) or not lecciones:
        return "'lecciones' debe ser una lista no vacía"

    # Pasada 1: recolectar ids + validar estructura de cada lección (sin prereqs)
    ids = set()
    for i, lec in enumerate(lecciones):
        donde = f"lección #{i}"
        if not isinstance(lec, dict):
            return f"{donde}: no es un objeto"
        if "id" not in lec:
            return f"{donde}: falta 'id'"
        cid = lec["id"]
        if cid in ids:
            return f"id duplicado: {cid}"
        ids.add(cid)
        for campo in ("titulo", "objetivo"):
            if not lec.get(campo):
                return f"{donde} ({cid}): falta '{campo}'"
        if not isinstance(lec.get("prereqs", []), list):
            return f"{donde} ({cid}): 'prereqs' debe ser lista"
        if "teoria" not in lec or not isinstance(lec["teoria"], list) or not lec["teoria"]:
            return f"{donde} ({cid}): 'teoria' debe ser lista no vacía"
        if "preguntas" not in lec or not isinstance(lec["preguntas"], list) \
                or not lec["preguntas"]:
            return f"{donde} ({cid}): 'preguntas' debe ser lista no vacía"
        for j, p in enumerate(lec["preguntas"]):
            if not isinstance(p, dict) or not p.get("q") or "a" not in p:
                return f"{donde} ({cid}): pregunta #{j} inválida (requiere 'q' y 'a')"

    # Pasada 2: existencia de prereqs + detección de ciclos (grafo completo ya conocido)
    for lec in lecciones:
        for pr in lec.get("prereqs", []):
            if pr not in ids:
                return f"{lec['id']}: prereq '{pr}' no existe en el curso"

    visitado = {}
    for lec in lecciones:
        cid = lec["id"]
        if visitado.get(cid) == 2:
            continue
        stack = [(cid, iter(lec.get("prereqs", [])))]
        while stack:
            nodo, it = stack[-1]
            visitado[nodo] = 1  # en proceso
            try:
                sig = next(it)
            except StopIteration:
                visitado[nodo] = 2  # listo
                stack.pop()
                continue
            if visitado.get(sig) == 1:
                return f"ciclo de prerrequisitos detectado en '{sig}'"
            if visitado.get(sig) is None:
                dest = next((l for l in lecciones if l["id"] == sig), None)
                if dest:
                    stack.append((sig, iter(dest.get("prereqs", []))))
    return None


def validar_estado(estado):
    if not isinstance(estado, dict):
        return "no es un objeto"
    for clave in ("alumno", "conceptos", "tarjetas", "historia"):
        if clave not in estado:
            return f"falta '{clave}'"
    return None


# ---------------------------------------------------------------------------
# Evaluación enchufable (hoy: matcher por claves; mañana: LLM semántico)
# ---------------------------------------------------------------------------


def normalizar(s):
    import re
    return re.sub(r"[^a-z0-9 ]", "", str(s).lower())


class EstrategiaEvaluacion:
    """Interfaz de evaluación. Subclases implementan evaluar(pregunta, respuesta)
    -> (acierto: bool, confianza: float 0..1, razon: str)."""

    def evaluar(self, pregunta, respuesta):
        raise NotImplementedError


class MatcherClaves(EstrategiaEvaluacion):
    def evaluar(self, pregunta, respuesta):
        texto = normalizar(respuesta)
        claves = pregunta.get("claves", [])
        if not claves:
            return False, 0.0, "sin claves de corrección"
        if any(normalizar(c) in texto for c in claves):
            return True, 0.9, "contiene clave de corrección"
        return False, 0.9, "no contiene clave de corrección"


def evaluar_respuesta(pregunta, respuesta, estrategia=None):
    if estrategia is None:
        estrategia = MatcherClaves()
    return estrategia.evaluar(pregunta, respuesta)


# ---------------------------------------------------------------------------
# Diagnóstico de placement (complejidad pedagógica)
# ---------------------------------------------------------------------------


def diagnosticar(curso, estado, evaluar, n_por_leccion=1, rng=None):
    """Recorre las lecciones EN ORDEN TOPOLÓGICO (respetando prereqs) y hace
    una pregunta de diagnóstico por lección. Si el alumno la acierta, se marca
    la lección como dominada (BKT=1.0, visto=True) y se propaga al resto de sus
    tarjetas. Devuelve la lista de (id, pregunta, respuesta, acierto)."""
    rng = rng or random
    orden = orden_topologico(curso)
    resultados = []
    for cid in orden:
        lec = next(l for l in curso["lecciones"] if l["id"] == cid)
        if not prereqs_cumplidos(curso, estado, lec):
            continue  # no se puede diagnosticar si falta base
        preguntas = list(lec["preguntas"])
        rng.shuffle(preguntas)
        p = preguntas[0]
        resp = evaluar(lec, p)
        acierto = bool(resp.get("acierto")) if isinstance(resp, dict) else bool(resp)
        resultados.append((cid, p, resp, acierto))

        c = asegurar_concepto(estado, cid)
        c["visto"] = True
        if acierto:
            c["bkt"] = 1.0
            c["aciertos"] = c.get("intentos", 0) + 1
            c["intentos"] = c.get("intentos", 0) + 1
            # propaga a todas las tarjetas como dominadas
            for i in range(len(lec["preguntas"])):
                k = clave_tarjeta(cid, i)
                t = estado["tarjetas"].setdefault(k, tarjeta_nueva())
                fsrs_lite_programar(t, 2)
        else:
            c["intentos"] = c.get("intentos", 0) + 1
    return resultados


def orden_topologico(curso):
    """Orden topológico estable por índice de aparición. Detecta ciclos."""
    by_id = {l["id"]: l for l in curso["lecciones"]}
    grado = {l["id"]: 0 for l in curso["lecciones"]}
    ady = {l["id"]: [] for l in curso["lecciones"]}
    for l in curso["lecciones"]:
        for pr in l.get("prereqs", []):
            if pr in by_id:
                grado[l["id"]] += 1
                ady[pr].append(l["id"])
    cola = sorted([cid for cid, g in grado.items() if g == 0])
    orden = []
    while cola:
        n = cola.pop(0)
        orden.append(n)
        for m in sorted(ady[n]):
            grado[m] -= 1
            if grado[m] == 0:
                cola.append(m)
    if len(orden) != len(grado):
        raise ValueError("ciclo de prerrequisitos: no hay orden topológico")
    return orden
