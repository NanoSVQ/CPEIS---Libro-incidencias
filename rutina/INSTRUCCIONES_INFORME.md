# Rutina diaria · Informe narrativo del libro de incidencias

*Herramienta personal · no oficial.* Este archivo es la guía que sigue Claude cada mañana. La tarea programada solo tiene que decir: **«Sigue las instrucciones de rutina/INSTRUCCIONES_INFORME.md»**.

## Qué hay que hacer (en este orden)

1. Comprueba que existen las variables de entorno `LIBRO_URL` y `LIBRO_TOKEN` (sin mostrar su valor). Si falta alguna, detente y explica qué falta.
2. Lee las anotaciones:
   ```bash
   python3 rutina/leer_anotaciones.py anotaciones.json
   ```
   El script imprime las anotaciones agrupadas por guardia y crea `anotaciones.json`. Cada anotación trae `fecha`, `dia`, `guardia_texto`, `bombero` (puede ser `null`) y `texto`.
3. Escribe el informe en `informe.md` siguiendo las reglas de abajo.
4. Publícalo:
   ```bash
   python3 rutina/publicar_informe.py informe.md anotaciones.json
   ```
5. Termina con un resumen de una línea: cuántas anotaciones se leyeron y si el informe se publicó.

No hagas commits ni cambies archivos del repositorio. `anotaciones.json` e `informe.md` son temporales. Si un paso falla, no inventes el informe: explica el error.

## Para quién es

Para el personal que entra de guardia y para el jefe de dotación. Tienen que poder leerlo en dos minutos y saber qué ha pasado en el parque en los últimos 15 días, sobre todo **qué sigue abierto** y **qué avisos hay que tener presentes**.

## Cómo escribirlo

- En **español**, en tercera persona, con un tono sobrio y profesional, como un parte de relevo.
- **En forma de relato, no como una lista copiada.** Une las anotaciones que tratan del mismo asunto (el mismo vehículo, la misma instalación, el mismo proveedor, el mismo material) en un solo párrafo que cuente la historia completa, de principio a fin.
- **Sitúa los hechos en su guardia**, con el día de la semana y la fecha: «En la guardia del viernes 30 de octubre…». Usa `guardia_texto`. Las anotaciones de madrugada ya vienen asignadas a la guardia del día anterior. Para la guardia en curso o la anterior puedes decir «en la pasada guardia» si queda claro.
- **Nombra a quien comunica** con el nombre tal como viene en `bombero` (normalmente el APODO, en mayúsculas): «el bombero ROSADO comunica…». Si `bombero` es `null`, no inventes a nadie: «se comunica…», «queda anotado…».
- **No inventes nada.** No añadas causas, cargos, matrículas, empresas ni resultados que no aparezcan en las anotaciones. Si algo no se sabe (por ejemplo, si un vehículo ya volvió), dilo: «no consta su regreso».
- **Conserva los datos concretos tal cual**: matrículas, indicativos de vehículos, nombres de empresas, ubicaciones y cifras.
- Un asunto se considera **cerrado** solo si una anotación posterior lo resuelve. Si no, va a «Asuntos abiertos».
- Las **instrucciones que deben seguirse siempre** («el interruptor debe quedar apagado tras su uso», «no usar la toma X») van en «Avisos vigentes», aunque sean antiguas dentro del periodo.
- Extensión orientativa: 150–600 palabras, según la cantidad de anotaciones. Si no hay ninguna, el informe es una sola frase: «No constan anotaciones en el libro entre el … y el …».

## Formato (Markdown sencillo)

La app solo interpreta: títulos con `## `, viñetas con `- `, **negrita** con `**…**` y párrafos separados por una línea en blanco. No uses tablas, enlaces ni otros elementos.

Estructura (omite cualquier sección que quede vacía):

```markdown
## Resumen
Dos o tres frases con lo más importante de la quincena.

## Asuntos abiertos
- Asunto pendiente, desde qué guardia y qué falta.

## Avisos vigentes
- Instrucción que debe seguirse siempre y desde cuándo.

## Vehículos
Relato agrupado por vehículo.

## Instalaciones y mantenimiento
…

## Material y equipos
…

## Personal y servicio
…

## Otras comunicaciones
…
```

Dentro de cada sección, cuenta los hechos en orden cronológico.

## Ejemplos de estilo

Anotaciones de partida (ejemplo):

> [24/10 09:10] FALCON: Hnos. Domínguez recogen el 3211-FWH (BUL) para pasar la ITV.
> [27/10 18:40] GIL: Traen de vuelta el BUL 3211-FWH, ITV pasada.

Relato esperado:

> El vehículo **3211-FWH (BUL)** fue recogido por Hnos. Domínguez en la guardia del sábado 24 de octubre para pasar la ITV y fue devuelto al parque en la guardia del martes 27, con la ITV superada (comunicado por FALCON y GIL).

Otro ejemplo:

> [30/10 11:20] ROSADO: Por el traslado del servicio de fontanería del Ayto., la bomba del parque debe quedar siempre con el interruptor apagado después de usarla.

Relato esperado, en «Avisos vigentes»:

> - En la guardia del viernes 30 de octubre, el bombero ROSADO comunica una incidencia en la bomba del parque a raíz del traslado del servicio de fontanería del Ayuntamiento: **el interruptor debe quedar siempre apagado tras su uso**.
