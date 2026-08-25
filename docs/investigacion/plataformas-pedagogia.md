# Investigación: Plataformas LMS self-hosted + Modelos pedagógicos/algorítmicos para un tutor IA

**Fecha:** 2026-08-25 · **Proyecto:** APP Tutor IA · **Alcance:** solo investigación (Parte A: plataformas; Parte B: motor pedagógico). Sin código.

---

# PARTE A — PLATAFORMAS LMS SELF-HOSTED

## A.1 Frappe Learning (frappe/lms) — la referencia principal

LMS 100 % open source construido sobre **Frappe Framework** (Python, ORM propio, REST API) + **Frappe UI** (Vue 3). Nació en 2021 como sistema interno de Mon.School porque "Moodle tenía formularios larguísimos y UI confusa"; hoy es el producto educativo del ecosistema Frappe (usado por Frappe School, Mon School, TinkerHub).

- **Modelo de datos (verificado en el repo `lms/lms/doctype`):** jerarquía de 3 niveles `LMS Course` → `Course Chapter` → `Course Lesson`, con tablas puente (`chapter_reference`, `lesson_reference`) y sidecars: `LMS Enrollment`, `LMS Course Progress`, `LMS Quiz`/`LMS Option`, `LMS Assignment Submission`, `LMS Batch`, `LMS Batch Timetable`, certificados, badges, cupones, evaluadores con agenda.
- **UI:** SPA Vue; menú lateral por curso con capítulos expandibles y lecciones numeradas — exactamente el patrón "Clase 1, Clase 2…" que queremos replicar.
- **Progreso:** cada lección marcada como completada genera un registro `LMS Course Progress`; el % del curso se calcula como lecciones completadas / total (docs oficiales "Course Progress Calculation"). Es tracking binario simple: no hay mastery, ni memoria de errores, ni repetición espaciada.
- **Instalación self-hosted:** script oficial `easy-install.py deploy --project=… --image=ghcr.io/frappe/lms --app=lms` que levanta Docker Compose (app + MariaDB + Redis) "en unos 5 minutos". Alternativa gestionada: Frappe Cloud. Requisitos realistas: servidor Linux 2 vCPU / 2–4 GB RAM, dominio con TLS (el script configura Traefik).
- **Extensibilidad:** al ser una app Frappe se extiende con DocTypes nuevos, hooks Python, scripts cliente JS y apps adicionales en el mismo bench (multi-app). API REST automática por DocType.
- **Licencia:** AGPL-3.0 (repo github.com/frappe/lms).

**Fuentes:** https://github.com/frappe/lms · https://docs.frappe.io/learning · https://docs.frappe.io/learning/course-creation (jerarquía) · https://docs.frappe.io/learning/others/course-progress-calculation · https://frappe.io/easy-install.py

## A.2 Moodle

El estándar industrial: PHP, >2000 plugins, SCORM 1.2/2004 y LTI, 40+ tipos de pregunta, competencias, badges. Usado en 240 países. **Contras para nosotros:** panel admin con cientos de ajustes, tema base anticuado, ~4 GB RAM recomendados, configuración inicial larga. Instalación vía Bitnami/Docker razonablemente fácil. Licencia GPL v3. Modelo curricular flexible pero heterogéneo (secciones, actividades, recursos sin jerarquía estricta); tracking granular (completion tracking, gradebook) pero orientado a notas, no a modelado cognitivo.

**Fuente:** https://selfhosting.sh/best/education/

## A.3 Canvas LMS (edición open source)

La mejor UX del grupo (los estudiantes la prefieren), SpeedGrader excelente, buena API, LTI. **Pero:** Rails, sin imagen Docker oficial, compilación de assets exige 6+ GB RAM, despliegue complejo con workers múltiples; la edición OSS pierde funciones del cloud. AGPL v3. Para un homelab/startup pequeño: no recomendada como base.

**Fuente:** https://selfhosting.sh/best/education/

## A.4 Open edX (+ instalador "Tutor")

Plataforma detrás de edX.org, diseñada para MOOC masivos: video-learning, foros, ejercicios autocalificados, certificados. **Tutor** es su distribución oficial basada en Docker ("100 % open source, corre enteramente en Docker, instalación 1-click"): `tutor local launch` pregunta configuración, genera templates, descarga imágenes y provisiona una plataforma completa en <10 min en un servidor con buen ancho de banda; soporta theming, plugins (discovery, ecommerce, notes) y Kubernetes. **Costo real:** pila enorme (LMS + Studio/CMS + MySQL + MongoDB + Redis + MinIO + MFEs separados), varios servicios y decenas de GB; construir imágenes MFE puede tardar ~40 min en VM pequeña. AGPL v3. Solo tiene sentido si el objetivo son catálogos masivos multiorganización.

**Fuentes:** https://github.com/overhangio/tutor · https://docs.tutor.edly.io/ · https://openedx.atlassian.net/wiki/spaces/COMM/pages/3793485852/How+to+Deploy+Tutor+Palm+with+the+Open+edX+Experimental+Plugins · https://docs.openedx.org/projects/openedx-proposals/en/latest/architectural-decisions/oep-0045/decisions/0001-tutor-as-replacement-for-edx-configuration.html

## A.5 Chamilo

PHP, GPL v3, más liviano que Moodle: admin más limpio, cursos más rápidos de crear, huella menor; quizzes, asignaciones, learning paths, BigBlueButton. Ideal para equipos pequeños que quieren LMS clásico sin la complejidad de Moodle, pero comparte el ADN "aula virtual": nada de modelado del alumno ni adaptatividad real.

**Fuente:** https://selfhosting.sh/best/education/

## A.6 Alternativas ligeras tipo "curso como documentación"

| Opción | Qué es | Pros | Contras |
|---|---|---|---|
| **MkDocs Material** | SSG Python, `pip install mkdocs-material`; navegación lateral jerárquica, búsqueda, tabs, admonitions, versiones | Cero backend, Markdown puro, nav lateral idéntica al patrón Frappe, hosting gratis | Estático: sin login, sin progreso por usuario, sin tracking; licencia MIT (core), tema "Insiders" es patrocinio |
| **Docusaurus** | SSG JS de Meta | Ecosistema React, MDX, versionado, i18n, MIT | Igual de estático; más peso de tooling |
| **Course-in-a-box** (P2PU) | Plantilla Jekyll/GitHub Pages para cursos abiertos | Gratis, comunidad de educación abierta | Arcaico, sin interactividad |

Estas opciones sirven para empaquetar el *contenido* de los cursos (nuestros "cursos empaquetados" podrían incluso generarse desde archivos Markdown), pero no cubren seguimiento, ni popups, ni motor pedagógico.

**Fuentes:** https://squidfunk.github.io/mkdocs-material/getting-started/ · https://docusaurus.io · https://course-in-a-box.p2pu.org

## A.7 Tabla comparativa

| Plataforma | Complejidad de instalación | Modelo de datos de currículo | Tracking de progreso | Extensibilidad | Licencia |
|---|---|---|---|---|---|
| **Frappe Learning** | Baja-media: easy-install.py Docker (~5 min); requiere bench Frappe para desarrollar | Curso→Capítulo→Lección limpio (DocTypes), batches, quizzes, assignments | Binario por lección + % curso; analytics de signups/completación | Alta: apps Frappe, DocTypes, hooks, REST automática | AGPL-3.0 |
| **Moodle** | Media-alta (Bitnami/Docker OK, config larga) | Secciones/actividades flexibles, menos jerárquico | Granular (completion, gradebook, competencias) | Muy alta: 2000+ plugins, LTI/SCORM | GPL-3.0 |
| **Canvas OSS** | Alta: build Rails desde fuente, 6+ GB RAM | Cursos→módulos→items, fuerte | Granular + SpeedGrader | Media: API buena, pocos plugins OSS | AGPL-3.0 |
| **Open edX + Tutor** | Media-alta (Tutor lo facilita) pero pila pesada multi-contenedor | Courseware estructurado (sections/subsections/units), OLX XML | Granular por unidad/subunidad, eventos xAPI-like | Alta vía XBlocks/plugins, pero curva dura | AGPL-3.0 |
| **Chamilo** | Baja-media | Cursos→learning paths→items | Medio (paths, scorm) | Media (plugins PHP) | GPL-3.0 |
| **MkDocs Material / Docusaurus** | Mínima (SSG estático) | Archivos Markdown con nav jerárquica | Ninguno | Limitado al front-end | MIT |

## A.8 Veredicto para APP Tutor IA

- **Como BASE (backend de contenido): Frappe Learning.** Su modelo Curso→Capítulo→Lección es exactamente nuestro menú lateral; la instalación Docker es la más simple del grupo; DocTypes extensibles nos dejarían añadir `LessonAttempt`, `ReviewCard` (FSRS), `CheckIn` sin pelear contra el framework; AGPL es viable para producto propio. Costo: aprender el ecosistema Frappe (bench, MariaDB) y vivir con MariaDB + Python/Vue.
- **Como INSPIRACIÓN de UX: Canvas** (flujo de tareas limpio) y **Duolingo/Khan Academy** (micro-sesiones, streaks humanizados). La estética minimalista final la definimos nosotros.
- **Como EMPAQUETADO de contenido: Markdown + MkDocs-style**, porque permite versionar cursos en git y renderizarlos dentro de nuestra app custom.
- **Descartadas como base:** Open edX (peso injustificado para app personal/tutoría 1:1), Canvas OSS (build Rails), Chamilo y Moodle (filosofía de aula, no de tutor individual; Moodle útil solo si algún día necesitamos SCORM corporativo).
- **Recomendación central:** app custom ligera (nuestro motor pedagógico ES el producto diferencial) que adopte el *modelo de datos* de Frappe (curso/capítulo/lección/progreso como entidades simples) y, opcionalmente, use Frappe Learning como panel de autoría/administración de cursos mientras el tutor vive en su propio backend.

---

# PARTE B — MODELO DE RAZONAMIENTO PARA ENSEÑAR

> Cada concepto: explicación breve + traducción a feature concreta + fuentes.

## B.1 Mastery learning + problema de las 2 sigmas (Bloom)

Bloom (1984) demostró que el alumno promedio tutelado 1-a-1 **con mastery learning** rendía 2 desviaciones estándar por encima del aula convencional —mejor que el 98 % de sus compañeros—. El mastery learning en grupo ya capturaba ~1 sigma: unidades pequeñas, test formativo tras cada una, y **no avanzar** hasta demostrar dominio (en Bloom: ≥90 % en tutoría, ≥80 % en aula). Revisiones posteriores moderan la cifra (tutoring típico d≈0.4–1.0; sistemas de software bien diseñados ≈0.70) pero confirman la dirección. La lección operativa: el efecto viene más de *exigir dominio antes de avanzar* que de la mera atención individual.

**Traducción a feature:** cada lección termina con un "gate" de mastery: 3–5 ítems de recuperación; si score < umbral (p. ej. 80 %), el planificador NO desbloquea la siguiente clase sino que agenda re-práctica dirigida a los conceptos fallados. El menú lateral muestra candados ✓/🔒 por clase, no solo "completada".

**Fuentes:** Bloom, "The 2 Sigma Problem", Educational Researcher 1984 — http://web.mit.edu/5.95/www/readings/bloom-two-sigma.pdf · https://en.wikipedia.org/wiki/Bloom%27s_2_Sigma_Problem · revisión crítica sistemática: https://nintil.com/bloom-sigma

## B.2 Retrieval practice / testing effect

Recuperar información de memoria fortalece la memoria mucho más que releerla: Roediger & Karpicke (2006) —61 % vs 40 % de retención a una semana—; Karpicke & Blunt (Science 2011): práctica de recuperación superó incluso mapas conceptuales elaborativos. El releer genera "ilusión de fluidez"; el esfuerzo de recuperación es una *desirable difficulty* (Bjork). Meta-análisis: g≈0.50–0.61, crece con el intervalo de retención. Regla de diseño: la respuesta nunca debe estar visible en pantalla cuando el alumno intenta responder.

**Traducción a feature:** toda sesión abre con 2–3 preguntas de recuperación de contenido ANTERIOR (antes de mostrar material nuevo); los quizzes cierran respuestas hasta después del intento; el tutor LLM está instruido para pedirle al alumno que explique/recuerde antes de revelar ("¿qué recuerdas de X?") — el quiz es el horno, no el termómetro.

**Fuentes:** https://www.science.org/doi/10.1126/science.1199327 · Karpicke & Bauernschmidt 2011 (spacing absoluto): https://learninglab.psych.purdue.edu/downloads/2011/2011_Karpicke_Bauernschmidt_JEPLMC.pdf · https://en.wikipedia.org/wiki/Testing_effect · Dunlosky et al. 2013: https://journals.sagepub.com/doi/10.1177/1529100612453266

## B.3 Repetición espaciada: SM-2 vs FSRS

SM-2 (SuperMemo/Anki clásico) multiplica el intervalo por un factor fijo según calificación; ignora el tiempo real y la dificultad individual. **FSRS** (Free Spaced Repetition Scheduler, integrado nativamente en Anki 23.10+) modela la memoria con el trío **D-S-R**: Difficulty, Stability (intervalo al que R=90 %) y Retrievability R(t,S)=(1+FACTOR·t/S)^DECAY, con parámetros entrenables por máxima verosimilitud sobre historiales reales (17 params en v4.5, 21 en v6). Benchmark abierto (1.7B reviews, 20k usuarios): LogLoss 0.3624 (FSRS-4.5) / 0.3460 (v6) vs 0.7317 (SM-2) → ~81–84 % mejor predicción. Implementaciones abiertas listas: **ts-fsrs** (TypeScript), **py-fsrs** (Python), go/rs/dart/swift. Con `request_retention` configurable (0.9 default) calcula cuándo repasar cada ítem para mantener esa probabilidad de recuerdo.

**Traducción a feature:** cada concepto/ítem del curso vive como una "card" con estado FSRS {difficulty, stability, due}; el planificador diario selecciona cards vencidas (R cayendo bajo 0.9) y las mezcla en la sesión. Empezamos con ts-fsrs y parámetros por defecto (capturan ~98 % del beneficio de v6 sin optimizar); cuando haya historial propio (>1000 reviews), optimizamos w0–w20 por usuario.

**Fuentes:** https://github.com/open-spaced-repetition/free-spaced-repetition-scheduler (lista de librerías) · https://github.com/open-spaced-repetition/ts-fsrs · https://github.com/open-spaced-repetition/py-fsrs · fórmulas: https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-Algorithm · benchmark/param defaults: https://github.com/SqueakyRobot/fsrs (tabla LogLoss)

## B.4 Zona de desarrollo próximo (Vygotsky) y scaffolding → dificultad adaptativa

ZPD = banda de tareas que el alumno no resuelve solo pero sí con ayuda. Wood, Bruner & Ross (1976) acuñaron "scaffolding" con tres rasgos operativos (van de Pol 2010): **contingente** (calibrado turno a turno según la respuesta), **con fading** (se retira al crecer la competencia) y con **transferencia de responsabilidad**. Corolario crítico: *expertise reversal effect* — dar andamiaje detallado a quien ya domina lo perjudica. Traducción computacional clásica: mantener la tasa de éxito del alumno en ~70–85 % (ni trivial ni frustrante) ajustando dificultad y ayuda.

**Traducción a feature:** cada ejercicio lleva dificultad 1–10 estimada; el planificador elige ítems cuya dificultad proyectada caiga dentro de [mastery_estimado+1, mastery_estimado+3] (la ZPD numérica del alumno por skill). Si acierta 3 seguidos sube nivel; si falla 2, baja y activa scaffolding (paso a paso). El andamiaje se apaga automáticamente al subir el mastery (fading).

**Fuentes:** Vygotsky 1978 (ZPD); Wood/Bruner/Ross 1976; síntesis: https://cognitivepsychology.com/Scaffolding · van de Pol et al. 2010 (3 criterios) · ZPD en sistemas adaptativos: https://www.researchgate.net/publication/221414136_Toward_Measuring_and_Maintaining_the_Zone_of_Proximal_Development_in_Adaptive_Instructional_Systems · expertise reversal: citado en https://arxiv.org/html/2602.07308v1

## B.5 Método socrático y escalada de pistas (hint escalation, worked examples, fading)

El tutor eficaz no da la respuesta: hace preguntas que estrechan el espacio de búsqueda (socrático) y, si el alumno se atasca, escala ayuda en gradiente: pista genérica → pista específica → paso parcial mostrado → ejemplo resuelto (worked example). Aleven/Renkl mostraron que **fade adaptativo** de worked examples (reemplazar pasos por espacios en blanco conforme mejora el rendimiento) produce más transferencia que problemas puros o fade fijo. El marco ICAP (Passive→Active→Constructive→Interactive) da el dial de compromiso; un ITS reciente (2026) que elegía adaptivamente entre ejemplos "guiados" (activo) y "buggy" (constructivo) usando BKT mejoró postests significativamente, especialmente en alumnos de baja base. Prueba de campo clave: el RCT de Harvard (Kestin et al., Scientific Reports 2025, N=194) — un tutor IA diseñado con estas prácticas (recuperación activa, pacing adaptativo, cuestionamiento socrático, guardarrails anti-respuesta-directa) hizo que alumnos aprendieran **~2× por hora** frente a su propia clase de active learning, con más engagement y motivación.

**Traducción a feature:** política de pistas de 4 niveles codificada en el prompt del tutor: N0 pregunta guía socrática → N1 pista conceptual → N2 pista procedural/esqueleto → N3 worked example completo; el nivel sube tras cada fallo o silencio largo y se resetea al acertar. Modo "ejemplo buggy": mostrar solución errónea para que el alumno la corrija (constructivo). Guardarraíl duro: el tutor nunca emite la respuesta final salvo comando explícito del usuario.

**Fuentes:** Kestin et al. 2025: https://www.nature.com/articles/s41598-025-97652-6 · fading adaptativo (Aleven/Salden/Renkl, CMU): http://www.cs.cmu.edu/~rons/ICLS%202008%20poster%20Salden%2C%20Aleven%2C%20Schwonke%20%26%20Renkl.pdf · scaffolding adaptativo con BKT/DRL (ICAP): https://arxiv.org/abs/2602.07308

## B.6 Knowledge tracing: BKT, DKT, AKT

Estimar en tiempo real qué sabe el alumno. **BKT** (Corbett & Anderson 1994): HMM binario conocido/no-conocido por skill con parámetros interpretables (learn, guess, slip, forget); actualización bayesiana por respuesta; funciona con poco dato y es explicable. **DKT** (Piech 2015): LSTM sobre secuencias alumno-item-correcto; mejor predicción bruta, caja negra, necesita miles de interacciones. **AKT** (Ghosh 2020): transformer con mecanismo de olvido; top en benchmarks pero —limitación documentada en DKT2 (arXiv 2501.14256)— requiere interacciones futuras en algunas variantes y no produce un estado de conocimiento comprehensivo. Datos mínimos (schema universal): user_id, orden temporal, question_id, skill_name/concept_id, correct(0/1). Guía práctica: empezar con BKT/logístico como baseline transparente; deep KT solo si hay volumen.

**Traducción a feature (MVP viable):** BKT por concepto con pyBKT (Python, MIT-friendly) alimentado por nuestro log de intentos {user, timestamp, skill, correct}. Cada concepto guarda P(conocido); esa probabilidad alimenta (a) el gate de mastery de B.1, (b) la ZPD de B.4 y (c) qué cards crea el planificador. Deep KT queda en roadmap para cuando existan ≥50k interacciones agregadas.

**Fuentes:** pyBKT: https://github.com/CAHLR/pyBKT · panorama y esquema mínimo de datos: https://educatian.github.io/knowledge-tracing · BKT/DKT/AKT en contexto: https://www.nature.com/articles/s41598-025-10497-x · limitaciones AKT: https://arxiv.org/abs/2501.14256

## B.7 Práctica intercalada y variación (interleaving)

Mezclar tipos de problema dentro de una sesión (A,C,B,A…) supera al bloqueo (AAAA,BBBB) en tests diferidos: Rohrer & Taylor 2007 —63 % vs 20 % a una semana—; en aulas reales de 7º grado, ventaja persistente a 30 días (d≈0.81–0.87, Rohrer et al.). Mecanismos: obliga a **discriminar** qué estrategia aplica (lo que pide un examen real) e implícitamente espacia cada tópico. Costo: se siente más difícil durante la sesión — otra desirable difficulty que el diseño debe explicar al usuario. Excepción: bloquear al introducir una técnica totalmente nueva, luego intercalar.

**Traducción a feature:** el generador de sesiones nunca emite >2 ítems consecutivos del mismo skill; baraja skills ya vistos (vencidos por FSRS) con el skill nuevo del día en proporción ~60/40 review/nuevo. Al terminar sesión, micro-copy: "hoy mezclamos temas a propósito: cuesta más y aprende más".

**Fuentes:** Rohrer & Taylor 2007 (resumen y cifras): https://lecturescribe.io/blog/interleaving-vs-blocked-practice · estudio aula ED557355: https://files.eric.ed.gov/fulltext/ED557355.pdf · mecanismos discriminación/espaciado: https://link.springer.com/article/10.3758/s13421-019-00918-4

## B.8 Estados afectivos: confusión y aburrimiento por telemetría/voz

D'Mello, Graesser y Baker (AutoTutor) establecieron que los estados relevantes en aprendizaje con software son confusión, flow/compromiso, frustración y aburrimiento — no las emociones básicas. Hallazgos clave: **la confusión moderada predice aprendizaje** (confusion can be beneficial, 2014) y "mejor frustrado que aburrido" (Baker 2010: el aburrimiento persiste y daña). Detección factible sin cámaras: señales conversacionales ("no entiendo", "mmm"), tiempo de reacción anómalo, latencias de tecleo, prosodia de voz (pausas, monotonía; F1≈0.68 detectando confusión por actos de habla), patrones de abandono de ítems. Intervención: ante confusión sostenida → escalada de pistas; ante aburrimiento → cambiar modalidad (subir reto, variar formato) en vez de regañar.

**Traducción a feature:** módulo de telemetría ligero: latencia entre pregunta y primer input, tiempo por ítem vs media histórica, ratio de saltos, palabras de duda en voz/texto (STT ya disponible por el micrófono), energía tonal básica. Salida: score {engaged | confused | bored} con histéresis (≥2 señales para cambiar estado) que alimenta el canal de intervención: confused→hint level+1; bored→inyectar reto/variación o sugerir pausa; nunca penalizar la confusión (mostrarla como señal positiva de aprendizaje).

**Fuentes:** AutoTutor afectivo (D'Mello et al. 2008): https://www.researchgate.net/publication/228673992_AutoTutor_detects_and_responds_to_learners_affective_and_cognitive_states · Baker et al. 2010 "Better to be frustrated than bored", IJHCS 68(4):223-241 · D'Mello et al. 2014 "Confusion can be beneficial for learning", Learning and Instruction 29:153-170 · detección por prosodia (F-1 0.68) y revisión multimodal: https://arxiv.org/html/2401.15201v1 · arquitectura de referencia producción: https://www.zenml.io/llmops-database/emotionally-aware-ai-tutoring-agents-with-multimodal-affect-detection

## B.9 Psicología del hábito y accountability (check-ins sin culpa)

Bucle hábito cue→rutina→recompensa (Duhigg): la conducta se automatiza si un disparador estable precede a una acción con recompensa rápida. **Implementation intentions** (Gollwitzer): "si ocurre X, hago Y" duplican la tasa de ejecución frente a metas vagas. **Commitment devices** comprometen públicamente o ponen algo en juego. Los **nudges** (recordatorios contextuales, red-dot +1.5 % DAU en Duolingo) funcionan si llegan en momento accionable. **Streaks:** potentes (streak wager de Duolingo: +14 % retención día-7) pero optimizan retención, no aprendizaje: encuesta citada —62 % de usuarios sintió culpa al fallar un día, 34 % ansiedad por notificaciones—; la ansiedad crónica eleva el "filtro afectivo" y enseña a abrir la app, no a aprender. Diseño correcto: streaks con *streak freeze*/perdón, métricas de progreso real (conceptos dominados) junto a la racha, y check-ins que preguntan intención ("¿qué vas a estudiar hoy y a qué hora?" = implementation intention) en lugar de avergonzar.

**Traducción a feature:** check-in matutino que captura implementation intention ("¿a las qué hora y qué clase?") → recordatorio a ESA hora (cue personalizado); popup de tarea con fecha pactada por el usuario (commitment device suave); racha visible pero "sin culpa": día perdido no rompe nada, muestra botón "retomar" con sesión de 5 min pre-armada (comeback mechanic); celebración ligada a mastery ganado, no solo a días consecutivos; opción de apuestas propias ("si termino la clase 4 esta semana, …").

**Fuentes:** crítica streak/guilt: https://satur.app/blog/duolingo-shame-streak-psychology/ · mecánica streak+wager (blog oficial): https://blog.duolingo.com/how-streaks-keep-duolingo-learners-committed-to-their-language-goals/ · arquitectura de notificaciones/comeback: https://www.digia.tech/post/duolingo-habit-forming-reminders-retention-architecture/ · implementation intentions (Gollwitzer 1999, resumen): https://en.wikipedia.org/wiki/Implementation_intention · habit loop: https://en.wikipedia.org/wiki/The_Power_of_Habit

## B.10 Agentes LLM con memoria: mem0 / Letta (MemGPT)

Un tutor debe recordar al alumno entre sesiones; el contexto del prompt no basta. Dos arquitecturas de referencia abiertas: **Mem0** (arXiv 2504.19413) — capa de memoria que extrae hechos salientes de cada interacción, los consolida/deduplica y los recupera semánticamente en turnos futuros (add → learn → retrieve); pipeline automático, simple de integrar, con variantes self-host (OpenMemory). **Letta (ex-MemGPT, arXiv 2310.08560)** — memoria paginada estilo SO en tres tiers: **core memory** (bloques persona/human siempre en contexto, editables por el propio agente vía core_memory_replace/append), **recall memory** (historial completo buscable) y **archival memory** (vector store de largo plazo); el agente gestiona lecturas/escrituras con function calls e inner monologue. Para un tutor: core = perfil pedagógico vivo ("odia las fracciones, le funciona analogías deportivas, objetivo: examen en mayo"); archival = episodios de sesiones y errores recurrentes.

**Traducción a feature:** Perfil/Memoria del motor implementado como esquema híbrido: bloque estructurado SIEMPRE en el system prompt del tutor (equivaliente a core memory: objetivos, preferencias, errores típicos, última sesión) + store vectorial/archival de resúmenes por sesión escritos al cerrarla; extracción de hechos estilo mem0 ("el usuario confundió varianza con desviación → card FSRS nueva"). Todo local/self-host para privacidad de pantalla y voz.

**Fuentes:** Mem0 paper: https://arxiv.org/abs/2504.19413 · repo: https://github.com/mem0ai/mem0 · Letta/MemGPT paper: https://arxiv.org/abs/2310.08560 · repo: https://github.com/letta-ai/letta · patrón tres-tiers explicado: https://github.com/ankurkumarz/agent_memory_techniques/blob/main/all_techniques/26_letta_memgpt_patterns/README.md

---

# ARQUITECTURA PROPUESTA DEL MOTOR PEDAGÓGICO

```
                        ┌──────────────────────────────────────────────┐
                        │              APP TUTOR IA                    │
                        └──────────────────────────────────────────────┘

 ┌─────────────────┐        ┌────────────────────────────┐        ┌──────────────────────┐
 │  PERFIL/MEMORIA │        │        PLANIFICADOR         │        │ GENERADOR DE SESIÓN  │
 │                 │        │                            │        │                      │
 │ Core block      │──────▶│ • Mastery gate (BKT ≥ .8)   │──────▶│ • Recuperación previa │
 │ (persona/human) │ lectura│ • FSRS due-cards (R<0.9)    │ cola   │   (testing effect)    │
 │ Archival vector │        │ • ZPD band [m+1, m+3]       │ diaria │ • Intercalado ≤2 seg  │
 │ (resúmenes      │◀──────│ • Interleaving shuffle      │        │ • Hint policy N0..N3  │
 │  por sesión,    │ writes │ • Objetivo/calendario       │        │   socrática           │
 │  hechos mem0)   │        └────────────▲───────────────┘        │ • Worked examples     │
 └────────▲────────┘                     │                         │   con fading          │
          │                              │                         └──────────┬───────────┘
          │ hechos extraídos             │ P(mastery), D,S,R                   │
          │ de cada sesión               │ por skill                           │ ejecución
          │                              │                                     ▼
 ┌────────┴──────────────────────────────┴──────────────────────────────────────────────┐
 │                          LOG DE INTERACCIONES (event store)                          │
 │            {user, ts, skill, item, correct, latency, hints_used, affect}             │
 └────────▲───────────────────────────────────────────────────────┬────────────────────┘
          │                                                       │
          │                                                       ▼
 ┌────────┴───────────────┐                        ┌────────────────────────────────────┐
 │ DETECTOR DE CONTEXTO    │                        │ CANAL DE INTERVENCIÓN              │
 │ • telemetría ítem       │──── estado ───────────▶│ • popup de tarea (commitment)      │
 │   (latencias, saltos)   │  {engaged/confused/    │ • check-in mañana = implementation │
 │ • voz (pausas, dudas,   │   bored}, histéresis   │   intention + hora pactada (cue)   │
 │   energía tonal)        │                        │ • nudge contextual (hora propia)   │
 │ • observación pantalla  │◀── instrucciones ──────│ • comeback sin culpa (sesión 5')   │
 │   (opcional, consentida)│    (cambiar reto/      │ • celebración por mastery, no días │
 └─────────────────────────┘     modalidad)         └────────────────────────────────────┘

 FLUJO DIARIO:  check-in (intención) → planificador arma sesión (due-FSRS ∩ ZPD ∩ nuevo skill)
                → sesión con recuperación+socrático+pistas → log → BKT/FSRS update →
                memoria actualizada (hechos→core; resumen→archival) → cierre con mastery ganado.
```

**Notas de implementación MVP (orden sugerido):**
1. Modelo de datos Frappe-style (curso/capítulo/lección + attempt_log) — semana 1.
2. ts-fsrs sobre ítems + gate de mastery simple (score%) — semana 2.
3. Prompt-engineering del tutor: socrático + hint ladder N0-N3 + guardarraíl anti-respuesta (validado contra el diseño Kestin/Harvard) — semana 2-3.
4. pyBKT por skill cuando exista ≥100 intents/skill; antes: score móvil.
5. Check-ins + implementation intentions + comeback mechanic.
6. Telemetría afectiva mínima (latencias + palabras de duda) — después del core.
7. Memoria: core-block en system prompt + archival vectorial al cierre de sesión.

---

*Fin del documento. Todas las afirmaciones empíricas llevan fuente URL en su sección.*
