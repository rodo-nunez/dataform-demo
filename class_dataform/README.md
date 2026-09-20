# Clase: Dataform — SQL con superpoderes

Slides (revealJS, tema oscuro) para la **Intro + Parte 1** del stream de en_coders sobre Dataform
(primeros ~50 min), más las láminas de puente hacia la demo (Parte 2), la pausa de memes y el cierre.
El código de los ejemplos sale del repo `dataform-demo`.

## Cómo renderizar

```bash
# Requiere Quarto (>= 1.5). No necesita Python, R ni LaTeX.
quarto render slides_dataform.qmd      # genera slides_dataform.html (autocontenido)
quarto preview slides_dataform.qmd     # modo desarrollo con recarga
```

El `.html` ya viene renderizado en el zip: se abre directo en el navegador.

## Atajos durante el stream

| Tecla | Qué hace |
|---|---|
| `→` / `espacio` | Avanza (cada fila de código aparece de a una) |
| `S` | Abre la **vista del orador** con las notas (guion, tiempos, cues de pizarra) |
| `Esc` | Vista general: sirve para **saltar el bonus dbt** si no hay tiempo |
| `F` | Pantalla completa |

## Estructura del paquete

- `slides_dataform.qmd` — presentación (fuente)
- `slides_dataform.html` — presentación renderizada
- `assets/` — logo de en_coders, tema (`custom.scss`) y diagramas SVG (stack, ciclo de vida, DAG real del proyecto)

## Guion de tiempos (aprox.)

| Minuto | Bloque |
|---|---|
| 0–10 | Warm-up (charla libre, **fuera** de las slides) |
| 10–15 | Intro: el caso y el dolor |
| 15–25 | Qué es Dataform y su vocabulario; qué le falta a SQL puro |
| 25–50 | Features: `ref()`, `config`, assertions, incrementales, JavaScript, tags/workflows, Git |
| 50–55 | Pros y contras |
| 55–60 | Bonus dbt (solo si sobra tiempo; si no, saltar) |
| ~60 | ☕ Pausa de memes |
| 65–110 | Parte 2: demo (guion en `docs/demo-runbook.md` del repo) |
| 110–120 | Cierre |

Los cues `PIZARRA:` y `MEME:` están en las notas del orador (tecla `S`).

## Antes del stream

1. Publicar el repo `dataform-demo` (hoy privado) y confirmar el link de las últimas slides.
2. Comparar las cifras de la slide "Lo que pasa cuando llega el batch 2" (4 037 → 6 186 filas; 187 snapshots) con tu corrida real.
3. Revisar las afirmaciones que las notas marcan como "verifica" (por ejemplo, los snapshots tipo dbt).
4. El bloque dbt es **ilustrativo**: no está en el repo ni se ejecutó.
5. Si prefieres un meme con imagen, reemplaza el panel de la slide "El meme".
