import getpass
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cipher import sudoku_64_encrypt


def main():
    flag = getpass.getpass("Enter a challenge flag (input is hidden): ")
    if len(flag) < 3:
        raise SystemExit("The flag must contain at least three characters.")

    first = int(input(f"Split after which character (1-{len(flag) - 2})? "))
    if first < 1 or first > len(flag) - 2:
        raise SystemExit("Invalid first split position.")
    second = int(input(f"Split after which character ({first + 1}-{len(flag) - 1})? "))
    if second <= first or second >= len(flag):
        raise SystemExit("Invalid second split position.")

    parts = [flag[:first], flag[first:second], flag[second:]]
    encoded = [sudoku_64_encrypt(part.encode("utf-8")) for part in parts]
    print("\nSet ENC_PARTS to this JSON value in your shell environment:")
    print(json.dumps(encoded))


if __name__ == "__main__":
    main()
