# Configurar la rutina diaria del informe narrativo

*Herramienta personal · no oficial · versión 20261104.5*

Esta guía deja funcionando una **rutina de Claude Code** (tarea programada en la nube) que cada mañana:

1. lee de tu hoja de Google las anotaciones de los últimos 15 días,
2. redacta un informe en forma de relato,
3. lo guarda en la pestaña **Informes** de la hoja, desde donde la app lo muestra en la pestaña **Informe**.

La rutina **no necesita acceso a tu cuenta de Google**. Usa la misma URL `/exec` y el mismo token que la app del móvil.

Tiempo estimado: 20–30 minutos.

---

## 0. Antes de empezar

Necesitas:

- [ ] Un plan de Claude **Pro, Max, Team o Enterprise** con **Claude Code en la web** activo (entra en <https://claude.ai/code>; si te pide conectar GitHub, hazlo).
- [ ] La **URL `/exec`** de tu Apps Script y tu **TOKEN** (los mismos que pusiste en la app).
- [ ] Acceso al repositorio `NanoSVQ/CPEIS---Libro-incidencias` en GitHub.

---

## 1. Actualizar el script de Google (Code.gs 20261104.5)

1. Abre la hoja → **Extensiones → Apps Script**.
2. Selecciona todo el contenido de `Código.gs` y bórralo. Pega el `Code.gs` nuevo.
3. **Vuelve a poner tu token** en la línea `const TOKEN = '…';` (el nuevo archivo trae `CAMBIA-ESTE-TOKEN`). Guarda (💾).
4. En el desplegable de funciones elige **`configurar`** → **▶ Ejecutar**. Si pide permisos, acéptalos como la primera vez. En el registro debe aparecer `Hoja lista…`. Ahora la hoja tiene una pestaña nueva, **Informes**.
5. **Implementar → Gestionar implementaciones** → lápiz ✏️ → **Versión: Nueva versión** → **Implementar**. La URL `/exec` no cambia.
6. Comprobación: abre en el navegador
   `TU_URL_EXEC?action=informe&token=TU_TOKEN`
   Debe responder `{"ok":true,"informe":null}` (todavía no hay informes).
   Si responde `"accion desconocida"`, no se publicó la nueva versión: repite el paso 5.

---

## 2. Subir la carpeta `rutina` al repositorio

La carpeta contiene 4 archivos, ninguno con secretos:

| Archivo | Para qué sirve |
|---|---|
| `rutina/leer_anotaciones.py` | Descarga las anotaciones de los últimos 15 días y crea `anotaciones.json`, con la guardia de cada una |
| `rutina/publicar_informe.py` | Envía el informe redactado a la hoja (pestaña Informes) |
| `rutina/INSTRUCCIONES_INFORME.md` | La guía de estilo que sigue Claude para redactar el relato |
| `rutina/CONFIGURAR_RUTINA.md` | Esta guía |

**Desde el ordenador (Chrome o Edge):**

1. Descomprime `libro-incidencias.zip`.
2. Abre `https://github.com/NanoSVQ/CPEIS---Libro-incidencias`.
3. **Add file → Upload files**.
4. Arrastra la **carpeta `rutina` completa** (la carpeta, no los archivos sueltos) a la zona de subida. GitHub mantiene la carpeta.
5. Abajo: mensaje `Añadir rutina de informe` → **Commit changes**.
6. Comprueba que en el repositorio aparece la carpeta `rutina` con los 4 archivos dentro.

**Si no puedes arrastrar la carpeta:** pulsa **Add file → Create new file**, escribe como nombre `rutina/leer_anotaciones.py` (al escribir la `/` se crea la carpeta), pega el contenido del archivo y pulsa **Commit changes**. Repite con los otros tres.

> No subas `Code.gs` (lleva tu token). Tampoco subas nunca `anotaciones.json` ni `informe.md` si algún día aparecen: son temporales y contienen anotaciones.

---

## 3. Crear el entorno en Claude Code

Un **entorno** define a qué puede conectarse la rutina y qué variables tiene. Crea uno exclusivo para esta rutina.

1. Ve a <https://claude.ai/code>.
2. Encima del cuadro de texto pulsa el **nombre del entorno** (normalmente pone *Default*) → **Add cloud environment**.
3. Rellena el formulario:

   **Name**
   ```
   libro-incidencias
   ```

   **Network access:** elige **Custom**.
   En **Allowed domains** escribe un dominio por línea:
   ```
   script.google.com
   script.googleusercontent.com
   ```
   Marca **Also include default list of common package managers**. No es imprescindible, pero evita problemas si Claude necesita instalar algo.

   > ¿Por qué dos dominios? Apps Script recibe la petición en `script.google.com` y devuelve la respuesta desde `script.googleusercontent.com`. Si falta el segundo, la lectura falla.

   **Environment variables** (formato `.env`, una por línea, sin comillas y sin espacios alrededor del `=`):
   ```
   LIBRO_URL=https://script.google.com/macros/s/AKfycb…TU_ID…/exec
   LIBRO_TOKEN=tu-token-exacto
   LIBRO_INICIO_GUARDIA=8
   LIBRO_DIAS=15
   ```
   - `LIBRO_INICIO_GUARDIA`: hora (0–23) en que empieza la guardia. Con `8`, una anotación de las 03:00 del sábado cuenta como «guardia del viernes».
   - `LIBRO_DIAS`: días que abarca el informe.
   - Si tu token contiene `#`, escríbelo entre comillas: `LIBRO_TOKEN="ab#cd"`.

   > Las variables de entorno las puede ver cualquiera que use ese entorno. Como el entorno es tuyo y personal, solo las ves tú. **No las pongas nunca en el repositorio ni en el texto de la rutina.** Las «Network secrets» de Claude Code no sirven aquí, porque el token viaja dentro de la petición y no en una cabecera.

   **Setup script:** déjalo vacío. Los scripts solo usan Python 3, que ya viene instalado.

4. Pulsa **Create environment**.

---

## 4. Probar el entorno a mano (antes de programar nada)

1. En <https://claude.ai/code>, elige el repositorio **CPEIS---Libro-incidencias** y el entorno **libro-incidencias**.
2. Escribe esta instrucción y envíala:
   ```
   Ejecuta: python3 rutina/leer_anotaciones.py anotaciones.json
   y después: python3 rutina/publicar_informe.py rutina/INSTRUCCIONES_INFORME.md anotaciones.json --simular
   No modifiques nada ni hagas commits. Dime solo el resultado de los dos comandos.
   ```
3. Resultado esperado:
   - El primer comando dice `N anotaciones del dd/mm/aaaa al dd/mm/aaaa → anotaciones.json` y lista las anotaciones agrupadas por guardia.
   - El segundo dice `[SIMULACIÓN] Se publicaría un informe…`. No publica nada.

**Si sale un error:**

| Mensaje | Qué hacer |
|---|---|
| `faltan variables de entorno: LIBRO_URL…` | Revisa el paso 3 (nombres exactos, en mayúsculas). Abre una sesión **nueva** tras editar el entorno. |
| `LIBRO_URL debe terminar en /exec` | Has copiado la URL de edición, no la de la implementación. Cópiala de *Implementar → Gestionar implementaciones*. |
| `ERROR al conectar… 403` / `Tunnel connection failed` / `Forbidden` | Falta algún dominio en **Allowed domains** (sobre todo `script.googleusercontent.com`) o el acceso no es **Custom**. |
| `token (LIBRO_TOKEN no coincide…)` | El token del entorno no es igual al de `Code.gs`. |
| `accion desconocida` | No se publicó la nueva versión del script (paso 1.5). |
| `la respuesta no es JSON` | La implementación no tiene acceso **Cualquier usuario**. |

---

## 5. Crear la rutina programada

1. Ve a <https://claude.ai/code/routines> → **New routine**.
2. **Name**
   ```
   Informe diario libro de incidencias
   ```
3. **Prompt.** Copia este texto tal cual:
   ```
   Eres la rutina diaria del "Libro de incidencias del parque" (herramienta personal, no oficial).
   Trabajas en el repositorio CPEIS---Libro-incidencias.

   Sigue al pie de la letra las instrucciones de rutina/INSTRUCCIONES_INFORME.md:
   1. Ejecuta python3 rutina/leer_anotaciones.py anotaciones.json
   2. Lee anotaciones.json y redacta el informe narrativo en informe.md con el estilo, la estructura y las reglas de ese archivo.
   3. Comprueba con python3 rutina/publicar_informe.py informe.md anotaciones.json --simular
   4. Publica con python3 rutina/publicar_informe.py informe.md anotaciones.json

   Reglas: no inventes datos que no estén en las anotaciones; no muestres el valor de LIBRO_TOKEN ni de LIBRO_URL;
   no modifiques archivos del repositorio, no hagas commits ni abras pull requests.
   Si algún paso falla, no publiques nada y explica el error en una frase.
   Termina con una línea: "Informe publicado: N anotaciones, periodo dd/mm–dd/mm" o el error.
   ```
4. **Repositories:** añade `NanoSVQ/CPEIS---Libro-incidencias`. Deja **desactivado** cualquier permiso para subir ramas: la rutina no necesita escribir en GitHub.
5. **Environment:** elige **libro-incidencias** (el del paso 3).
6. **Connectors:** quita todos. No hacen falta.
7. **Select a trigger → Schedule → Daily**, hora **07:45**.
   - El formulario usa la **zona horaria de tu dispositivo**. Si tu móvil u ordenador está en hora de España, pon 07:45. Si está en otra zona, convierte la hora; con el cambio de hora la diferencia puede variar una hora en algunas semanas del año. Si quieres fijarla en hora de Madrid sea cual sea la zona de tu dispositivo, pídeselo a Claude Code: «cambia la rutina "Informe diario libro de incidencias" para que se ejecute a las 07:45 hora de Madrid» (o, en la terminal, `/schedule update`).
   - Las rutinas pueden arrancar unos minutos después de la hora fijada. Con 07:45 el informe suele estar listo antes de las 08:00.
8. Pulsa **Create**.

---

## 6. Primera ejecución y comprobación

1. Abre la rutina en <https://claude.ai/code/routines> y pulsa **Run now**.
2. Se abre una sesión: verás a Claude ejecutar los comandos y redactar el informe. Al final debe decir `Informe publicado: …`.
3. Comprueba:
   - En la hoja, pestaña **Informes**: una fila nueva con fecha, periodo, texto, número de anotaciones y autor `Claude · rutina diaria`.
   - En la app: pestaña **Informe → Actualizar**. Arriba aparece el relato con «Generado el …».
4. Al día siguiente, comprueba que se ha generado solo.

---

## 7. Mantenimiento

- **Cambiar el estilo del informe:** edita `rutina/INSTRUCCIONES_INFORME.md` en GitHub (lápiz ✏️ → *Commit changes*). La siguiente ejecución ya lo usa.
- **Cambiar la hora de inicio de la guardia o los días del informe:** edita las variables del entorno (paso 3). No hay que tocar la rutina.
- **Cambiar el token:** cámbialo en `Code.gs` (y publica una nueva versión), en la app de cada móvil y en `LIBRO_TOKEN` del entorno.
- **Pausar la rutina:** en su página de detalle, desactívala. La app avisará de que el informe tiene más de un día.
- **Histórico:** cada ejecución añade una fila a **Informes**. La app muestra siempre el más reciente. Puedes borrar filas antiguas de esa pestaña sin problema.
- **Consumo:** cada ejecución es una sesión de Claude Code y cuenta para el uso de tu plan.
