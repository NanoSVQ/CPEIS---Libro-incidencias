#!/usr/bin/env python3
"""
Libro de incidencias · Rutina diaria de informe (paso 3: publicar)
Herramienta personal · no oficial

Envía el informe narrativo (archivo Markdown) a la aplicación web de Apps
Script, que lo guarda como una fila nueva en la pestaña "Informes" de la hoja.
La app lo muestra en la pestaña Informe.

Variables de entorno: LIBRO_URL y LIBRO_TOKEN (las mismas que leer_anotaciones.py).

Uso:  python3 rutina/publicar_informe.py informe.md [anotaciones.json]
"""
import json
import os
import sys
import urllib.request


def main():
    url = os.environ.get("LIBRO_URL", "").strip()
    token = os.environ.get("LIBRO_TOKEN", "").strip()
    if not url or not token:
        sys.exit("ERROR: faltan las variables de entorno LIBRO_URL y/o LIBRO_TOKEN.")
    if len(sys.argv) < 2:
        sys.exit("Uso: python3 rutina/publicar_informe.py informe.md [anotaciones.json]")

    with open(sys.argv[1], encoding="utf-8") as f:
        texto = f.read().strip()
    if not texto:
        sys.exit("ERROR: el informe está vacío.")
    meta_path = sys.argv[2] if len(sys.argv) > 2 else "anotaciones.json"
    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)

    cuerpo = json.dumps({
        "token": token,
        "accion": "informe",
        "desde": meta["desde"],
        "hasta": meta["hasta"],
        "anotaciones": meta.get("total", 0),
        "autor": "Claude · rutina diaria",
        "texto": texto,
    }).encode("utf-8")
    # Cuerpo como texto plano: Apps Script responde con una redirección 302 que
    # urllib sigue como GET, que es justo lo que espera Google.
    req = urllib.request.Request(url, data=cuerpo, method="POST",
                                 headers={"Content-Type": "text/plain;charset=utf-8",
                                          "User-Agent": "libro-incidencias-rutina"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            res = json.loads(r.read().decode("utf-8"))
    except Exception as e:  # noqa: BLE001
        sys.exit(f"ERROR al publicar: {e}")
    if not res.get("ok"):
        sys.exit(f"ERROR del servidor: {res.get('error')}")
    print(f"Informe publicado (fila {res.get('fila')} de la pestaña Informes).")


if __name__ == "__main__":
    main()
