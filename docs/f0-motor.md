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

## Pendientes hacia F1

- Corrección semántica con LLM (hoy: matching por claves; la interfaz ya está lista)
- Popup/check-in desktop (F1) y voz (F2)
- Empaquetador md→curso: `motor/empaquetar.py` ya existe en el repo (md → curso JSON)

