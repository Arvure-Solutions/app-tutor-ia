#!/usr/bin/env python3
"""UI web mínima del Tutor IA (F2) — solo stdlib, corre local, $0.

Monta el motor F1 detrás de una interfaz HTML. No instala nada.
Sirve un dashboard: estado de maestría, lección abierta, sesión retrieval-first
y check-in de voz (loop) opcional.

Arranque:
    python3 web.py [puerto]

Luego abrí http://localhost:8000
La API (JSON) vive en /api/*.
"""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, str(Path(__file__).resolve().parent))
import modelo
import sesion

RAIZ = Path(__file__).resolve().parent
CURSO = json.loads((RAIZ / "curso_premiere.json").read_text(encoding="utf-8"))


def _curso_nombre():
    return CURSO.get("curso", "default").replace(" ", "_").replace("-", "_").lower()


def cargar_o_crear_estado():
    modelo.ESTADO_PATH = RAIZ / f"estado_{_curso_nombre()}.json"
    try:
        return modelo.cargar_estado()
    except RuntimeError:
        return None


def estado_resumen(estado):
    if estado is None:
        return {"alumno": None, "lecciones": [], "resumen": None}
    lecciones = []
    for lec in CURSO["lecciones"]:
        c = estado["conceptos"].get(lec["id"])
        pct = int((c["bkt"] if c else 0) * 100)
        lecciones.append({
            "id": lec["id"], "titulo": lec["titulo"],
            "maestria": pct,
            "visto": bool(c and c.get("visto")),
            "dominada": pct >= int(modelo.UMBRAL_MAESTRIA * 100),
        })
    return {"alumno": estado["alumno"],
            "lecciones": lecciones,
            "resumen": modelo.resumen_alumno(CURSO, estado)}


HTML = """<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tutor IA</title>
<style>
 body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:760px;margin:2rem auto;padding:0 1rem;background:#0f1115;color:#e7e9ee}
 h1{font-size:1.4rem} h2{font-size:1.1rem;margin-top:1.6rem;border-bottom:1px solid #222;padding-bottom:.3rem}
 .bar{background:#1c2230;height:10px;border-radius:6px;overflow:hidden;margin:2px 0 6px}
 .bar>i{display:block;height:100%;background:linear-gradient(90deg,#4f8cff,#7c5cff)}
 .row{display:flex;justify-content:space-between;align-items:center;padding:4px 0}
 .m{font-variant-numeric:tabular-nums;color:#9aa4b2}
 .ok{color:#5fd38a}.lock{color:#6b7280}.book{color:#4f8cff}
 button{cursor:pointer;border:0;border-radius:8px;padding:.6rem 1rem;background:#4f8cff;color:#fff;font-weight:600;margin:.3rem .3rem .3rem 0}
 button.sec{background:#222a3a}
 .q{background:#161b27;border:1px solid #222a3a;border-radius:10px;padding:1rem;margin:.6rem 0}
 input[type=text]{width:100%;padding:.6rem;border-radius:8px;border:1px solid #2a3346;background:#0f1115;color:#e7e9ee}
 .msg{margin-top:.5rem;font-size:.95rem}
 .pill{display:inline-block;font-size:.7rem;padding:2px 8px;border-radius:999px;background:#222a3a;color:#9aa4b2;margin-left:.4rem}
 pre{background:#161b27;padding:.8rem;border-radius:8px;overflow:auto}
</style></head>
<body>
<h1>🧠 Tutor IA <span class="m" id="alum"></span></h1>

<h2>Maestría por lección</h2>
<div id="maestria"></div>

<h2>Sesión de hoy</h2>
<div id="acciones">
  <button onclick="abrirClase()">▶ Abrir próxima lección</button>
  <button onclick="iniciarSesion()">🔁 Sesión retrieval-first</button>
  <button class="sec" onclick="loopDiario()">🌅 Loop diario + voz</button>
  <button class="sec" onclick="reset()">🗑 Reset</button>
</div>
<div id="leccion"></div>
<div id="sesion"></div>
<div id="reporte"></div>

<script>
const api = async (p, body) => {
  const r = await fetch('/api/'+p, {method: body? 'POST':'GET',
    headers:{'Content-Type':'application/json'}, body: body? JSON.stringify(body):null});
  return r.json();
};
async function cargar(){
  const e = await api('estado');
  document.getElementById('alum').textContent = e.alumno? '· '+e.alumno:'';
  const m = document.getElementById('maestria'); m.innerHTML='';
  (e.lecciones||[]).forEach(l=>{
    const cls = l.dominada? 'ok':'';
    const mk = l.dominada? '🏆':(l.visto? '📖':'🔒');
    m.innerHTML += `<div class="row"><span>${mk} ${l.id} · ${l.titulo}</span>
      <span class="m">${l.maestria}%</span></div>
      <div class="bar"><i style="width:${l.maestria}%"></i></div>`;
  });
}
async function abrirClase(){
  const r = await api('clase', {});
  const d = document.getElementById('leccion');
  if(!r.leccion){ d.innerHTML='<p class="msg">Nada desbloqueado: repasá lo vencido.</p>'; return; }
  const L=r.leccion;
  d.innerHTML = `<div class="q"><b>${L.id} · ${L.titulo}</b><br>
    <span class="m">Objetivo:</span> ${L.objetivo}<ul>${L.teoria.map(t=>`<li>${t}</li>`).join('')}</ul>
    <span class="m">Práctica:</span> ${L.practica}</div>`;
}
async function iniciarSesion(){
  const r = await api('sesion', {});
  const s = document.getElementById('sesion'); s.innerHTML='';
  if(!r.cola || !r.cola.length){ s.innerHTML='<p class="msg">Nada vencido y sin lección nueva. ✨</p>'; return; }
  r.cola.forEach(item=>{
    const div=document.createElement('div'); div.className='q';
    div.innerHTML=`<b>${item.etiqueta} · ${item.titulo}</b><div class="m">${item.q}</div>
      <input type="text" id="r_${item.cid}_${item.idx}" placeholder="tu respuesta...">
      <button onclick="responder('${item.cid}',${item.idx})">Responder</button>
      <div class="msg" id="m_${item.cid}_${item.idx}"></div>`;
    s.appendChild(div);
  });
}
async function responder(cid, idx){
  const txt = document.getElementById(`r_${cid}_${idx}`).value;
  const r = await api('responder', {cid, idx, texto:txt});
  const m = document.getElementById(`m_${cid}_${idx}`);
  m.innerHTML = (r.acierto? '✔ <span class="ok">Correcto.</span>'
      : `💡 ${r.mensaje} <span class="pill">${r.fuente}</span><br>${r.pista||''}`);
  if(!r.acierto){
    m.innerHTML += `<br><input type="text" id="r2_${cid}_${idx}" placeholder="otra chance...">
      <button onclick="segundo('${cid}',${idx})">Reintentar</button>`;
  }
  await cargar();
}
async function segundo(cid, idx){
  const txt = document.getElementById(`r2_${cid}_${idx}`).value;
  const r = await api('segundo', {cid, idx, texto:txt});
  document.getElementById(`m_${cid}_${idx}`).innerHTML =
    (r.acierto? '✔ <span class="ok">Mejoró con la pista.</span>'
             : `✘ Respuesta: ${r.mensaje.replace('Por ahí no es. Respuesta: ','')}`);
  await cargar();
}
async function loopDiario(){
  const r = await api('loop', {hablar:true});
  document.getElementById('reporte').innerHTML =
    '<pre>'+ (r.reporte||'') +'</pre>';
  await cargar();
}
async function reset(){
  if(confirm('¿Borrar TODO el progreso?')){ await api('reset',{}); await cargar(); }
}
cargar();
</script>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def _json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _html(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML.encode("utf-8"))

    def do_GET(self):
        u = urlparse(self.path)
        if u.path in ("/", "/index.html"):
            self._html()
            return
        if u.path == "/api/estado":
            self._json(estado_resumen(cargar_o_crear_estado()))
            return
        self._json({"error": "no encontrado"}, 404)

    def do_POST(self):
        u = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}") if length else {}
        estado = cargar_o_crear_estado()

        if u.path == "/api/clase":
            lec, estado = sesion.abrir_clase(CURSO, estado)
            self._json({"leccion": lec})

        elif u.path == "/api/sesion":
            if estado is None:
                self._json({"cola": [], "error": "sin alumno"})
                return
            cola, lec = sesion.armar_cola(CURSO, estado)
            out = [{"cid": c, "idx": i, "etiqueta":
                    ("NUEVA" if modelo.clave_tarjeta(c, i) not in estado["tarjetas"] else "REPASO"),
                    "titulo": modelo.leccion_por_id(CURSO, c)["titulo"],
                    "q": modelo.leccion_por_id(CURSO, c)["preguntas"][i]["q"]}
                   for c, i in cola]
            self._json({"cola": out})

        elif u.path == "/api/responder":
            r = sesion.responder(CURSO, estado, body["cid"], body["idx"], body.get("texto", ""))
            self._json(r)

        elif u.path == "/api/segundo":
            r = sesion.segundo_intento(CURSO, estado, body["cid"], body["idx"], body.get("texto", ""))
            self._json(r)

        elif u.path == "/api/loop":
            out = sesion.loop_diario(CURSO, estado, hablar=bool(body.get("hablar")))
            reporte = next((c for n, c in out["pasos"] if n == "reporte"), "")
            self._json({"reporte": reporte})

        elif u.path == "/api/reset":
            modelo.ESTADO_PATH = RAIZ / f"estado_{_curso_nombre()}.json"
            if modelo.ESTADO_PATH.exists():
                modelo.ESTADO_PATH.unlink()
            self._json({"ok": True})

        else:
            self._json({"error": "no encontrado"}, 404)

    def log_message(self, *a):
        pass  # silencioso


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"🌐 Tutor IA en http://localhost:{port}  (Ctrl+C para salir)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()


if __name__ == "__main__":
    main()
