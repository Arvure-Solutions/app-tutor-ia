---
tags: [tutor-ia, educacion, propuesta, proyecto]
creado: 2026-08-25
estado: 🌱 verde — propuesta tras barrido de investigación
investigacion: "[[APP Tutor IA/00 ÍNDICE|ver índice del proyecto]]"
---

# Propuesta — APP Tutor IA

> **Tutor que no te deja solo al día siguiente.** Todo lo que existe hoy (NotebookLM, ChatGPT Study Mode, Khanmigo) explica bien pero **desaparece cuando cerrás la app**. Nadie retoma tu aprendizaje mañana a las 9, nadie pregunta si hiciste la tarea, nadie mira por encima de tu hombro y dice *"por ahí no es"*. Eso es este proyecto.

## 1. El problema, validado en la investigación

| Evidencia | Fuente |
|---|---|
| NotebookLM **admite su mayor hueco**: "no hay forma de saber si tus alumnos usaron el material" | [[APP Tutor IA/docs/investigacion/youtube-videos\|youtube-videos]] §3, min ~8:40 |
| Dolor #1 en Reddit/X: herramientas **amnésicas**, la sesión termina y nadie retoma el hilo; usuarios lo tapan con prompts artesanales y bots caseros de WhatsApp | [[APP Tutor IA/docs/investigacion/comunidad-usuarios\|comunidad-usuarios]] |
| Comprensión ≠ retención: la herramienta nunca te evalúa ni agenda repaso ("ilusión de haber estudiado") | íbid. |
| Solo ~5% usa las herramientas online como debe (dato Khanmigo) → sin seguimiento, la herramienta no se usa | youtube-videos §6 |
| Hueco de mercado confirmado: **ningún repo integra los 5 pilares** (cursos × tutor × loop diario × visión de pantalla × FSRS) | [[APP Tutor IA/docs/investigacion/github-repos\|github-repos]] |

## 2. Qué hace (loops, no chats)

```
        DÍA A DÍA
 ┌─────────────────────────────────────────────┐
 │ 07:00  BRIEFING      "Ayer quedamos en X.   │
 │                      Hoy: Y (12 min)."       │
 │ 09:30  SESIÓN        enseña socrático, ve    │
 │                      pantalla si se permite  │
 │ 14:00  CHECK-IN voz  "¿Cómo vas con Y?"      │
 │ 18:00  REPASO FSRS   re-pregunta lo fallido  │
 │ 21:30  REPORTE       qué dominaste / qué     │
 │                      vuelve mañana           │
 └─────────────────────────────────────────────┘
```

- **Popup de tarea**: "¿Hiciste la tarea?" con seguimiento firme pero **sin culpa** (rachas reparables, nada de búho llorón).
- **Check-in hablado**: micrófono > push notification (la gente ignora notificaciones, la voz no).
- **Ojo sobre el hombro** (opt-in): ve la pantalla, detecta el error real y habla: *"por ahí no es — mirá la línea 3"*.
- **Cursos empaquetados**: menú lateral Clase 1, Clase 2… estilo Frappe Learning, instalable en servidor.

## 3. ⭐ Modelo de razonamiento para enseñar (el corazón)

Siete módulos encadenados. Cada decisión pedagógica es una regla inspeccionable, no magia negra.

### M1 · Memoria del alumno (quién sos y qué sabés)
Memoria híbrida estilo [mem0/Letta](https://github.com/letta-ai/letta):
- **Core**: objetivos, nivel, preferencias, contexto de vida.
- **Episódica**: cada sesión, errores, dudas ("se trabó en recursión el martes").
- **Semántica**: grafo de conceptos dominados/débiles (knowledge state).
> Regla: *nada se olvida, todo se decae*. Los conceptos fallidos suben su prioridad de repaso.

### M2 · Diagnóstico continuo (qué tan bien lo sabés)
Knowledge tracing **BKT** ([pyBKT](https://github.com/CAHLR/pyBKT)) como MVP: probabilidad P(domina|historial) por concepto.
→ **Mastery gate**: no avanzás de clase hasta P ≥ 0.8 en los prerrequisitos (Bloom 2σ: tutoría 1-a-1 con maestría supera al 98% del aula tradicional).

### M3 · Planificador (cuándo repasar y qué mostrar)
- **Repaso**: FSRS-4.5 ([py-fsrs/ts-fsrs](https://github.com/open-spaced-repetition), MIT) — ~81% mejor retención que SM-2/Anki clásico.
- **Contenido nuevo**: ZPD numérica — dificultad objetivo = zona donde el alumno falla ~15-30% de los intentos (si acierta todo: muy fácil; si fracasa todo: demasiado difícil). Scaffolding con fading progresivo.
- **Mezcla**: interleaving ≤2 habilidades por sesión (práctica intercalada supera al bloque masivo).

### M4 · Generador de sesión (retrieval-first)
Nunca empieza explicando: **empieza preguntando** (testing effect). Genera:
1. 2-3 preguntas de recuperación de lo visto días atrás (del planificador FSRS).
2. 1 challenge nuevo dentro de la ZPD.
3. Cierre: metacognición — "¿qué te costó más? ¿por qué?"

### M5 · Intervención socrática (el "por ahí no es")
Escalera de pistas N0→N3, nunca dar la respuesta primero (RCT Harvard 2025: ~2× aprendizaje/hora vs respuesta directa):

| Nivel | Comportamiento | Ejemplo |
|---|---|---|
| **N0** | Silencio activo: observa 2 intentos | *(ve que errás el mismo paso dos veces)* |
| **N1** | Pregunta focalizadora | "¿Qué está devolviendo esa variable?" |
| **N2** | Pista estructural | "El error está entre la línea 3 y 5, ¿qué tipo es `x` ahí?" |
| **N3** | Ejemplo análogo resuelto + fade back | "Mirá este caso parecido… ahora vos." |

Con pantalla: VLM detecta **cambios significativos** (no habla ante cada movimiento; back-off exponencial, patrón [onevision](https://github.com/Arjunhg/onevision)). Con voz: tono/pausa larga = confusión posible → baja un nivel de dificultad o cambia de estrategia (estados afectivos, D'Mello).

### M6 · Accountability sin culpa (que vuelvas mañana)
- **Implementation intentions**: el check-in no es "¿vas a estudiar?" sino "¿a las 19h en tu escritorio o después de cenar?" (compromiso específico = 2-3× cumplimiento).
- Rachas **reparables** (SmarterHumans) + tono coach firme, jamás avergonzante (lección streak-guilt Anki/Duolingo).
- Reporte semanal: progreso visible, no puntos ni castigos.

### M7 · Loop diario orquestado (el diferenciador)
Patrón [pacer-ai](https://github.com/flysheep-ai/pacer-ai): scheduler (APScheduler/cron) dispara briefing → sesiones → check-ins → repaso → reporte. **La app te busca a vos.** Este loop es exactamente lo que NotebookLM declaró no tener.

### Ejemplo real de una interacción
```
[18:00] TUTOR (voz): "¿Hiciste el ejercicio de recursión?"
TÚ:    "Empecé pero me tira error"
TUTOR: "Compartime la pantalla... ok. ¿Qué dice el error?"
TÚ:    "'maximum recursion depth exceeded'"
TUTOR: (N1) "¿Y en qué momento tu función se llama a sí misma
             sin llegar al caso base?"
TÚ:    "...ah, no tengo caso base cuando n es 0"
TUTOR: "Eso es. Probalo."
TÚ:    (funciona)
TUTOR: "Dominado. Te lo vuelvo a preguntar el sábado.
        Mañana a las 9: closures, 10 minutos."
```

## 4. Arquitectura técnica

```
┌────────────────────────────────────────────────────────────┐
│                     CLIENTES                               │
│   Desktop (Electron/Tauri: pantalla+mic+popup)             │
│   Móvil (notificaciones+voz)   Web (curso tipo Frappe)     │
└──────────────┬─────────────────────────────────────────────┘
               │
┌──────────────▼─────────────────────────────────────────────┐
│                  ORQUESTADOR DE AGENTES                    │
│  Scheduler (loop diario) · Router de intenciones           │
│  ┌─────────┐ ┌──────────┐ ┌───────────┐ ┌──────────────┐  │
│  │ M1 Mem. │ │ M2 Diagn.│ │ M3 Planif.│ │ M4 Sesiones  │  │
│  │ mem0/SQL│ │ pyBKT    │ │ py-fsrs   │ │ LLM socrático│  │
│  └─────────┘ └──────────┘ └───────────┘ └──────────────┘  │
│  ┌──────────────────────┐  ┌────────────────────────────┐ │
│  │ M5 Percepción (optin)│  │ M6/M7 Accountability       │ │
│  │ screen VLM · ASR voz │  │ check-ins · reportes       │ │
│  └──────────────────────┘  └────────────────────────────┘  │
└──────────────┬─────────────────────────────────────────────┘
               │
     SQLite/Postgres (estado) · Supabase opcional (sync multi-dispositivo)
```

**Decisiones:**
- **Base de curriculum**: inspirar UI en Frappe Learning (Curso→Capítulo→Lección) pero **custom ligero** — Frappe completo es demasiado para un tutor personal; su modelo de datos sí es la referencia ([[APP Tutor IA/docs/investigacion/plataformas-pedagogia|plataformas-pedagogia]] A.8).
- **FSRS + BKT + LLM** son piezas open-source existentes: el trabajo propio es la **orquestación** y el tono.
- **Privacidad como feature de primera clase**: pantalla y microfono opt-in, procesamiento local cuando sea posible, indicador visible siempre. El rechazo a Microsoft Recall es la lección (comunidad-usuarios §4).

## 5. Roadmap

| Fase | Entregable | Prueba de éxito |
|---|---|---|
| **F0** (sem 1-2) | Motor pedagógico CLI: memoria + BKT + FSRS + sesión retrieval-first en terminal | 1 usuario, 7 días seguidos usando el loop diario |
| **F1** (sem 3-4) | Popup/check-ins desktop + empaquetador de curso (md→clases con menú lateral) | Un curso real cargado y completado con mastery gates |
| **F2** (sem 5-6) | Voz: check-in hablado + transcripción | Check-in de voz respondido ≥80% de los días |
| **F3** (sem 7-8) | Visión de pantalla opt-in con hint ladder N0-N3 | Corrige un error real antes de que el usuario lo encuentre |
| **F4** | Servidor self-hosted (Docker), multiusuario, reportes semanales | Instalable en 5 min como Frappe |

## 6. Riesgos abiertos

1. **Adopción del screen-awareness**: mitigación = opt-in granular + local-first + nicho ADHD inicial.
2. **Costo LLM** de sesiones diarias: mitigación = modelos pequeños locales para percepción, LLM grande solo para enseñanza.
3. **Friction del popup**: si molesta más de lo que ayuda, muere — medir tasa de respuesta desde F1.

---
**Investigación completa:** [[APP Tutor IA/docs/investigacion/github-repos|GitHub]] · [[APP Tutor IA/docs/investigacion/comunidad-usuarios|Reddit/X]] · [[APP Tutor IA/docs/investigacion/youtube-videos|YouTube]] · [[APP Tutor IA/docs/investigacion/plataformas-pedagogia|Plataformas y pedagogía]]
