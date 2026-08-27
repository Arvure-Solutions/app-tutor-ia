import argparse
import json
import random
import re
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from modelo import (ESTADO_PATH, UMBRAL_MAESTRIA, cargar_estado, clave_tarjeta,
                    guardar_estado, marcar_vista, nuevo_estado,
                    preguntas_de_leccion, registrar_respuesta, resumen_alumno,
                    tarjetas_vencidas, validar_curso, evaluar_respuesta,
                    MatcherClaves, EstrategiaLLM, diagnosticar, leccion_siguiente,
                    orden_topologico, prereqs_cumplidos)
import modelo

RAIZ = Path(__file__).resolve().parent
CURSO_DEFAULT = RAIZ / "curso_premiere.json"


def cargar_curso(ruta=None):
    curso_path = Path(ruta) if ruta else CURSO_DEFAULT
    if not curso_path.is_absolute():
        curso_path = RAIZ / curso_path
    raw = json.loads(curso_path.read_text(encoding="utf-8"))
    problema = validar_curso(raw)
    if problema:
        print(f"❌ Curso inválido: {problema}", file=sys.stderr)
        sys.exit(1)
    return raw


def leccion_por_id(curso, cid):
    for l in curso["lecciones"]:
        if l["id"] == cid:
            return l
    return None


def evaluar_respuesta_cli(pregunta, respuesta, lec=None):
    """Devuelve (acierto, confianza, razon, fuente). Por defecto usa EstrategiaLLM
    (MockLLMClient offline); si se activa TUTOR_LLM=http usa un modelo real y
    cae al matcher si la llamada falla."""
    res = estrategia().evaluar(pregunta, respuesta, lec)
    if len(res) == 4:
        return res
    # matcher devuelve 3-tuple
    acierto, conf, razon = res
    return acierto, conf, razon, "matcher"


_estrategia = None


def estrategia():
    global _estrategia
    if _estrategia is None:
        if getattr(estrategia, "_forzar", None) == "matcher":
            from modelo import MatcherClaves, EstrategiaEvaluacion
            class _M(EstrategiaEvaluacion):
                def evaluar(self, pregunta, respuesta, leccion=None):
                    return (*MatcherClaves().evaluar(pregunta, respuesta), "matcher")
            _estrategia = _M()
        elif getattr(estrategia, "_forzar", None) == "http":
            import os
            os.environ["TUTOR_LLM"] = "http"
            _estrategia = EstrategiaLLM()
        else:
            _estrategia = EstrategiaLLM()
    return _estrategia


def pedir(prompt):
    try:
        return input(prompt).strip()
    except EOFError:
        return ""


def confirmar(prompt):
    return pedir(prompt).lower() in ("s", "si", "sí", "y")


def mostrar_leccion(lec):
    print(f"\n{'=' * 62}")
    print(f"  {lec['id'].upper()} · {lec['titulo']}")
    print(f"  Objetivo: {lec['objetivo']}")
    print(f"{'=' * 62}")
    for t in lec["teoria"]:
        print(f"  • {t}")
    print(f"\n  PRÁCTICA: {lec['practica']}")


def preguntar(estado, lec, idx, primera_vez):
    p = lec["preguntas"][idx]
    print(f"\n  ❓ {p['q']}")
    r1 = pedir("  tu respuesta > ")
    acierto, conf, razon, fuente = evaluar_respuesta_cli(p, r1, lec)
    if not acierto:
        pista = estrategia().pista(lec, p, r1)
        print(f"  💡 pista ({fuente}): {pista}")
        r2 = pedir("  otra chance > ")
        if evaluar_respuesta_cli(p, r2, lec)[0]:
            registrar_respuesta(estado, lec["id"], idx, True, grado=1)
            print("  ✔ mejoró con la pista. Vuelve a repaso pronto.")
            return
        grado = 0
        print(f"  ✘ Por ahí no es. Respuesta: {p['a']}")
    else:
        grado = 3 if primera_vez and random.random() < 0.15 else 2
        print("  ✔ Correcto." if grado == 2 else "  ✔ Correcto, y fluido: intervalo largo.")
    registrar_respuesta(estado, lec["id"], idx, grado != 0, grado=grado)


def cmd_estado(estado, curso):
    if estado is None:
        print("\n  No hay alumno todavía. Arrancá con: tutor.py clase\n")
        return
    r = resumen_alumno(curso, estado)
    print(f"\n  🧠 Alumno: {estado['alumno']}")
    print(f"  📚 Lecciones: {r['lecciones']}")
    print(f"  🎯 Respuestas: {r['respuestas']}")
    print(f"  ⏰ Repasos vencidos: {r['vencidas']}")
    print(f"  ▶ Próxima lección sugerida: {r['proxima']}\n")
    print(f"  {'ID':<5} {'MAESTRÍA':>9}  LECCIÓN")
    for lec in curso["lecciones"]:
        c = estado["conceptos"].get(lec["id"])
        pct = int((c["bkt"] if c else 0) * 100)
        barra = "█" * (pct // 10) + "·" * (10 - pct // 10)
        marca = "🏆" if pct >= UMBRAL_MAESTRIA * 100 else ("🔒" if c is None or not c.get("visto") else "📖")
        print(f"  {lec['id']:<5} {barra} {pct:>3}%  {marca} {lec['titulo']}")
    print()


def cmd_clase(estado, curso, cid=None):
    if estado is None:
        estado = nuevo_estado()
    lec = leccion_por_id(curso, cid) if cid else leccion_siguiente(curso, estado)
    if lec is None:
        print("\n  Nada desbloqueado: primero repasá lo vencido (tutor.py sesion).\n")
        return
    mostrar_leccion(lec)
    marcar_vista(estado, lec["id"])
    guardar_estado(estado)
    print(f"\n  Marcada como vista ({lec['id']}). Ahora fijala con: tutor.py sesion\n")


def cmd_sesion(estado, curso, solo_repaso=False):
    if estado is None:
        print("\n  Primero abrí una lección: tutor.py clase\n")
        return
    vencidas = tarjetas_vencidas(curso, estado)
    cola = list(vencidas[:4])
    lec = leccion_siguiente(curso, estado) if not solo_repaso else None
    if lec and not solo_repaso:
        cola += [(lec["id"], i) for i in preguntas_de_leccion(curso, estado, lec, cantidad=3)]
    if not cola:
        print("\n  ✨ Nada vencido y sin lección nueva disponible. Volvé mañana o abrí otra clase.\n")
        return
    # mezclar solo las NUEVAS (después de las vencidas) para variar el orden
    fijas = cola[:4]
    nuevas = cola[4:]
    random.shuffle(nuevas)
    cola = fijas + nuevas
    print(f"\n  Sesión retrieval-first: {len(vencidas)} repasos vencidos"
          + (f" + nuevas de {lec['titulo']}" if lec else ""))
    for n, (cid, idx) in enumerate(cola, 1):
        l = leccion_por_id(curso, cid)
        nueva = clave_tarjeta(cid, idx) not in estado["tarjetas"]
        etiqueta = "NUEVA" if nueva else "REPASO"
        print(f"\n  [{n}/{len(cola)}] ({etiqueta} · {l['titulo']})")
        preguntar(estado, l, idx, nueva)
    guardar_estado(estado)
    cmd_estado(estado, curso)


def _evaluar_desde_cli(lec, pregunta):
    """Adaptador CLI para diagnosticar(): pide la respuesta por stdin."""
    print(f"\n  [diagnóstico] {lec['titulo']}")
    print(f"  ❓ {pregunta['q']}")
    r = pedir("  tu respuesta > ")
    acierto, conf, razon, fuente = evaluar_respuesta_cli(pregunta, r, lec)
    if not acierto:
        print(f"  (respuesta esperada: {pregunta['a']}) [vía {fuente}]")
    return {"acierto": acierto}


def cmd_diagnostico(estado, curso):
    if estado is None:
        estado = nuevo_estado("diagnostico")
    resultados = diagnosticar(curso, estado, _evaluar_desde_cli, rng=random)
    aciertos = sum(1 for *_, a in resultados if a)
    print(f"\n  🩺 Diagnóstico: {aciertos}/{len(resultados)} lecciones ya dominadas.")
    print("  Lecciones saltadas por placement:", aciertos)
    guardar_estado(estado)
    cmd_estado(estado, curso)


def cmd_demo(estado, curso, dias=5):
    print(f"\n  Simulando {dias} días de un alumno real...\n")
    if estado is None:
        estado = nuevo_estado("demo")
    random.seed(7)
    from modelo import _ahora, fsrs_lite_programar, tarjeta_nueva, bkt_actualizar
    for dia in range(dias):
        for lec in curso["lecciones"]:
            c = estado["conceptos"].setdefault(lec["id"], {"bkt": 0.15, "visto": False, "intentos": 0, "aciertos": 0})
            if c["bkt"] < UMBRAL_MAESTRIA and prereqs_cumplidos(curso, estado, lec):
                c["visto"] = True
                for i, _ in enumerate(lec["preguntas"]):
                    k = clave_tarjeta(lec["id"], i)
                    if k not in estado["tarjetas"]:
                        estado["tarjetas"][k] = tarjeta_nueva()
                break
        for k in list(estado["tarjetas"].keys()):
            t = estado["tarjetas"][k]
            if t["reps"] == 0 or t["due"] <= _ahora().isoformat():
                cid, idx = k.split("::")
                proba = estado["conceptos"][cid]["bkt"]
                correcto = random.random() < max(0.35, min(proba + 0.25, 0.95))
                grado = 2 if correcto else 0
                estado["conceptos"][cid]["intentos"] += 1
                estado["conceptos"][cid]["aciertos"] += 1 if correcto else 0
                estado["conceptos"][cid]["bkt"] = bkt_actualizar(estado["conceptos"][cid]["bkt"], correcto)
                fsrs_lite_programar(t, grado)
                estado["historia"].append({"t": f"dia{dia}", "tarjeta": k,
                                           "correcto": correcto, "grado": grado,
                                           "bkt": round(estado["conceptos"][cid]["bkt"], 3)})
        guardar_estado(estado)
    cmd_estado(estado, curso)
    print("  (estado demo guardado; usá 'reset' para volver a cero)\n")


def main():
    parser = argparse.ArgumentParser(description="Tutor IA F0 — motor pedagógico CLI")
    parser.add_argument("comando", choices=["estado", "clase", "sesion", "repaso", "diagnostico", "demo", "reset"],
                        help="qué hacer")
    parser.add_argument("--id", help="id de lección para 'clase' (ej: c03)")
    parser.add_argument("--curso", help="ruta al JSON del curso (default: curso_premiere.json)")
    parser.add_argument("--matcher", action="store_true",
                        help="fuerza evaluación por claves (sin capa LLM)")
    parser.add_argument("--http", action="store_true",
                        help="fuerza backend LLM HTTP (requiere TUTOR_LLM_* en env)")
    parser.add_argument("--dias", type=int, default=5, help="días a simular en 'demo'")
    args = parser.parse_args()

    if args.matcher:
        estrategia._forzar = "matcher"
    elif args.http:
        estrategia._forzar = "http"

    curso = cargar_curso(args.curso)
    # Estado file per-course to avoid mixing progress
    curso_nombre = curso.get("curso", "default").replace(" ", "_").replace("-", "_").lower()
    import modelo
    modelo.ESTADO_PATH = RAIZ / f"estado_{curso_nombre}.json"
    estado = None
    try:
        estado = cargar_estado()
    except RuntimeError as exc:
        print(f"⚠️  {exc}", file=sys.stderr)
        sys.exit(1)

    if args.comando == "estado":
        cmd_estado(estado, curso)
    elif args.comando == "clase":
        cmd_clase(estado, curso, args.id)
    elif args.comando in ("sesion", "repaso"):
        cmd_sesion(estado, curso, solo_repaso=(args.comando == "repaso"))
    elif args.comando == "diagnostico":
        cmd_diagnostico(estado, curso)
    elif args.comando == "demo":
        cmd_demo(estado, curso, args.dias)
    elif args.comando == "reset":
        if modelo.ESTADO_PATH.exists() and confirmar("¿Borrar TODO el progreso? (s/n) > "):
            modelo.ESTADO_PATH.unlink()
            print("  Estado eliminado.")
        else:
            print("  Cancelado.")


if __name__ == "__main__":
    main()
