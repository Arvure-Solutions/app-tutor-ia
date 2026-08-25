import json
from datetime import datetime, timedelta
from pathlib import Path

BKT_INICIO = 0.15
BKT_APRENDE = 0.12
BKT_ERROR_HUMANO = 0.12
BKT_ADIVINA = 0.20
UMBRAL_MAESTRIA = 0.80

RAIZ = Path(__file__).resolve().parent
ESTADO_PATH = RAIZ / "estado_alumno.json"


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


def tarjeta_nueva():
    return {"ease": 2.5, "intervalo_d": 0.007, "reps": 0, "lapsus": 0, "due": _ahora().isoformat()}


def fsrs_lite_programar(tarjeta, grado):
    if grado == 0:
        tarjeta["reps"] = 0
        tarjeta["lapsus"] += 1
        tarjeta["ease"] = max(1.3, tarjeta["ease"] - 0.20)
        tarjeta["intervalo_d"] = 0.007
    elif grado == 1:
        tarjeta["reps"] += 1
        tarjeta["ease"] = max(1.3, tarjeta["ease"] - 0.15)
        tarjeta["intervalo_d"] = max(0.02, tarjeta["intervalo_d"] * 1.2)
    elif grado == 2:
        tarjeta["reps"] += 1
        tarjeta["intervalo_d"] = min(180.0, max(0.02, tarjeta["intervalo_d"] * tarjeta["ease"]))
    else:
        tarjeta["reps"] += 1
        tarjeta["ease"] = min(3.0, tarjeta["ease"] + 0.15)
        tarjeta["intervalo_d"] = min(180.0, tarjeta["intervalo_d"] * tarjeta["ease"] * 1.3)
    tarjeta["due"] = (_ahora() + timedelta(days=tarjeta["intervalo_d"])).isoformat()
    return tarjeta


def concepto_nuevo():
    return {"bkt": BKT_INICIO, "visto": False, "intentos": 0, "aciertos": 0}


def nuevo_estado(alumno="alumno"):
    return {"alumno": alumno, "creado": _ahora().isoformat(),
            "conceptos": {}, "tarjetas": {}, "historia": []}


def cargar_estado():
    if ESTADO_PATH.exists():
        return json.loads(ESTADO_PATH.read_text(encoding="utf-8"))
    return None


def guardar_estado(estado):
    ESTADO_PATH.write_text(json.dumps(estado, indent=2, ensure_ascii=False), encoding="utf-8")


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
        "respuestas": f"{len(h)} respuestas · {100 * aciertos // len(h)}% acierto" if h else "sin respuestas aún",
        "vencidas": len(tarjetas_vencidas(curso, estado)),
        "proxima": proxima["titulo"] if proxima else "(curso completado o bloqueado)",
    }
