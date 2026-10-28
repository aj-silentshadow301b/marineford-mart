# Marineford Mart

A deliberately vulnerable Flask CTF storefront for an isolated practice lab. The exercise demonstrates server-side template injection (SSTI), a removal-based filter bypass, client-controlled pricing, a hidden purchase gate, and a multi-part flag receipt.

> **Warning:** This app is intentionally vulnerable. Run it only on your own computer or an isolated lab you control. Never expose it to the public internet or use real credentials or user data.

## Requirements

- Python 3.10+
- Flask 3.x

## Run locally

```sh
python -m venv .venv
```

Activate the environment (`source .venv/bin/activate` on macOS/Linux or `.\.venv\Scripts\Activate.ps1` in PowerShell), then install:

```sh
python -m pip install -r requirements.txt
```

Set a session key and your own encrypted flag fragments before launch.

PowerShell:

```powershell
$env:SECRET_KEY = [guid]::NewGuid().ToString()
$env:ENC_PARTS = '["encoded-part-1","encoded-part-2","encoded-part-3"]'
python app.py
```

macOS/Linux:

```sh
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export ENC_PARTS='["encoded-part-1","encoded-part-2","encoded-part-3"]'
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000). The app binds to localhost by default. The `ACE_SECRET` header value is generated at runtime unless configured explicitly. The bracelet receipt is disabled until three encrypted fragments are set.

### Generate your own flag fragments

Run `python tools/configure_challenge.py`. It prompts for a flag without echoing it, asks for two split positions, and prints the encoded fragments as a JSON array. Copy that JSON into `ENC_PARTS` in your shell environment. The original author solution and flag are not included in this repository.

## Project files

- `app.py` — Flask routes and intentionally vulnerable storefront logic.
- `cipher.py` — reversible Sudoku-derived transposition and URL-safe Base64 wrapper.
- `tools/configure_challenge.py` — local helper that encodes a flag you provide.
- `static/bracelet.png` — image referenced by the receipt route.
- `shop.db` — created at runtime and ignored by Git.

## Lab safety

The SSTI sink, weak blacklist, trusted client price, and hidden header gate are intentional parts of the exercise. Keep the app offline or inside a disposable, network-isolated environment. SQLite stores order details locally. See [SECURITY.md](SECURITY.md) before running the lab.

## License

No license has been selected. All rights are reserved by the author unless a license is added.
