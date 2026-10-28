# cipher.py
import base64

# 0-indexed first row of a classic solved Sudoku grid (permutation of 0..7)
SEED = [7, 2, 4, 0, 5, 6, 1, 3]
GRID = 8
CELLS = GRID * GRID


def _order(shift):
    rows = [SEED[(i + shift) % GRID] for i in range(GRID)]
    cols = [SEED[(j + 2 * shift) % GRID] for j in range(GRID)]
    return rows, cols


def _transpose(s, shift):
    """Fill 8x8 grid row-major, read out in Sudoku-derived order."""
    rows, cols = _order(shift)
    return "".join(s[rows[i] * GRID + cols[j]]
                   for i in range(GRID) for j in range(GRID))


def _inverse(s, shift):
    """Undo one transposition round."""
    rows, cols = _order(shift)
    out = [""] * CELLS
    for i in range(GRID):
        for j in range(GRID):
            out[rows[i] * GRID + cols[j]] = s[i * GRID + j]
    return "".join(out)


def sudoku_64_encrypt(data: bytes, rounds: int = 3, key: int = 7) -> str:
    b64 = base64.urlsafe_b64encode(data).decode().rstrip("=")
    while len(b64) % CELLS != 0:
        b64 += "."                     # '.' is outside the b64 alphabet -> stripped on decode
    for r in range(rounds):
        b64 = _transpose(b64, key + r)
    return b64


def sudoku_64_decrypt(ct: str, rounds: int = 3, key: int = 7) -> bytes:
    for r in reversed(range(rounds)):
        ct = _inverse(ct, key + r)
    clean = ct.replace(".", "")
    clean += "=" * (-len(clean) % 4)
    return base64.urlsafe_b64decode(clean)
