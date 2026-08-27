#!/usr/bin/env python3
"""
Empaquetador: cursos en Markdown → curso_premiere.json compatible con el motor.
Uso: python3 empaquetar.py curso.md [curso.json]
"""
import json
import re
import sys
import unicodedata
from pathlib import Path


def _limpiar_md(s):
    return re.sub(r"\*\*([^*]+)\*\*", r"\1", s).strip()


def _sin_tilde(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").lower()


def parsear_md(ruta):
    texto = Path(ruta).read_text(encoding="utf-8")
    lecciones = []
    actual = None
    bloque = None

    for linea in texto.splitlines():
        stripped = _limpiar_md(linea.strip())
        sl = _sin_tilde(stripped)

        if stripped.startswith("## "):
            if actual:
                lecciones.append(actual)
            cid = stripped[3:].strip()
            actual = {"id": cid, "titulo": "", "objetivo": "", "prereqs": [],
                       "teoria": [], "practica": "", "preguntas": []}
            bloque = None
        elif actual is None:
            continue
        elif sl.startswith("objetivo:"):
            actual["objetivo"] = stripped.split(":", 1)[1].strip()
        elif sl.startswith("prerequisitos:"):
            raw = stripped.split(":", 1)[1].strip()
            actual["prereqs"] = [p.strip() for p in re.split(r"[,;]", raw) if p.strip()]
        elif sl.startswith("titulo:"):
            actual["titulo"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("- ") and sl.lstrip("- ").startswith("teoria"):
            bloque = "teoria"
        elif stripped.startswith("- ") and sl.lstrip("- ").startswith("practica"):
            bloque = "practica"
        elif stripped.startswith("- ") and sl.lstrip("- ").startswith("preguntas"):
            bloque = "preguntas"
        elif stripped.startswith("- ") and bloque == "teoria":
            actual["teoria"].append(stripped[2:].strip())
        elif stripped.startswith("- ") and bloque == "preguntas":
            _agregar_pregunta(actual, stripped[2:].strip())
        elif stripped and bloque == "practica" and not stripped.startswith("**"):
            if actual["practica"]:
                actual["practica"] += " "
            actual["practica"] += stripped
        elif stripped.startswith("**") and stripped.endswith("**") and not bloque:
            actual["titulo"] = stripped.strip("*").strip()

    if actual:
        lecciones.append(actual)

    return lecciones


def _agregar_pregunta(lec, linea):
    partes = linea.split("|")
    if len(partes) < 2:
        return
    q = partes[0].strip()
    a = partes[1].strip() if len(partes) > 1 else ""
    claves = [c.strip() for c in partes[2].split(",")] if len(partes) > 2 else [a.split()[0]]
    pistas = [p.strip() for p in partes[3].split(",")] if len(partes) > 3 else []
    lec["preguntas"].append({"q": q, "a": a, "claves": claves, "pistas": pistas})


def validar(curso):
    ids = {l["id"] for l in curso["lecciones"]}
    errores = []
    for lec in curso["lecciones"]:
        if not lec["titulo"]:
            errores.append(f"  {lec['id']}: falta título (usá **Título:** en el md)")
        if not lec["preguntas"]:
            errores.append(f"  {lec['id']}: sin preguntas de refuerzo")
        for p in lec["prereqs"]:
            if p not in ids:
                errores.append(f"  {lec['id']}: prerrequisito '{p}' no existe")
    return errores


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 empaquetar.py curso.md [salida.json]")
        sys.exit(1)

    md_path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else md_path.replace(".md", ".json")

    lecciones = parsear_md(md_path)
    curso = {"curso": Path(md_path).stem.replace("_", " ").replace("-", " "),
             "nivel": "personalizado", "lecciones": lecciones}

    errores = validar(curso)
    if errores:
        print("\n⚠ Errores de estructura:")
        for e in errores:
            print(e)
        print("\nGenerando de todas formas (revisá el JSON)...\n")

    Path(out_path).write_text(json.dumps(curso, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ {len(lecciones)} lecciones → {out_path}")
    if errores:
        print(f"   ({len(errores)} warnings — revisá antes de usar con tutor.py)")


if __name__ == "__main__":
    main()
