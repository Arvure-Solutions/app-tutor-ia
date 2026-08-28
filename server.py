"""Server de la plataforma Tutor IA (F3 — portal multi-dominio).

Sirve la app pulida (app/) y expone una API JSON que maneja múltiples cursos:

  GET  /api/catalogo
  POST /api/generar        {tema, dominio?}           -> {slug, curso}
  GET  /api/curso/<slug>/estado
  POST /api/curso/<slug>/clase      {cid?}
  POST /api/curso/<slug>/sesion
  POST /api/curso/<slug>/responder  {cid, idx, texto}
  POST /api/curso/<slug>/segundo    {cid, idx, texto}
  POST /api/curso/<slug>/consultar  {cid?, texto}

Cada curso reutiliza el motor pedagógico (modelo/sesion) por igual.
Solo stdlib: http.server + ThreadingHTTPServer. $0, sin dependencias.
"""
from __future__ import annotations

import json
import sys
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "motor"))
import modelo
import sesion
import catalogo
import generador

RAIZ = Path(__file__).resolve().parent
APP = RAIZ / "app"
try:
    PORT = int(sys.argv[1])
except (IndexError, ValueError):
    PORT = int(os.environ.get("PORT", "8000"))


def cargar_estado(slug):
    modelo.ESTADO_PATH = catalogo.estado_path(slug)
    try:
        return modelo.cargar_estado()
    except RuntimeError:
        return None


def crear_si_falta(slug):
    e = cargar_estado(slug)
    if e is None:
        curso = catalogo.cargar_curso(slug)
        e = modelo.nuevo_estado(curso.get("curso", slug))
        modelo.guardar_estado(e)
    return e


def resumen(slug, curso, estado):
    lecciones = []
    for lec in curso["lecciones"]:
        c = estado["conceptos"].get(lec["id"])
        pct = int((c["bkt"] if c else 0) * 100)
        lecciones.append({
            "id": lec["id"], "titulo": lec["titulo"], "maestria": pct,
            "visto": bool(c and c.get("visto")),
            "dominada": pct >= int(modelo.UMBRAL_MAESTRIA * 100),
            "fuentes": lec.get("fuentes", []),
        })
    return {"alumno": estado["alumno"], "lecciones": lecciones,
            "resumen": modelo.resumen_alumno(curso, estado)}


class Handler(BaseHTTPRequestHandler):
    def _json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _archivo(self, ruta):
        if not ruta.exists():
            self._json({"error": "no encontrado"}, 404)
            return
        self.send_response(200)
        if ruta.suffix == ".html":
            ct = "text/html; charset=utf-8"
        elif ruta.suffix == ".js":
            ct = "text/javascript; charset=utf-8"
        elif ruta.suffix == ".css":
            ct = "text/css; charset=utf-8"
        else:
            ct = "application/octet-stream"
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(ruta.stat().st_size))
        self.end_headers()
        self.wfile.write(ruta.read_bytes())

    def do_GET(self):
        u = urlparse(self.path)
        if u.path in ("/", "/index.html"):
            self._archivo(APP / "portal.html")
            return
        if u.path == "/curso.html":
            self._archivo(APP / "curso.html")
            return
        if u.path == "/api/catalogo":
            self._json({"bienvenida": catalogo.cargar_catalogo().get("bienvenida", ""),
                        "dominios": catalogo.dominios()})
            return
        if u.path.startswith("/api/curso/") and u.path.endswith("/estado"):
            slug = u.path.split("/")[3]
            curso = catalogo.cargar_curso(slug)
            if not curso:
                self._json({"error": "curso inexistente"}, 404)
                return
            estado = crear_si_falta(slug)
            self._json(resumen(slug, curso, estado))
            return
        self._json({"error": "no encontrado"}, 404)

    def do_POST(self):
        u = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}") if length else {}
        partes = [p for p in u.path.split("/") if p]

        # /api/generar
        if u.path == "/api/generar":
            tema = body.get("tema", "").strip()
            if not tema:
                self._json({"error": "falta tema"}, 400)
                return
            curso = generador.generar(tema, body.get("dominio"))
            slug = catalogo.slug(tema)
            self._json({"slug": slug, "curso": curso})
            return

        # /api/curso/<slug>/...
        if len(partes) >= 4 and partes[0] == "api" and partes[1] == "curso":
            slug = partes[2]
            accion = partes[3]
            curso = catalogo.cargar_curso(slug)
            if not curso:
                self._json({"error": "curso inexistente"}, 404)
                return
            estado = crear_si_falta(slug)

            if accion == "clase":
                lec, estado = sesion.abrir_clase(curso, estado, body.get("cid"))
                self._json({"leccion": lec})
            elif accion == "sesion":
                cola, lec = sesion.armar_cola(curso, estado)
                out = [{"cid": c, "idx": i,
                        "etiqueta": ("NUEVA" if modelo.clave_tarjeta(c, i)
                                     not in estado["tarjetas"] else "REPASO"),
                        "titulo": modelo.leccion_por_id(curso, c)["titulo"],
                        "q": modelo.leccion_por_id(curso, c)["preguntas"][i]["q"]}
                       for c, i in cola]
                self._json({"cola": out})
            elif accion == "responder":
                r = sesion.responder(curso, estado, body["cid"], body["idx"],
                                     body.get("texto", ""))
                self._json(r)
            elif accion == "segundo":
                r = sesion.segundo_intento(curso, estado, body["cid"], body["idx"],
                                           body.get("texto", ""))
                self._json(r)
            elif accion == "consultar":
                cid = body.get("cid") or (estado and next(
                    (cid for cid, c in estado["conceptos"].items()
                     if c.get("visto")), None))
                r = sesion.consultar(curso, estado, cid, body.get("texto", ""))
                self._json(r)
            else:
                self._json({"error": "no encontrado"}, 404)
            return

        self._json({"error": "no encontrado"}, 404)

    def log_message(self, *a):
        pass


def main():
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"🌐 Plataforma Tutor IA en http://localhost:{PORT}  (Ctrl+C para salir)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
