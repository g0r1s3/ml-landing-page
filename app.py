from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path
from datetime import datetime, timezone
import json
import os

app = Flask(__name__)

# Speicherort für Nachrichten (lokal, ohne DB)
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
MESSAGES_FILE = DATA_DIR / "messages.jsonl"  # JSON Lines: eine Nachricht pro Zeile

def save_message(payload: dict) -> None:
    payload["received_at"] = datetime.now(timezone.utc).isoformat()
    with MESSAGES_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")

@app.get("/")
def index():
    # Erfolgs-/Fehleranzeige über Query-Param
    status = request.args.get("s")  # "ok" | "invalid" | "spam"
    return render_template("index.html", status=status)

@app.get("/impressum")
def impressum():
    return render_template("impressum.html")


@app.post("/contact")
def contact():
    # Einfache Validierung + Honeypot
    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip()
    message = (request.form.get("message") or "").strip()
    website = (request.form.get("website") or "").strip()  # Honeypot: muss leer sein

    if website:
        return redirect(url_for("index", s="spam"))

    if not name or "@" not in email or len(message) < 5:
        return redirect(url_for("index", s="invalid"))

    save_message({"name": name, "email": email, "message": message})
    return redirect(url_for("index", s="ok"))

# Lokaler Dev-Start
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
