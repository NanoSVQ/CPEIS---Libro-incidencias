#!/usr/bin/env python3
"""
Libro de incidencias · Rutina diaria de informe (paso 1: leer)
Herramienta personal · no oficial

Descarga las anotaciones de los últimos N días (15 por defecto) desde la
aplicación web de Apps Script y las guarda en anotaciones.json, ordenadas de
la más antigua a la más reciente, con la "guardia" a la que pertenece cada una.

Necesita dos variables de entorno (NUNCA las escribas en el repositorio):
  LIBRO_URL    URL de la aplicación web de Apps Script (termina en /exec)
  LIBRO_TOKEN  el mismo TOKEN que hay en Code.gs

Opcionales:
  LIBRO_DIAS            días a leer (15)
  LIBRO_INICIO_GUARDIA  hora en que empieza la guardia, 0-23 (8)

Uso:  python3 rutina/leer_anotaciones.py [salida.json]   (por defecto /tmp/libro/anotaciones.json,
      fuera del repositorio, para no dejar archivos con datos reales en git)
Solo usa la biblioteca estándar de Python 3.9+.
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone


def _zona_madrid():
    """Europe/Madrid. Si el sistema no tiene base de zonas horarias, aplica la regla UE a mano."""
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo("Europe/Madrid")
    except Exception:  # noqa: BLE001
        return None


def _ultimo_domingo(anio, mes):
    d = datetime(anio, mes + 1, 1) - timedelta(days=1) if mes < 12 else datetime(anio, 12, 31)
    return d - timedelta(days=(d.weekday() + 1) % 7)


def _offset_madrid(utc):
    """Desfase de Madrid para un instante UTC: +2 h en verano (último domingo de marzo a último de octubre, 01:00 UTC)."""
    ini = _ultimo_domingo(utc.year, 3).replace(hour=1)
    fin = _ultimo_domingo(utc.year, 10).replace(hour=1)
    return timedelta(hours=2) if ini <= utc.replace(tzinfo=None) < fin else timedelta(hours=1)


_ZI = _zona_madrid()


def a_madrid(ts_segundos=None):
    """Convierte un instante (segundos epoch, o ahora) a fecha/hora de Madrid."""
    utc = datetime.fromtimestamp(ts_segundos, timezone.utc) if ts_segundos is not None else datetime.now(timezone.utc)
    if _ZI is not None:
        return utc.astimezone(_ZI)
    return utc.astimezone(timezone(_offset_madrid(utc)))
DIAS_SEMANA = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def texto_dia(d):
    return f"{DIAS_SEMANA[d.weekday()]} {d.day} de {MESES[d.month - 1]}"


def main():
    url = os.environ.get("LIBRO_URL", "").strip()
    token = os.environ.get("LIBRO_TOKEN", "").strip()
    faltan = [n for n, v in (("LIBRO_URL", url), ("LIBRO_TOKEN", token)) if not v]
    if faltan:
        sys.exit("ERROR: faltan variables de entorno: " + ", ".join(faltan) +
                 ". Defínelas en el entorno de Claude Code (Environment variables).")
    if not url.endswith("/exec"):
        sys.exit("ERROR: LIBRO_URL debe terminar en /exec.")
    dias = int(os.environ.get("LIBRO_DIAS", "15"))
    inicio_guardia = int(os.environ.get("LIBRO_INICIO_GUARDIA", "8"))
    salida = sys.argv[1] if len(sys.argv) > 1 else "/tmp/libro/anotaciones.json"
    os.makedirs(os.path.dirname(os.path.abspath(salida)), exist_ok=True)

    ahora = a_madrid()
    hasta = ahora.date()
    desde = hasta - timedelta(days=dias - 1)

    qs = urllib.parse.urlencode({
        "action": "rango", "token": token,
        "desde": desde.isoformat(), "hasta": hasta.isoformat(),
    })
    req = urllib.request.Request(url + ("&" if "?" in url else "?") + qs,
                                 headers={"User-Agent": "libro-incidencias-rutina"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            datos = json.loads(r.read().decode("utf-8"))
    except json.JSONDecodeError:
        sys.exit("ERROR: la respuesta no es JSON. Revisa que la implementación tenga acceso "
                 "'Cualquier usuario' y que LIBRO_URL sea la URL /exec.")
    except Exception as e:  # noqa: BLE001
        sys.exit(f"ERROR al conectar con Apps Script: {e}\n"
                 "Comprueba LIBRO_URL y que el entorno permite acceder a script.google.com "
                 "y script.googleusercontent.com.")
    if not datos.get("ok"):
        err = datos.get("error")
        pista = {"token": " (LIBRO_TOKEN no coincide con el TOKEN de Code.gs)",
                 "accion desconocida": " (publica la versión nueva de Code.gs)"}.get(err, "")
        sys.exit(f"ERROR del servidor: {err}{pista}")

    anotaciones = []
    for r in datos.get("registros", []):
        ts = r.get("ts") or 0
        if ts:
            momento = a_madrid(ts / 1000)
        else:  # fila escrita a mano en la hoja con formato dd/mm/aaaa hh:mm (ya en hora de Madrid)
            try:
                momento = datetime.strptime(r.get("fecha", ""), "%d/%m/%Y %H:%M")
            except ValueError:
                continue
        # Una anotación de madrugada (antes del inicio de guardia) pertenece a la guardia del día anterior.
        guardia = momento.date() if momento.hour >= inicio_guardia else momento.date() - timedelta(days=1)
        anotaciones.append({
            "fecha": momento.strftime("%d/%m/%Y %H:%M"),
            "dia": texto_dia(momento.date()),
            "guardia": guardia.isoformat(),
            "guardia_texto": "guardia del " + texto_dia(guardia),
            "bombero": (r.get("bombero") or "").strip() or None,
            "texto": (r.get("texto") or "").strip(),
            "_orden": momento.strftime("%Y%m%d%H%M"),
        })
    anotaciones.sort(key=lambda a: a["_orden"])
    for a in anotaciones:
        a.pop("_orden")

    resultado = {
        "generado": ahora.strftime("%d/%m/%Y %H:%M"),
        "hoy": texto_dia(hasta),
        "desde": desde.isoformat(),
        "hasta": hasta.isoformat(),
        "inicio_guardia": f"{inicio_guardia:02d}:00",
        "total": len(anotaciones),
        "anotaciones": anotaciones,
    }
    with open(salida, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f"{len(anotaciones)} anotaciones del {desde:%d/%m/%Y} al {hasta:%d/%m/%Y} → {salida}")
    guardia_actual = None
    for a in anotaciones:
        if a["guardia"] != guardia_actual:
            guardia_actual = a["guardia"]
            print(f"\n## {a['guardia_texto']}")
        print(f"- [{a['fecha']}] {a['bombero'] or '(sin indicar)'}: {a['texto']}")


if __name__ == "__main__":
    main()
