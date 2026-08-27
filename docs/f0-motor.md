# F0 — Motor pedagógico CLI

**Estado:** funcional (2026-08-25). Sin dependencias externas: Python 3 stdlib only.
Los upgrades `py-fsrs` y `pyBKT` son drop-in cuando el MVP lo pida.

## Uso

```bash
cd motor
python3 tutor.py clase            # abre la próxima lección desbloqueada
python3 tutor.py sesion           # sesión retrieval-first: repasos vencidos + nuevas
python3 tutor.py repaso           # solo repasos vencidos
python3 tutor.py estado           # progreso, maestría por lección, gates
python3 tutor.py demo --dias 6    # simula un alumno para validar el pipeline
python3 tutor.py reset            # borra el progreso
```

## Qué implementa del modelo de la propuesta

| Módulo propuesta | Implementación F0 |
|---|---|
| M1 Memoria | `estado_alumno.json`: BKT por concepto + tarjetas FSRS + historia completa |
| M2 Diagnóstico | BKT inline (`modelo.py`): P(domina\|historial), gate de maestría **≥ 0.80** |
| M3 Planificador | FSRS-lite: ease/intervalo/lapsos con grados again-hard-good-easy |
| Prerequisitos | Grafo en `curso_premiere.json`; lección bloqueada hasta dominar prereqs |
| M4 Sesión | retrieval-first: primero vencidas (orden por due), luego nuevas de la lección actual |
| M5 Socrático | Escalera N1→N2 (pista) → N3 (respuesta revelada); grado hard si acierta con pista |

## Curso piloto: Premiere Pro

11 lecciones (interfaz → organización → montaje → timeline → transiciones → audio →
keyframes → color → títulos → multicam → exportación), cada una con teoría, práctica
y banco de preguntas con claves de corrección + pista socrática.

## F0.5 — Robustez y complejización (2026-08-27)

Hardening del motor sin romper F0. Cambios:

- **Bugfixes reales del F0:**
  - `reset` crasheaba con `NameError` (`ESTADO_PATH` no importado) → corregido.
  - `curso_premiere.json` c10 tenía `"objeto"` en vez de `"objetivo"` → `KeyError` al mostrarla → corregido.
  - `cmd_sesion` hacía `random.shuffle(cola[4:])` sobre una copia, así que las
    preguntas nuevas nunca se mezclaban → ahora se mezclan de verdad.
- **Validación de esquema (`validar_curso`):** dos pasadas — estructura de cada
  lección + existencia de prereqs, y **detección de ciclos** en el grafo (DFS).
  El CLI ahora rechaza un curso roto con mensaje claro en vez de romperse en runtime.
- **Validación/carga de estado:** `cargar_estado` detecta JSON corrupto o estado con
  campas faltantes y avisa; `guardar_estado` es **atómico** (temp + rename) para no
  dejar el progreso del alumno roto si el proceso muere a mitad.
- **Evaluación enchufable (`EstrategiaEvaluacion`):** hoy `MatcherClaves` (matching
  por claves, igual que F0), pero la firma `evaluar(pregunta, respuesta) -> (acierto,
  confianza, razon)` ya admite un backend LLM semántico como drop-in para la F1.
- **Diagnóstico de placement (`diagnosticar`):** recorre el curso en **orden
  topológico** (respeta prereqs) y hace 1 pregunta por lección; las que el alumno
  ya domina se marcan `bkt=1.0` y desbloquean el resto. Comando nuevo: `tutor.py diagnostico`.
- **Tests (`tests/test_modelo.py`, pytest):** 21 tests cubren BKT, FSRS-lite (again/
  hard/good/easy, techo de intervalo), validación de curso (faltantes, id duplicado,
  prereq inexistente, **ciclo**), matcher, diagnóstico y roundtrip de guardado/carga.

Uso:
```bash
cd motor
python3 -m pytest tests/ -q        # 21 tests verdes
python3 tutor.py diagnostico       # placement adaptativo
python3 tutor.py clase             # próxima lección desbloqueada
python3 tutor.py sesion            # retrieval-first + nuevas mezcladas
python3 tutor.py estado            # maestría por lección + gates
python3 tutor.py demo --dias 6     # simula un alumno
python3 tutor.py reset             # borra progreso (ahora sin crashear)
```

## F1 — Capa LLM pluggable (2026-08-27)

Hace que el tutor deje de ser "app de quiz" y empiece a corregir con criterio
semántico + generar pistas socráticas, **con costo cero y sin cargar la máquina**.

- **`motor/llm.py`:** interfaz `LLMClient` con dos implementaciones:
  - `MockLLMClient` (default): heurística offline sobre teoría+claves del curso
    (filtra stopwords, exige palabras sustantivas ≥4 letras para el solap
    semántico). Cero red, cero recursos.
  - `HTTPLLMClient`: OpenAI-compatible (`/chat/completions`, `response_format`
    json). Cubre Ollama, Groq, OpenAI, Together, etc.
- **Factory `get_client()` por env:** si `TUTOR_LLM` no está seteado → Mock.
  Para usar un modelo real solo se setean env vars (sin tocar código):
  `TUTOR_LLM=http`, `TUTOR_LLM_BASE_URL`, `TUTOR_LLM_MODEL`, `TUTOR_LLM_API_KEY`.
- **`EstrategiaLLM(EstrategiaEvaluacion)`:** usa el cliente para grading
  semántico + pista; **fallback automático al matcher por claves** si la
  llamada HTTP falla (red caída, key inválida, modelo ausente). Nunca mudo.
- **CLI:** default ya usa `EstrategiaLLM`; flags `--matcher` (fuerza claves
  viejas) y `--http` (fuerza backend real) para comparar.

Uso:
```bash
cd motor
python3 -m pytest tests/ -q          # 32 tests verdes

# Default: MockLLM offline (semántico barato, $0, 0 recursos)
python3 tutor.py sesion

# Igual que F0 (solo matching por claves)
python3 tutor.py sesion --matcher

# Con modelo real (requiere Ollama/Groq/OpenAI en env; cae al matcher si falla)
TUTOR_LLM=http TUTOR_LLM_BASE_URL=http://localhost:11434/v1 TUTOR_LLM_MODEL=llama3.1 \
  python3 tutor.py sesion --http
```

## Pendientes hacia F2

- Voz / check-in desktop (loop diario proactivo)
- Empaquetador md→curso: `motor/empaquetar.py` ya existe en el repo (md → curso JSON)
- Métricas de retención y reporte al alumno


