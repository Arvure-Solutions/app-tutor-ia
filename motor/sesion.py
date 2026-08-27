"""Núcleo reutilizable de la sesión del tutor (F2).

Unifica la lógica para CLI, web y loop diario proactivo. No imprime nada por sí
solo: devuelve dicts/strings que cada superficie (terminal, HTML, voz) consume.

Voz: usa `say` nativo de macOS (offline, $0, sin cargar la máquina). En otros
SO, si `say` no existe, la voz es no-op (el resto sigue funcionando).
"""
from __future__ import annotations

import random
import subprocess
from pathlib import Path

import modelo
from modelo import (clave_tarjeta, leccion_por_id, leccion_siguiente,
                    marcar_vista, nuevo_estado, preguntas_de_leccion,
                    registrar_respuesta, resumen_alumno, tarjetas_vencidas,
                    UMBRAL_MAESTRIA)

# Estrategia de evaluación (MockLLM por defecto; cae a matcher si falla)
from modelo import EstrategiaLLM


def _estrategia():
    return EstrategiaLLM()


def armar_cola(curso, estado, solo_repaso=False):
    """Devuelve la cola de (cid, idx) para una sesión retrieval-first.
    Las 4 primeras son repasos vencidos (orden por due); luego nuevas mezcladas."""
    vencidas = tarjetas_vencidas(curso, estado)
    cola = list(vencidas[:4])
    lec = leccion_siguiente(curso, estado) if not solo_repaso else None
    if lec and not solo_repaso:
        cola += [(lec["id"], i) for i in preguntas_de_leccion(curso, estado, lec, cantidad=3)]
    fijas = cola[:4]
    nuevas = cola[4:]
    random.shuffle(nuevas)
    return fijas + nuevas, lec


def responder(curso, estado, cid, idx, texto):
    """Procesa una respuesta del alumno a la tarjeta (cid, idx).
    Devuelve un dict con el resultado del turno (sin imprimir)."""
    lec = leccion_por_id(curso, cid)
    p = lec["preguntas"][idx]
    es_nueva = clave_tarjeta(cid, idx) not in estado["tarjetas"]
    acierto, conf, razon, fuente = _estrategia().evaluar(p, texto, lec)
    if acierto:
        grado = 3 if es_nueva and random.random() < 0.15 else 2
        registrar_respuesta(estado, cid, idx, True, grado=grado)
        modelo.guardar_estado(estado)
        return {
            "acierto": True, "fuente": fuente, "grado": grado,
            "mensaje": "Correcto." if grado == 2 else "Correcto, y fluido: intervalo largo.",
        }
    # incorrecto: damos pista (sin revelar respuesta todavía)
    pista = _estrategia().pista(lec, p, texto)
    return {
        "acierto": False, "fuente": fuente, "grado": None,
        "pista": pista,
        "mensaje": "No del todo. Una pista:",
    }


def segundo_intento(curso, estado, cid, idx, texto):
    """Segunda oportunidad tras la pista. Si acierta, grado=1 (revisar pronto);
    si no, grado=0 y se revela la respuesta."""
    lec = leccion_por_id(curso, cid)
    p = lec["preguntas"][idx]
    acierto, conf, razon, fuente = _estrategia().evaluar(p, texto, lec)
    if acierto:
        registrar_respuesta(estado, cid, idx, True, grado=1)
        modelo.guardar_estado(estado)
        return {"acierto": True, "fuente": fuente, "grado": 1,
                "mensaje": "Mejoró con la pista. Vuelve a repaso pronto."}
    registrar_respuesta(estado, cid, idx, False, grado=0)
    modelo.guardar_estado(estado)
    return {"acierto": False, "fuente": fuente, "grado": 0,
            "mensaje": f"Por ahí no es. Respuesta: {p['a']}"}


def abrir_clase(curso, estado, cid=None):
    if estado is None:
        estado = nuevo_estado()
    lec = leccion_por_id(curso, cid) if cid else leccion_siguiente(curso, estado)
    if lec is None:
        return None, estado
    marcar_vista(estado, lec["id"])
    modelo.guardar_estado(estado)
    return lec, estado


def briefing(curso, estado):
    """Texto corto de arranque del día (loop proactivo)."""
    if estado is None:
        return "Buen día. Abrí tu primera lección con 'clase' para empezar."
    r = resumen_alumno(curso, estado)
    vencidas = r["vencidas"]
    proxima = r["proxima"]
    if vencidas:
        return (f"Tienes {vencidas} repaso(s) vencido(s). "
                f"Hoy toca repasar y seguir con: {proxima}.")
    return f"Todo al día. Seguimos con: {proxima}."


def reporte(curso, estado):
    """Resumen al cerrar el loop."""
    if estado is None:
        return "Sin progreso todavía."
    r = resumen_alumno(curso, estado)
    return (f"Lecciones: {r['lecciones']}. Respuestas: {r['respuestas']}. "
            f"Repasos vencidos: {r['vencidas']}. Próxima: {r['proxima']}.")


def voz_hablar(texto, vel=170):
    """Habla con `say` de macOS (offline). No-op si no existe."""
    try:
        subprocess.run(["say", "-r", str(vel), texto], check=False,
                       timeout=30)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass  # no hay `say` (no es macOS) o tardó demasiado: ignoramos


def loop_diario(curso, estado, hablar=False):
    """Ejecuta el ciclo proactivo: briefing → (clase si hace falta) → sesión →
    reporte. Si `hablar=True`, usa voz en briefing/reporte.
    Devuelve dict con los pasos para que la CLI/UI lo muestre."""
    pasos = []
    b = briefing(curso, estado)
    pasos.append(("briefing", b))
    if hablar:
        voz_hablar(b)

    if estado is None:
        estado = nuevo_estado()

    # si no hay lección vista a medias, abrimos la siguiente
    if leccion_siguiente(curso, estado) is None and not any(
            c.get("visto") for c in estado["conceptos"].values()):
        lec, estado = abrir_clase(curso, estado)
        if lec:
            pasos.append(("clase", f"Lección abierta: {lec['titulo']}"))

    cola, lec = armar_cola(curso, estado)
    if not cola:
        fin = "Nada vencido y sin lección nueva. Volvé mañana."
        pasos.append(("sesion", fin))
        rep = reporte(curso, estado)
        pasos.append(("reporte", rep))
        if hablar:
            voz_hablar(rep)
        return {"pasos": pasos, "estado": estado}

    resultados = []
    for n, (cid, idx) in enumerate(cola, 1):
        lec = leccion_por_id(curso, cid)
        etiqueta = "NUEVA" if clave_tarjeta(cid, idx) not in estado["tarjetas"] else "REPASO"
        r1 = responder(curso, estado, cid, idx, "")
        # En modo loop headless no hay input: simulamos "sin respuesta" → damos
        # pista y revelamos. Para interacción real, la CLI usa responder/segundo_intento.
        if not r1["acierto"]:
            r1 = segundo_intento(curso, estado, cid, idx, "")
        resultados.append({"n": n, "etiqueta": etiqueta, "leccion": lec["titulo"],
                           "acierto": r1["acierto"], "mensaje": r1["mensaje"]})
    pasos.append(("sesion", resultados))

    rep = reporte(curso, estado)
    pasos.append(("reporte", rep))
    if hablar:
        voz_hablar(rep)
    return {"pasos": pasos, "estado": estado}
