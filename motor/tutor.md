---
tipo: archivo
proyecto: "APP Tutor IA"
ruta: motor/tutor.py
milestone: F0
actualizado: 2026-08-26
---

# tutor.py — CLI principal del motor pedagógico

**Ruta:** [[motor/tutor.py]]
**Líneas:** ~277 | **Dependencias:** modelo.py, sesion.py | **Stdlib only:** sí

## Qué hace
Interfaz de línea de comandos para interactuar con el motor pedagógico. Punto de entrada único para el usuario.

## Subcommands
| Comando | Qué hace |
|---|---|
| `estado` | Muestra progreso, lecciones, maestría, repasos vencidos |
| `clase` | Presenta una lección (teoría + práctica) y la marca como vista |
| `sesion` | Sesión retrieval-first: repasos vencidos primero, luego nuevas |
| `repaso` | Solo repasos de preguntas vencidas |
| `diagnostico` | Evalúa todas las lecciones vistas con 1 pregunta cada una |
| `demo` | Simula N días de progreso con respuestas aleatorias |
| `reset` | Borra el estado del alumno |

## Subcommands nuevos (F1)
| Comando | Qué hace |
|---|---|
| `loop` | Loop proactivo: briefing → sesión → check-in voz → reporte |
| `--curso` | Carga cualquier JSON de curso empaquetado |
| `--hablar` | Activa feedback de voz en loop |

## Arquitectura interna
```
main() → args → cmd_*() → modelo.funciones()
                            └→ evaluar_respuesta() → MatcherClaves | EstrategiaLLM
                            └→ registrar_respuesta() → BKT update + FSRS schedule
                            └→ guardar_estado() → JSON atómico
```

## Estados del curso
- Cada curso tiene su propio archivo `estado_{nombre}.json`
- Seleccionado vía `--curso` o default `curso_premiere.json`

## Notas
- Importa `modelo` y `sesion` como módulos separados
- `EstrategiaLLM` (en modelo.py) es el F1 para grading semántico
