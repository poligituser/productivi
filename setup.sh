#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

python3 -m venv .venv
.venv/bin/python -m pip install --no-cache-dir -r requirements.txt
.venv/bin/python - <<'PY'
from pathlib import Path
from secrets import token_urlsafe

path = Path(".env")
if not path.exists():
    text = Path(".env.example").read_text()
    for key in ("DJANGO_SECRET_KEY", "POSTGRES_PASSWORD"):
        text = text.replace(f"{key}=\n", f"{key}={token_urlsafe(48)}\n")
    path.touch(mode=0o600, exist_ok=False)
    path.write_text(text)
PY
docker compose up -d --wait
.venv/bin/python manage.py migrate --noinput
.venv/bin/python manage.py check --database default
.venv/bin/python manage.py shell -c 'from django.db import connection; connection.ensure_connection(); print("PostgreSQL: соединение установлено")'
