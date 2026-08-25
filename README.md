# APP Tutor IA

> **Tutor que no te deja solo al día siguiente.** Loop diario proactivo, check-ins de voz,
> visión de pantalla opt-in ("por ahí no es") y un motor pedagógico real:
> memoria persistente + knowledge tracing + repetición espaciada FSRS + método socrático.

## Documentos

| Doc | Contenido |
|---|---|
| [`docs/propuesta.md`](docs/propuesta.md) | ⭐ Propuesta completa: problema validado, los 7 módulos del motor pedagógico, arquitectura, roadmap F0–F4 |
| [`docs/investigacion/github-repos.md`](docs/investigacion/github-repos.md) | ~16 repos open-source analizados (pacer-ai, mind-mentor, onevision…) |
| [`docs/investigacion/comunidad-usuarios.md`](docs/investigacion/comunidad-usuarios.md) | Voz real Reddit/X: dolores, features pedidas, competidores |
| [`docs/investigacion/youtube-videos.md`](docs/investigacion/youtube-videos.md) | 6 videos con transcripciones analizadas |
| [`docs/investigacion/plataformas-pedagogia.md`](docs/investigacion/plataformas-pedagogia.md) | Frappe Learning como base + 10 conceptos pedagógicos traducidos a features |

## Estado

🚧 **F0 funcional** (2026-08-25): motor pedagógico CLI con curso piloto de Premiere Pro.

```bash
cd motor
python3 tutor.py clase    # próxima lección desbloqueada
python3 tutor.py sesion   # sesión retrieval-first (repasos FSRS + nuevas)
python3 tutor.py estado   # maestría por lección
```

Próximo paso: **F1** — popups/check-ins desktop + empaquetador md→curso.
