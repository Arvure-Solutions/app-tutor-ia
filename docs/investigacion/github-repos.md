# Investigación: repos open-source de "tutores IA con seguimiento continuo"

**Fecha:** 2026-08-25
**Objetivo:** barrer GitHub buscando proyectos de tutores IA con seguimiento continuo del estudiante (check-ins diarios, memoria persistente, voz/pantalla, motor pedagógico adaptativo) para inspirar el diseño de nuestra app-tutor.

---

## Metodología

- **9+ rondas de búsqueda** con `gh search repos` (keywords: "AI tutor", "llm tutor", "tutoring agent", "learning companion", "spaced repetition", "knowledge tracing", "socratic tutor", "adaptive learning", "AI teacher", "voice tutor", "study tracker", "homework reminder"; topics: `education`, `lms`, `spaced-repetition`, `tutoring`).
- **Búsqueda semántica web** (exa) para casos que las keywords no capturan: agentes proactivos, tutores que miran la pantalla, compañeros de estudio con memoria longitudinal.
- **Lectura de READMEs completos + estructura de árbol** (`gh api repos/O/R/git/trees`) para los ~16 repos más prometedores.
- **Verificación de metadatos** (licencia, último push, lenguaje) en cada candidato final.
- Casos obligatorios examinados: `frappe/lms`, clones de NotebookLM (SurfSense, PageLM), memoria persistente aplicada a educación (Mem0/Letta), tutores por voz, combos calendario/recordatorios + estudio.

---

## Tabla comparativa

| Repo | Stars | Último commit | Licencia | Qué hace | Relevancia |
|---|---|---|---|---|---|
| [flysheep-ai/pacer-ai](https://github.com/flysheep-ai/pacer-ai) | 2 | 2026-05-21 | Apache-2.0 | Compañero IA multi-agente con loop diario completo (briefing → check-ins → reporte nocturno), memoria persistente por alumno y scheduler APScheduler | ⭐⭐⭐⭐⭐ |
| [KartikLabhshetwar/mind-mentor](https://github.com/KartikLabhshetwar/mind-mentor) | 143 | 2026-05-18 | Apache-2.0 | Tutor multi-agente (Tutor/Analyst/Scheduler) con Mem0, SM-2, recordatorios por email y analytics de estudio | ⭐⭐⭐⭐⭐ |
| [Arjunhg/onevision](https://github.com/Arjunhg/onevision) | 0 | 2026-03-01 | Sin licencia | Tutor multimodal en tiempo real que ve cámara O pantalla compartida, escucha voz y corrige hablando ("por ahí no es" en vivo) | ⭐⭐⭐⭐⭐ |
| [plastic-labs/tutor-gpt](https://github.com/plastic-labs/tutor-gpt) | 923 | 2026-02-20 | GPL-3.0 | Tutor con razonamiento Theory-of-Mind; actualiza sus propios prompts y modela al usuario vía Honcho | ⭐⭐⭐⭐ |
| [nagisanzenin/engram](https://github.com/nagisanzenin/engram) | 1.373 | 2026-08-18 | MIT | Motor de aprendizaje para agentes: tutor Socrático + examinador ciego + scheduler FSRS-4.5 con estado local JSON | ⭐⭐⭐⭐ |
| [open-spaced-repetition/py-fsrs](https://github.com/open-spaced-repetition/py-fsrs) (+ fsrs4anki, 4k★) | 474 | 2026-08-09 | MIT | Librería del algoritmo FSRS (sucesor moderno de SM-2); base lista para nuestro planificador de repasos | ⭐⭐⭐⭐ |
| [Li-Evan/Bloom](https://github.com/Li-Evan/Bloom) | 240 | 2026-06-23 | MIT | Tutor privado basado en 2-Sigma de Bloom: sílabo → lección → anotación → feedback → siguiente lección adaptada | ⭐⭐⭐⭐ |
| [frappe/lms](https://github.com/frappe/lms) "Frappe Learning" | 3.164 | 2026-08-25 (activo diario) | AGPL-3.0 | LMS self-hosted simple: cursos→capítulos→lecciones, batches, quizzes, certificados | ⭐⭐⭐ |
| [MudassarAbrar/SAGE__GEMINI_LIVE_AGENT_HACKATHON](https://github.com/MudassarAbrar/SAGE__GEMINI_LIVE_AGENT_HACKATHON) | 3 | 2026-03-01 | Sin licencia | Agente Gemini Live con voz + visión + control de UI que detecta cuándo el alumno está atascado/frustrado e interviene | ⭐⭐⭐⭐ |
| [HugeCatLab/ChatTutor](https://github.com/HugeCatLab/ChatTutor) | 1.308 | 2026-01-09 | AGPL-3.0 | Tutor visual interactivo con pizarra electrónica que la IA sabe usar (canvas matemático, mindmaps, animación física) | ⭐⭐⭐ |
| [andymatuschak/orbit](https://github.com/andymatuschak/orbit) | 1.828 | 2024-10-14 (inactivo) | AGPL/BUSL mixta | Plataforma de repetición espaciada embebida en textos ("mnemonic medium") con sync multiplataforma y notificaciones | ⭐⭐⭐ |
| [echo-loop/Echo-Loop](https://github.com/echo-loop/Echo-Loop) | 3.226 | 2026-08-23 | AGPL-3.0 | App de entrenamiento auditivo-oral en inglés con pipeline pedagógico rígido y repaso espaciado automático con recordatorios | ⭐⭐⭐ |
| [MODSetter/SurfSense](https://github.com/MODSetter/SurfSense) | 16.007 | 2026-08-25 | Community License | Alternativa open-source a NotebookLM orientada a investigación agéntica con KB con citas | ⭐⭐⭐ |
| [CaviraOSS/PageLM](https://github.com/CaviraOSS/PageLM) | 1.884 | 2026-08-19 | PageLM Community | NotebookLM educativo: PDFs → quizzes, flashcards, notas, podcasts | ⭐⭐⭐ |
| [JushBJJ/Mr.-Ranedeer-AI-Tutor](https://github.com/JushBJJ/Mr.-Ranedeer-AI-Tutor) | 29.600 | 2025-09-30 (**DISCONTINUED**) | — (prompt puro) | El prompt-tutor más famoso de GPT-4; personalización por profundidad/tono/estilo. Referencia histórica | ⭐⭐ |
| [X-RayLuan/Openclaw-Study-Coach](https://github.com/X-RayLuan/Openclaw-Study-Coach) | 8 | 2026-06-02 | MIT | Skill-pack markdown K-12 con memoria longitudinal, repetición espaciada y Parent Playbook (actividades diarias de 3 min) | ⭐⭐⭐ |

Menciones de apoyo (componentes, no apps): [pykt-team/pykt-toolkit](https://github.com/pykt-team/pykt-toolkit) (430★, benchmark de knowledge tracing DL), [CAHLR/pyBKT](https://github.com/CAHLR/pyBKT) (275★, Bayesian Knowledge Tracing), [riiid/ednet](https://github.com/riiid/ednet) (dataset de Santa, tutor IA con 780K usuarios), [thunlp/ProactiveAgent](https://github.com/thunlp/ProactiveAgent) (653★, agentes que anticipan tareas).

---

## Deep dive

### 1. flysheep-ai/pacer-ai — el patrón exacto que queremos construir
URL: https://github.com/flysheep-ai/pacer-ai · Python/FastAPI + Vue 3 · Apache-2.0 · nuevo pero con 81 tests backend + 66 frontend

Es el repo más cercano a la visión completa: un compañero IA para estudiantes de Gaokao donde **tres agentes (profesor tutor, profesor de materia, compañero emocional) comparten UNA conversación continua** con memoria persistente construida durante meses.

Hallazgos de arquitectura aprovechables:
- **Loop diario programado**: briefing 07:00 → Q&A todo el día → revisión de errores 18:00 → informe diario 21:30 → buenas noches 22:30. Implementado con **APScheduler en proceso separado** (`src/pacer/scheduler/{jobs,runner}.py`).
- **Plan con checkboxes matutino**: la tasa real de completion alimenta el informe nocturno — exactamente el popup "¿hiciste la tarea?".
- **Memoria persistente**: embeddings 384-dim (all-MiniLM-L6-v2, numpy puro), deduplicación por similitud coseno, extracción automática de hechos de cada conversación + resumidor cada N turnos (`src/pacer/memory/{persistent,summarizer}.py`).
- **Cuaderno de errores ("error book")**: cada fallo se registra; un botón relanza un chat donde el profesor re-explica, genera variante del problema y califica el intento → refuerzo según lo que responde.
- **Mastery tracking por punto de conocimiento** (~200 knowledge points sembrados) con detección de puntos débiles y chat de repaso con un clic.
- **Red de seguridad emocional**: escáner de palabras clave + triage LLM que deriva a líneas de crisis ANTES de que el agente principal procese el texto.
- Router (Haiku) elige agente por turno; streaming SSE vía EventBus.

### 2. KartikLabhshetwar/mind-mentor — el trío Tutor/Analyst/Scheduler
URL: https://github.com/KartikLabhshetwar/mind-mentor · Next.js 14 + Cloudflare Workers + Express · Apache-2.0

Separación de responsabilidades muy limpia, directamente portable:
- **Agente Tutor**: chat con memoria Mem0, streaming SSE, extrae tópicos después de cada intercambio (para alimentar el motor de repaso).
- **Agente Analyst**: corre **SM-2**, construye grafo de conocimiento, detecta patrones de estudio, genera recomendaciones; dashboards de radar de dominio, heatmap de estudio, velocidad, puntos débiles.
- **Agente Scheduler**: cron horario que envía recordatorios diarios, avisos de racha perdida, alertas de repaso espaciado vencido, digests semanales e hitos por email (Resend). Es el "¿cómo vas?" automatizado.
- Extras reutilizables: Pomodoro con tracking de sesiones/rachas, planes de estudio generados con hitos semanales, quiz generation.

### 3. Arjunhg/onevision — mirar la pantalla y corregir en vivo
URL: https://github.com/Arjunhg/onevision · Python + React + Stream Video SDK · sin licencia (pedir permiso o re-implementar patrón)

Implementa literalmente el escenario "está haciendo la tarea en su PC, yo veo la pantalla y digo 'por ahí no es'":
- **ScreenShareProcessor**: captura frames a FPS configurable, detecta cambios visuales significativos y solo envía al VLM cuando hay novedad (IDE errors, esquemas, UI).
- **Modo auto**: cambia entre cámara (YOLO pose) y screen-share según lo publicado en la llamada.
- **Proactive feedback loop con back-off exponencial**: el agente calla cuando no pasa nada y solo habla si detecta error real o se le pregunta — evita narración incesante.
- **Echo guard**: fuzzy matching (SequenceMatcher) entre transcript STT entrante y TTS reciente para suprimir auto-feedback del propio agente.
- Stack: Deepgram STT/TTS, VLM para razonar sobre frames, prioridad de track screen-share > cámara.

### 4. plastic-labs/tutor-gpt — pedagogía Theory-of-Mind + modelado del usuario
URL: https://github.com/plastic-labs/tutor-gpt · Next.js + Supabase · GPL-3.0 · paper arXiv:2310.06983

- El tutor **razona sobre el estado mental del estudiante y reescribe sus propios prompts** para servir mejor; el producto hosteado se llama Bloom (guiño al problema 2-Sigma).
- Personalización delegada a **Honcho** (identity modeling / representaciones robustas del usuario) — alternativa a Mem0 como capa de memoria de perfil.
- No tiene scheduler ni continuidad día-a-día nativa (vía Discord/web chat), pero es la mejor referencia de *calidad pedagógica conversacional*.

### 5. nagisanzenin/engram — motor de aprendizaje con FSRS dentro de agentes
URL: https://github.com/nagisanzenin/engram · Python stdlib only · MIT · 315/315 selftests · muy activo

- Tesis clara: "tu IA puede explicar cualquier cosa; Engram garantiza que tú aún lo sepas el mes que viene". Convierte cualquier agente en **tutor (te hace producir la respuesta antes de explicar) + examinador ciego (califica en escrito, sin dejarse convencer) + scheduler FSRS-4.5**.
- Estado local en JSON plano (`~/.claude/learning/`), 100% offline, compartido entre plataformas (Claude Code, Codex, OpenCode, OpenClaw…).
- **Nudge de sesión**: aviso silencioso al abrir sesión cuando hay repasos vencidos (y silencio total si no los hay) — patrón perfecto para nuestros popups no intrusivos.
- Verificación de recuerdo libre "con recibos": cada repaso queda registrado y auditable; anti-inflación de notas (0/258 juicios inflados).

### 6. open-spaced-repetition/py-fsrs — el planificador listo para usar
URL: https://github.com/open-spaced-repetition/py-fsrs · MIT · familia FSRS (py/ts/rust/go)

- Implementación oficial del algoritmo **FSRS (Free Spaced Repetition Scheduler)**, modelo DSR (Difficulty-Stability-Retrievability): predice la probabilidad de recuerdo y agenda cada concepto "justo antes de que se te olvide".
- Sucesor moderno de SM-2 (Anki ya lo usa vía fsrs4anki, 4.053★). Incluye optimizador de parámetros por usuario.
- Decisión técnica recomendada para nuestra app: **FSRS como motor de repetición espaciada en lugar de SM-2** (mind-mentor usa SM-2; engram ya migró a FSRS-4.5).

### 7. Li-Evan/Bloom — curriculum adaptativo con ciclo de feedback
URL: https://github.com/Li-Evan/Bloom · FastAPI + React 19 + skill Claude Code · MIT

- Flujo canónico 2-Sigma: **sílabo generado → lección uno a uno → el alumno anota/comenta → la IA lee esas anotaciones y adapta la SIGUIENTE lección al nivel real de comprensión → evaluación → resumen**.
- Doble modo (CLI skill / web app) demuestra cómo empaquetar un tutor como skill de agente y como app completa.
- La lectura de anotaciones como señal de adaptación es un mecanismo barato y potente de personalización continua.

### 8. frappe/lms (Frappe Learning) — el LMS de referencia del usuario
URL: https://github.com/frappe/lms · Frappe Framework (Python) + Vue (frappe-ui) · AGPL-3.0 · commit diario

- Estructura de contenido: **curso → capítulos → lecciones** (jerarquía de 3 niveles que da contexto a cada lección) + **batches** (cohortes con cursos y duración) + live classes Zoom + quizzes (single/multi/open-ended) + assignments (PDF/docs) + certificados.
- Lo que NO tiene (y es nuestro diferencial): nada de tutor IA, ni check-ins proactivos, ni memoria del alumno, ni repetición espaciada. Es contenedor de contenido empaquetado — útil como referencia de modelo de datos de cursos y de UI tipo sidebar (menú lateral derecho con clases).
- Lección de diseño: simplicidad radical frente a Moodle (formularios cortos, UI clara).

### 9. MudassarAbrar/SAGE — intervención emocionalmente inteligente
URL: https://github.com/MudassarAbrar/SAGE__GEMINI_LIVE_AGENT_HACKATHON · Python (Gemini Live API) · sin licencia

- Agente en tiempo real con **voz + visión + control de UI** cuyo valor central es detectar **cuándo el alumno está atascado o frustrado e intervenir en el momento justo** — "como un tutor humano sentado a tu lado".
- Es el complemento conductual de onevision: onevision aporta el plumbing técnico de pantalla; SAGE aporta la política de intervención (cuándo hablar).

### 10. HugeCatLab/ChatTutor — tutor con pizarra electrónica
URL: https://github.com/HugeCatLab/ChatTutor · Vue + Node · AGPL-3.0

- La IA **opera herramientas de aula**: canvas matemático, mapas mentales, simulaciones físicas animadas. Para STEM el texto solo alcanza poco.
- Patrón aprovechable: acciones estructuradas del LLM sobre un lienzo (en vez de solo texto), similar a lo que necesitaremos cuando el tutor dibuje/explicite pasos.

### Referencias rápidas restantes
- **orbit** (andymatuschak): "mnemonic medium" — repasos embebidos dentro de textos; mono-repo TS con backend/notifier/sync; inactivo desde 2024, licencias mixtas AGPL+BUSL según paquete. Inspiración conceptual para integrar repaso dentro del material, no aparte.
- **Echo-Loop**: pipeline pedagógico fijo (盲听→精听→跟读→复述→复习 = blind listen → intensive → shadowing → retell → review) con agenda automática de repasos y recordatorios; Flutter multiplataforma, publicada en App Store/Play. Demuestra el valor de un método rígido guiado vs. chat libre.
- **SurfSense / PageLM**: cubren la parte NotebookLM (KB con citas, PDF→quiz/flashcards/podcast) pero **sin continuidad** — confirman el hueco de mercado que mencionó el usuario.
- **Openclaw-Study-Coach**: skill markdown K-12 con memoria longitudinal, repetición espaciada y **Parent Playbook** (actividades concretas de 3 min/día para padres) — idea de producto para involucrar a la familia.
- **Mr.-Ranedeer** (29.6k★): discontinuado; prueba que el interés existe masivamente pero un prompt sin estado/scheduler no retiene aprendizaje.
- **EdNet (Riiid Santa)**: dataset industrial de interacciones alumno-sistema (780K usuarios); valida knowledge tracing a escala. pyBKT/pyKT ofrecen implementaciones listas de BKT/DKT si algún día queremos dominio por concepto más fino que FSRS.

---

## Patrones comunes detectados

Los componentes que aparecen una y otra vez en los proyectos serios:

1. **Memoria del alumno en dos capas**: (a) memoria conversacional/perfil (Mem0, Honcho, embeddings+dedup como pacer-ai, o JSON local como engram) y (b) memoria de dominio (mastery por punto de conocimiento, cuaderno de errores). Los proyectos que fallan (NotebookLM, Mr.-Ranedeer) tienen solo contexto puntual y por eso no hay continuidad.
2. **Scheduler separado del chat**: siempre hay un proceso/cron distinto (APScheduler en pacer-ai, cron horario en Cloudflare Workers en mind-mentor, nudges en hooks de sesión en engram) encargado de los contactos proactivos. El "¿hiciste la tarea?" es trabajo de fondo, no del turno del LLM.
3. **Motor de repetición espaciada como pieza estándar**: SM-2 (mind-mentor) o FSRS-4.5 (engram; librerías oficiales py-fsrs/fsrs4anki). FSRS es hoy el estándar emergente con parámetros optimizables por usuario.
4. **Ciclo diario con momentos fijos** (pacer-ai: 07:00 briefing / 18:00 errores / 21:30 reporte / 22:30 cierre) + señales de racha/streak. La constancia se gamifica y se mide con tasas reales de check-off.
5. **Refuerzo basado en errores**: registro sistemático del error → regeneración de variantes → recalificación (error book de pacer-ai; examinador ciego de engram; verificación de recuerdo libre con "recibos").
6. **Multimodalidad con política de silencio**: los tutores de pantalla/voz (onevision, SAGE) resuelven el problema opuesto al chat: no cuándo hablar sino **cuándo callar** (back-off exponencial, echo guard, hablar solo ante error real). Crítico para que el seguimiento no sea invasivo.
7. **Pedagogía explícita**: Theory-of-Mind (tutor-gpt), Socrático (no dar la respuesta hasta que el alumno la produzca), 2-Sigma con anotaciones (Bloom). Ninguno deja que el LLM "explique y ya".
8. **Seguridad emocional** en público infantil/juvenil: red de seguridad con keywords + triage antes del agente principal (pacer-ai) y detección de frustración (SAGE).
9. **Stack típico**: FastAPI/Next.js + SQLite→Postgres + SSE streaming + router de intents + embeddings locales pequeños (MiniLM 384d) — todo replicable sin infra pesada.
10. **Hueco confirmado**: nadie combina TODO — LMS con contenido empaquetado (Frappe Learning) × tutor conversacional pedagógico (tutor-gpt/Bloom) × loop diario proactivo (pacer-ai/mind-mentor) × visión de pantalla (onevision/SAGE) × FSRS. Nuestra app-tutor sería el primer proyecto que integra los cinco pilares.
