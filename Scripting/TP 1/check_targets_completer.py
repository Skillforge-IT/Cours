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
    Retourne: "OK" ou "KO" ou "ERROR"
    """
    try:
        system = platform.system().lower()

        # TODO: compléter la commande ping selon l'OS
        # Windows: ping -n 1 -w <ms>
        # Linux/macOS: ping -c 1 -W <s>   (sur macOS, -W est différent; on garde simple)
        if "windows" in system:
            cmd = ["ping", "-n", "1", "-w", str(TIMEOUT_S * 1000), host]
        else:
            cmd = ["ping", "-c", "1", host]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT_S + 1)
        return "OK" if result.returncode == 0 else "KO"
    except Exception:
        return "ERROR"


def main() -> int:
    if not TARGETS_FILE.exists():
        print(f"ERREUR: fichier introuvable: {TARGETS_FILE}")
        return 2

    targets = [line.strip() for line in TARGETS_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]

    # TODO: écrire le report.csv avec en-tête et une ligne par cible
    # Colonnes: target, type, ping

    print(f"À traiter: {len(targets)} cible(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
