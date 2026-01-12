#!/usr/bin/env python3
"""
TP1 — Lire des cibles depuis un fichier et générer un rapport CSV.
Vous apprenez ici :
- lire un fichier texte
- détecter IP vs DNS
- lancer un ping (commande système)
- écrire un CSV exploitable
"""

import csv
import platform
import subprocess
import ipaddress
from pathlib import Path

TARGETS_FILE = Path("targets.txt")
REPORT_FILE = Path("report.csv")
TIMEOUT_S = 2


def is_ip(value: str) -> bool:
    """
    Vous utilisez ipaddress pour valider proprement une IP.
    Avantage : vous évitez les regex fragiles.
    """
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def ping(host: str) -> str:
    """
    Vous lancez un ping via subprocess.
    Retour attendu : "OK" / "KO" / "ERROR"
    - OK : la commande ping a un returncode 0
    - KO : ping échoue (hôte non joignable, filtrage ICMP, etc.)
    - ERROR : une exception est survenue
    """
    try:
        system = platform.system().lower()

        # Vous adaptez la commande selon l'OS (Windows != Linux/macOS)
        if "windows" in system:
            # -n 1 : un paquet
            # -w ms : timeout en millisecondes (approx)
            cmd = ["ping", "-n", "1", "-w", str(TIMEOUT_S * 1000), host]
        else:
            # Linux/macOS : version simple
            # -c 1 : un paquet
            cmd = ["ping", "-c", "1", host]

        # timeout côté subprocess : évite qu'un ping reste bloqué
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT_S + 1)

        return "OK" if result.returncode == 0 else "KO"

    except subprocess.TimeoutExpired:
        # Si la commande dépasse le temps, vous considérez KO
        return "KO"
    except Exception:
        return "ERROR"


def main() -> int:
    # Vous refusez de continuer si le fichier n'existe pas
    if not TARGETS_FILE.exists():
        print(f"ERREUR: fichier introuvable: {TARGETS_FILE}")
        return 2

    # Vous lisez toutes les lignes, vous strippez et vous ignorez les lignes vides
    targets = [
        line.strip()
        for line in TARGETS_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    # Vous écrivez un CSV propre : newline="" évite les lignes vides sous Windows
    with REPORT_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["target", "type", "ping"])
        writer.writeheader()

        # Vous itérez : automatisation = boucle
        for t in targets:
            row_type = "IP" if is_ip(t) else "DNS"
            row_ping = ping(t)

            writer.writerow({"target": t, "type": row_type, "ping": row_ping})

    print(f"OK: rapport généré -> {REPORT_FILE.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
