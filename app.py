# app.py — Marineford Mart (deliberately vulnerable CTF challenge)
import json
import os
import secrets
import sqlite3

from flask import (Flask, request, redirect, url_for,
                   render_template_string, make_response)

from cipher import sudoku_64_encrypt

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
DB = os.environ.get("DATABASE_PATH", "shop.db")

# ------------------------------------------------------------------
# Challenge material is supplied by the lab operator at runtime.
# Keep the original flag and encrypted fragments out of public source.
# ------------------------------------------------------------------
try:
    ENC_PARTS = json.loads(os.environ.get("ENC_PARTS", "[]"))
except (TypeError, ValueError):
    ENC_PARTS = []
if not isinstance(ENC_PARTS, list) or len(ENC_PARTS) != 3 or not all(isinstance(part, str) and part for part in ENC_PARTS):
    ENC_PARTS = []


# ------------------------------------------------------------------
# Catalog & backdoor
# ------------------------------------------------------------------
PRODUCTS = [
    {"id": 1, "name": "Straw Hat Replica",            "price": 500,     "stock": 99},
    {"id": 2, "name": "Devil Fruit (Display Only)",   "price": 9999,    "stock": 3},
    {"id": 3, "name": "Ace's Fire Fist Bracelet",     "price": 1000000, "stock": 0},
    {"id": 4, "name": "Sea Prism Stone Keychain",     "price": 120,     "stock": 50},
]
ACE_SECRET = os.environ.get("ACE_SECRET") or secrets.token_urlsafe(24)  # generated challenge gate

# ------------------------------------------------------------------
# Bypassable WAF: removal-based blacklist (double-up words to bypass)
# ------------------------------------------------------------------
BAD = ["config", "class", "globals", "popen", "lipsum", "cycler", "joiner",
       "namespace", "open", "read", "system", "import", "subprocess",
       "request", "session", "flag", "cat", "os", "env"]


def waf(s: str) -> str:
    for w in BAD:
        s = s.replace(w, "")
    return s

# ------------------------------------------------------------------
# Database helpers
# ------------------------------------------------------------------
def init_db():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER, qty INTEGER, price INTEGER)""")
    con.commit()
    con.close()


def save_order(pid, qty, price):
    con = sqlite3.connect(DB)
    cur = con.execute(
        "INSERT INTO orders (product_id, qty, price) VALUES (?,?,?)",
        (pid, qty, price))
    con.commit()
    oid = cur.lastrowid
    con.close()
    return oid


def get_order(oid):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    row = con.execute("SELECT * FROM orders WHERE id=?", (oid,)).fetchone()
    con.close()
    return row

# ------------------------------------------------------------------
# LOGIN PANEL — SSTI sink (the fake flag honeypot is in the comment)
# ------------------------------------------------------------------
LOGIN_PAGE = """
<!doctype html><html><head><title>Marineford Mart - Crew Login</title></head><body>
<h2>Marineford Mart - Crew Login</h2>
<form method="POST" action="/login">
  <input name="username" placeholder="Crew handle">
  <input name="password" type="password" placeholder="Secret phrase">
  <button>Set sail</button>
</form>
<p class="hint">The sea keeps its secrets, nakama.</p>
<!-- The Grand Line hides many treasures... FAKE_FLAG: ARC{BETTER_LUCK_NEXT_TOME:BAKA} -->
</body></html>
"""


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = waf(request.form.get("username", ""))
        # VULNERABILITY: user input concatenated into a template string
        template = ("<h2>Ahoy, %s!</h2>"
                    "<p>Wrong secret, nakama. The tide rejects you.</p>") % username
        return render_template_string(template)
    return render_template_string(LOGIN_PAGE)

# ------------------------------------------------------------------
# Storefront
# ------------------------------------------------------------------
INDEX_PAGE = """
<!doctype html><html><head><title>Marineford Mart</title></head><body>
<h2>Marineford Mart — souvenirs of the Grand Line</h2>
<div class="cards">{cards}</div>
</body></html>
"""


@app.route("/")
def index():
    cards = "".join(
        f"<div class='card'><h3>{p['name']}</h3>"
        f"<p>{p['price']} beli | stock: {p['stock']}</p>"
        + ("" if p["stock"] else "<p class='soldout'>SOLD OUT</p>")
        + "</div>"
        for p in PRODUCTS)
    return render_template_string(INDEX_PAGE.format(cards=cards))

# ------------------------------------------------------------------
# ORDER — business-logic vulns: client price + hidden header backdoor
# ------------------------------------------------------------------
@app.route("/order", methods=["POST"])
def order():
    try:
        pid = int(request.form.get("product_id", 0))
        qty = int(request.form.get("qty", 1))
        price = int(request.form.get("price", 0))     # VULN: trusts client price
    except ValueError:
        return "Invalid order.", 400

    product = next((p for p in PRODUCTS if p["id"] == pid), None)
    if not product:
        return "Unknown product.", 404

    if pid == 3 and (not ACE_SECRET or request.headers.get("X-Ace-Secret") != ACE_SECRET):
        return "Ace's flames cannot be bought. (403)", 403

    if pid != 3 and qty > product["stock"]:
        return "Not enough stock.", 400

    oid = save_order(pid, qty, price)
    return redirect(url_for("receipt", oid=oid))     # <- the redirect to the flag page

# ------------------------------------------------------------------
# RECEIPT — the "deep area of the order section"
# ------------------------------------------------------------------
NORMAL_RECEIPT = """
<!doctype html><html><head><title>Order #{oid}</title></head><body>
<h2>Order #{oid} — confirmed</h2>
<p>Thank you, nakama. Your item is on the way.</p>
<p><a href="/">Back to the deck</a></p>
</body></html>
"""

ACE_RECEIPT = """
<!doctype html><html><head><title>Order #{oid}</title></head><body>
<h2>Order #{oid} — confirmed</h2>
<p>Thank you, nakama. The Fire Fist Bracelet is yours. It still burns warm.</p>
<p class="track">Track this voyage: /track/{oid}</p>
<!--
  ============================================================
  order_trace: {p1}
  ============================================================
-->
<script>
  // the log pose remembers every island it has visited
  var seaChart = "{p2}";
</script>
<img src="/static/bracelet.png" alt="bracelet" width="1" height="1">
<p><a href="/">Back to the deck</a></p>
</body></html>
"""


@app.route("/receipt/<int:oid>")
def receipt(oid):
    row = get_order(oid)
    if not row:
        return "Order not found.", 404

    if row["product_id"] == 3:
        if len(ENC_PARTS) != 3:
            return "Challenge fragments are not configured.", 503
        body = render_template_string(ACE_RECEIPT.format(
            oid=oid, p1=ENC_PARTS[0], p2=ENC_PARTS[1], p3=ENC_PARTS[2]))
        resp = make_response(body)
        resp.headers["X-Marine-Trace"] = ENC_PARTS[2]   # fragment 3
        return resp

    return render_template_string(NORMAL_RECEIPT.format(oid=oid))


@app.route("/track/<int:oid>")
def track(oid):
    return "Your ship is at sea, nakama. The log pose points to /receipt/%d." % oid


if __name__ == "__main__":
    init_db()
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", "5000")), debug=os.environ.get("FLASK_DEBUG") == "1")
