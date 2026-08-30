---
tipo: nodo-proyecto
proyecto: "APP Tutor IA"
actualizado: 2026-08-25
---

# 🧩 APP Tutor IA — Nodo del proyecto

> [!info] Nodo central que conecta todas las notas y adjuntos del proyecto.
> Volver al mapa general: [[00 CEREBRO|🧠 Cerebro]]

## Qué es
Tutor IA con seguimiento continuo: loop diario proactivo (briefing → sesión → check-in voz → repaso FSRS → reporte), popups de tarea sin culpa, micrófono, observación de pantalla opt-in con corrección "por ahí no es", y cursos empaquetados estilo Frappe Learning. El corazón del proyecto es el **modelo de razonamiento pedagógico** (memoria + BKT + FSRS + socrático).

## 📝 Documento central
| Nota | Contenido |
|---|---|
| [[APP Tutor IA/docs/propuesta\|docs/propuesta]] | ⭐ PROPUESTA COMPLETA: problema validado, los 7 módulos del motor pedagógico, arquitectura, roadmap F0-F4, riesgos |
| [[APP Tutor IA/docs/f0-motor\|docs/f0-motor]] | ✅ F0 FUNCIONAL: motor pedagógico CLI (BKT + FSRS-lite + gates) con curso piloto de Premiere Pro — código en `motor/` |

## 📝 Investigación (barrido 2026-08-25, 4 subagentes)
| Nota | Resumen |
|---|---|
| [[APP Tutor IA/docs/investigacion/github-repos\|github-repos]] | ~16 repos open-source analizados. Top: pacer-ai (loop diario), mind-mentor (Mem0+SM-2), onevision (pantalla en vivo). Nadie integra los 5 pilares → hueco confirmado |
| [[APP Tutor IA/docs/investigacion/comunidad-usuarios\|comunidad-usuarios]] | Voz real Reddit/X: dolor #1 herramientas amnésicas; voz > push; streak-guilt mata; screen-awareness solo opt-in+local+visible. Citas textuales con enlaces |
| [[APP Tutor IA/docs/investigacion/youtube-videos\|youtube-videos]] | 6 videos con transcripciones: NotebookLM admite su hueco de seguimiento; crítica UX de Charlie Gedeon (UI clicable, no chatbot); Sana 3-agentes; Khanmigo accountability |
| [[APP Tutor IA/docs/investigacion/plataformas-pedagogia\|plataformas-pedagogia]] | Frappe Learning como referencia de curriculum; 10 conceptos pedagógicos traducidos a features (Bloom 2σ, retrieval-first, FSRS vs SM-2, ZPD, hint ladder N0-N3, BKT, interleaving, hábitos) |

## 📁 Archivos del motor
| Archivo | Qué hace |
|---|---|
| [[APP Tutor IA/motor/modelo\|motor/modelo.py]] | 🧠 Cerebro: BKT + FSRS-lite + estado + evaluación (sin deps) |
| [[APP Tutor IA/motor/tutor\|motor/tutor.py]] | 🖥️ CLI: clase, sesión, repaso, demo, loop, reset |
| [[APP Tutor IA/motor/empaquetar\|motor/empaquetar.py]] | 📦 Empaquetador: Markdown → JSON de curso |
| [[APP Tutor IA/cursos/curso_premiere\|cursos/curso_premiere.json]] | 🎬 Curso piloto: Premiere Pro 11 lecciones |
| [[APP Tutor IA/cursos/biodescodificacion\|cursos/biodescodificacion.json]] | 🧪 Curso de prueba: biodescodificación 6 lecciones |

## 🔗 Conexiones
- Mapa general: [[00 CEREBRO]]
