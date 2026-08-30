---
tipo: archivo
proyecto: "APP Tutor IA"
ruta: motor/empaquetar.py
milestone: F0
actualizado: 2026-08-26
---

# empaquetar.py — convertidor md → JSON de curso

**Ruta:** [[motor/empaquetar.py]]
**Líneas:** ~121 | **Dependencias:** solo stdlib (json, re, unicodedata, pathlib)

## Qué hace
Toma un curso en Markdown y lo convierte a JSON compatible con el motor pedagógico. Permite crear cursos sin tocar código.

## Uso
```bash
python3 empaquetar.py curso.md [salida.json]
```

## Formato Markdown esperado
```markdown
# Curso: Nombre

## c01
**Título:** Título de la lección
**Objetivo:** Qué aprenderá el alumno
**Prerequisitos:** c01, c02

- teoria
- Punto de teoría 1
- Punto de teoría 2
- practica
- Instrucción de práctica
- preguntas
- Pregunta | Respuesta | palabra,clave | pista1,pista2
```

## Bloques soportados
| Bloque | Contenido |
|---|---|
| `teoria` | Lista de bullet points con conceptos |
| `practica` | Texto libre con instrucción de práctica |
| `preguntas` | Formato pipe: `q \| a \| claves \| pistas` |

## Validación
- Título obligatorio por lección
- Al menos 1 pregunta por lección (warning si falta)
- Prerequisitos deben existir como IDs de lección

## Notas
- Normaliza acentos para matching (`unicodedata.normalize`)
- Maneja `**bold**` markdown stripping
- Bloques marcados con `- teoria`, `- practica`, `- preguntas` (con guion)
