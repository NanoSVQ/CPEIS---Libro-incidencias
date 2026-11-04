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

Uso:  python3 rutina/leer_anotaciones.py [salida.json]
Solo usa la biblioteca estándar de Python 3.9+.
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

ZONA = ZoneInfo("Europe/Madrid")
DIAS_SEMANA = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def texto_dia(d):
    return f"{DIAS_SEMANA[d.weekday()]} {d.day} de {MESES[d.month - 1]}"


def main():
    url = os.environ.get("LIBRO_URL", "").strip()
    token = os.environ.get("LIBRO_TOKEN", "").strip()
    if not url or not token:
        sys.exit("ERROR: faltan las variables de entorno LIBRO_URL y/o LIBRO_TOKEN.")
    dias = int(os.environ.get("LIBRO_DIAS", "15"))
    inicio_guardia = int(os.environ.get("LIBRO_INICIO_GUARDIA", "8"))
    salida = sys.argv[1] if len(sys.argv) > 1 else "anotaciones.json"

    ahora = datetime.now(ZONA)
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
    except Exception as e:  # noqa: BLE001
        sys.exit(f"ERROR al conectar con Apps Script: {e}\n"
                 "Comprueba LIBRO_URL y que el entorno permite acceder a script.google.com "
                 "y script.googleusercontent.com.")
    if not datos.get("ok"):
        sys.exit(f"ERROR del servidor: {datos.get('error')}")

    anotaciones = []
    for r in datos.get("registros", []):
        ts = r.get("ts") or 0
        if ts:
            momento = datetime.fromtimestamp(ts / 1000, ZONA)
        else:  # fila escrita a mano en la hoja con formato dd/mm/aaaa hh:mm
            try:
                momento = datetime.strptime(r.get("fecha", ""), "%d/%m/%Y %H:%M").replace(tzinfo=ZONA)
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
            "_ts": momento.timestamp(),
        })
    anotaciones.sort(key=lambda a: a["_ts"])
    for a in anotaciones:
        a.pop("_ts")

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
