from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
import json, base64, mimetypes, datetime, shutil, os

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "ganado.json"
PHOTOS = ROOT / "fotos"
BACKUPS = ROOT / "respaldos"
PHOTOS.mkdir(exist_ok=True)
BACKUPS.mkdir(exist_ok=True)

DEFAULT = {
    "animals": [],
    "health": [],
    "reproduction": [],
    "inventory": [],
    "milk": [],
    "finances": [],
    "settings": {"farmName": "Mi finca ganadera"}
}

def load_data():
    if not DATA.exists():
        save_data(DEFAULT)
    try:
        obj = json.loads(DATA.read_text(encoding="utf-8"))
        for k, v in DEFAULT.items():
            obj.setdefault(k, v.copy() if isinstance(v, (list, dict)) else v)
        return obj
    except Exception:
        return DEFAULT.copy()

def save_data(obj):
    if DATA.exists():
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        try:
            shutil.copy2(DATA, BACKUPS / f"ganado-{stamp}.json")
        except Exception:
            pass
    tmp = DATA.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(DATA)

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_json(self, obj, status=200):
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/data":
            return self.send_json(load_data())
        if path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", "0"))
        if length > 30 * 1024 * 1024:
            return self.send_json({"ok": False, "error": "Archivo demasiado grande (máximo 30 MB)."}, 413)
        try:
            body = self.rfile.read(length)
            obj = json.loads(body.decode("utf-8"))
            if path == "/api/data":
                allowed = set(DEFAULT.keys())
                if not isinstance(obj, dict) or not all(k in allowed for k in obj):
                    return self.send_json({"ok": False, "error": "Estructura de datos no válida."}, 400)
                save_data(obj)
                return self.send_json({"ok": True, "savedAt": datetime.datetime.now().isoformat(timespec="seconds")})
            if path == "/api/photo":
                name = os.path.basename(str(obj.get("name", "foto.jpg"))).replace(" ", "_")
                ext = Path(name).suffix.lower()
                if ext not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
                    return self.send_json({"ok": False, "error": "Formato de foto no permitido."}, 400)
                content = str(obj.get("data", ""))
                if "," in content:
                    content = content.split(",", 1)[1]
                binary = base64.b64decode(content, validate=True)
                if len(binary) > 20 * 1024 * 1024:
                    return self.send_json({"ok": False, "error": "La foto supera 20 MB."}, 413)
                stem = Path(name).stem[:50] or "animal"
                target = PHOTOS / f"{stem}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}{ext}"
                target.write_bytes(binary)
                return self.send_json({"ok": True, "path": "fotos/" + target.name})
            if path == "/api/backup":
                stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                target = BACKUPS / f"respaldo-manual-{stamp}.json"
                target.write_text(json.dumps(load_data(), ensure_ascii=False, indent=2), encoding="utf-8")
                return self.send_json({"ok": True, "file": target.name})
            return self.send_json({"ok": False, "error": "Ruta no encontrada."}, 404)
        except Exception as exc:
            return self.send_json({"ok": False, "error": str(exc)}, 400)

if __name__ == "__main__":
    import webbrowser, threading, time
    host, port = "127.0.0.1", 8765
    print("Control Ganadero disponible en http://127.0.0.1:8765")
    print("Los datos se guardan junto a este programa, en ganado.json y fotos/.")
    threading.Timer(1.0, lambda: webbrowser.open(f"http://{host}:{port}")).start()
    try:
        ThreadingHTTPServer((host, port), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
