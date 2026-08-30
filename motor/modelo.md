---
tipo: archivo
proyecto: "APP Tutor IA"
ruta: motor/modelo.py
milestone: F0
actualizado: 2026-08-26
---

# modelo.py — cerebro del motor pedagógico

**Ruta:** [[motor/modelo.py]]
**Líneas:** ~433 | **Dependencias:** solo stdlib (json, random, datetime, tempfile)

## Qué hace
Implementa todos los algoritmos de razonamiento pedagógico. Es el corazón del sistema — sin dependencias externas.

## Módulos internos

### BKT — Bayesian Knowledge Tracing
| Función | Qué hace |
|---|---|
| `bkt_actualizar(p, correcto)` | Actualiza P(K) con fórmula bayesiana |
| Constantes | p_init=0.15, T=0.12, S=0.12, G=0.20, umbral_maestria=0.80 |

### FSRS-lite — Spaced Repetition
| Función | Qué hace |
|---|---|
| `tarjeta_nueva()` | Crea tarjeta con ease=2.5, interval=1, lapses=0 |
| `fsrs_lite_programar(tarjeta, grado)` | Recalcula intervalo según grade (0-3) |
| `tarjetas_vencidas(curso, estado)` | Retorna preguntas cuya fecha ya pasó |

### Estado del alumno
| Función | Qué hace |
|---|---|
| `nuevo_estado(alumno)` | Crea estado vacío |
| `cargar_estado()` / `guardar_estado(estado)` | Persistencia JSON atómica |
| `asegurar_concepto(estado, cid)` | Inicializa concepto si no existe |
| `marcar_vista(estado, cid)` | Marca lección como vista |
| `registrar_respuesta(estado, cid, idx, correcto)` | Actualiza BKT + FSRS |

### Navegación de curso
| Función | Qué hace |
|---|---|
| `prereqs_cumplidos(curso, estado, leccion)` | Verifica si se pueden abrir prerrequisitos |
| `leccion_siguiente(curso, estado)` | Siguiente lección no vista con prereqs cumplidos |
| `preguntas_de_leccion(curso, estado, lec)` | Selecciona preguntas mixtas (repaso + nuevas) |

### Evaluación de respuestas
| Función/Clase | Qué hace |
|---|---|
| `MatcherClaves` | Matching por palabras clave (F0) |
| `EstrategiaLLM` | Grading semántico con LLM + fallback (F1) |
| `evaluar_respuesta()` | Wrapper que usa la estrategia activa |
| `diagnosticar()` | Evalúa todas las lecciones con 1 pregunta c/u |

### Utilidades
| Función | Qué hace |
|---|---|
| `validar_curso()` | Valida estructura JSON del curso |
| `validar_estado()` | Valida JSON del estado |
| `orden_topologico()` | Topological sort de prerrequisitos |
| `resumen_alumno()` | Texto formateado del progreso |
| `normalizar(s)` | Lowercase + quitar tildes para matching |

## Notas
- Persistencia: JSON atómico via tempfile + rename (POSIX-safe)
- Sin dependencias externas — ideal para testing
- `EstrategiaLLM` importa `llm.py` de forma lazy para no acoplar
