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

## Pendientes hacia F1

- Corrección semántica con LLM (hoy: matching por claves)
- Popup/check-in desktop (F1) y voz (F2)
- Empaquetador md→curso (cargar cursos nuevos sin editar JSON a mano)
