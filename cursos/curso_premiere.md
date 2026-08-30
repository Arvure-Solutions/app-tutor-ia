---
tipo: archivo
proyecto: "APP Tutor IA"
ruta: cursos/biodescodificacion.json
milestone: F0
actualizado: 2026-08-26
---

# curso_premiere.json — curso empaquetado de Premiere Pro

**Ruta:** [[cursos/biodescodificacion.json]]
**Formato:** JSON (generado por empaquetar.py)
**Lecciones:** 11 (c01–c11)
**Nivel:** principiante → intermedio

## Qué es
Curso completo de edición en Premiere Pro, empaquetado para el motor pedagógico. Cubre desde interfaz hasta multicam + colour grading.

## Estructura del JSON
```json
{
  "curso": "Premiere Pro desde cero",
  "nivel": "principiante-intermedio",
  "lecciones": [
    {
      "id": "c01",
      "titulo": "...",
      "objetivo": "...",
      "prereqs": [],
      "teoria": ["...", "..."],
      "practica": "...",
      "preguntas": [{"q": "...", "a": "...", "claves": [...], "pistas": [...]}]
    }
  ]
}
```

## Lecciones
| ID | Título | Prereqs |
|---|---|---|
| c01 | Interfaz y flujo de trabajo | — |
| c02 | Importación y organización | c01 |
| c03 | Timeline y ediciones básicas | c02 |
| c04 | Transiciones y efectos | c03 |
| c05 | Títulos y Essential Graphics | c04 |
| c06 | Audio: limpieza y mezcla | c05 |
| c07 | Corrección de color Lumetri | c06 |
| c08 |-keyframes y animación | c07 |
| c09 | Secuencias multicam | c08 |
| c10 | Exportación y configuración | c09 |
| c11 | Flujo completo: proyecto corto | c10 |

## Generado desde
`cursos/curso_premiere.md` → `motor/empaquetar.py` → `cursos/curso_premiere.json`
