# Marineford Mart

A small, intentionally vulnerable Flask CTF storefront for an isolated practice lab. The exercise combines server-side template injection (SSTI), a removal-based input filter, client-controlled order pricing, a hidden purchase gate, and a multi-part flag exposed through a receipt flow.

> **Warning:** This application is deliberately vulnerable. Run it only on your own machine or an isolated lab you control. Do not expose it to the public internet or use real credentials or user data.

## Requirements

- Python 3.10+
- Flask 3.x

## Run locally

```sh
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Configure a private session key and your own challenge flag fragments before launching the app.

PowerShell:

```powershell
$env:SECRET_KEY = [guid]::NewGuid().ToString()
$env:ENC_PARTS = '["paste-encoded-part-1","paste-encoded-part-2","paste-encoded-part-3"]'
python app.py
```

macOS/Linux:

```sh
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export ENC_PARTS='["paste-encoded-part-1","paste-encoded-part-2","paste-encoded-part-3"]'
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000). The app binds to localhost by default. The bracelet receipt route remains unavailable until three encoded flag fragments are configured.

### Create your own flag fragments

Run `python tools/configure_challenge.py`. It prompts for a flag without echoing it, asks where to split it into three pieces, and prints an `ENC_PARTS` JSON value. Copy that value into your shell environment before starting the app. The private flag is not included in this repository.

## Project files

- `app.py` — Flask routes and the intentionally vulnerable storefront.
- `cipher.py` — reversible Sudoku-derived transposition and URL-safe Base64 wrapper.
- `tools/configure_challenge.py` — local-only helper to encode a flag you supply.
- `static/bracelet.png` — tiny image used by the receipt page.
- `shop.db` — created locally at runtime and ignored by Git.

The original author-only solver and encryption script are omitted from this public repository.

## Lab safety

The SSTI sink, weak blacklist, trusted client price, and hidden header gate are the exercise itself. Keep the instance offline or inside a disposable, network-isolated environment. The SQLite database records submitted orders. Review [SECURITY.md](SECURITY.md) before running the challenge.

## License

No license has been selected. All rights are reserved by the author unless a license is added.
