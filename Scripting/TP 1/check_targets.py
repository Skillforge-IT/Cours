#!/usr/bin/env python3
import csv
import platform
import subprocess
import ipaddress
from pathlib import Path

TARGETS_FILE = Path("targets.txt")
REPORT_FILE = Path("report.csv")
TIMEOUT_S = 2


def is_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def ping(host: str) -> str:
    """
    Retourne: "OK" si ping réussi, "KO" si ping échoue, "ERROR" si exception.
    """
    try:
        system = platform.system().lower()

        if "windows" in system:
            # -n 1 : 1 paquet
            # -w ms : timeout en millisecondes (approx)
            cmd = ["ping", "-n", "1", "-w", str(TIMEOUT_S * 1000), host]
        else:
            # Linux/macOS (simple)
            # -c 1 : 1 paquet
            cmd = ["ping", "-c", "1", host]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT_S + 1)
        return "OK" if result.returncode == 0 else "KO"
    except subprocess.TimeoutExpired:
        return "KO"
    except Exception:
        return "ERROR"


def main() -> int:
    if not TARGETS_FILE.exists():
        print(f"ERREUR: fichier introuvable: {TARGETS_FILE}")
        return 2

    targets = [line.strip() for line in TARGETS_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]

    with REPORT_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["target", "type", "ping"])
        writer.writeheader()

        for t in targets:
            row_type = "IP" if is_ip(t) else "DNS"
            row_ping = ping(t)

            writer.writerow({
                "target": t,
                "type": row_type,
                "ping": row_ping,
            })

    print(f"OK: rapport généré -> {REPORT_FILE.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
