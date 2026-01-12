#!/usr/bin/env python3
from __future__ import annotations

import csv
import ipaddress
import platform
import socket
import subprocess
from pathlib import Path

TARGETS_FILE = Path("targets.txt")
REPORT_FILE = Path("report.csv")

PORTS_TO_TEST = [22, 443]
TIMEOUT_S = 2


def is_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def resolve_dns(name: str) -> str:
    """Retourne une IP sous forme de str, ou "" si échec."""
    try:
        return socket.gethostbyname(name)
    except socket.gaierror:
        return ""


def ping(host: str) -> str:
    """
    Retourne: "OK" / "KO" / "ERROR"
    Vous devez adapter la commande selon l'OS.
    """
    try:
        system = platform.system().lower()

        if "windows" in system:
            # -n 1 = 1 paquet ; -w en millisecondes
            cmd = ["ping", "-n", "1", "-w", str(TIMEOUT_S * 1000), host]
        else:
            # Linux/macOS (simplifié) : -c 1 = 1 paquet
            cmd = ["ping", "-c", "1", host]

        r = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT_S + 1)
        return "OK" if r.returncode == 0 else "KO"
    except subprocess.TimeoutExpired:
        return "KO"
    except Exception:
        return "ERROR"


def test_tcp(host: str, port: int) -> str:
    """
    Retourne: "OPEN" / "CLOSED" / "ERROR"
    """
    try:
        with socket.create_connection((host, port), timeout=TIMEOUT_S):
            return "OPEN"
    except (TimeoutError, OSError):
        return "CLOSED"
    except Exception:
        return "ERROR"


def main() -> int:
    if not TARGETS_FILE.exists():
        print(f"ERREUR: fichier introuvable: {TARGETS_FILE}")
        return 2

    targets = [line.strip() for line in TARGETS_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]

    # TODO: ouvrir report.csv et écrire l'en-tête avec DictWriter
    # Colonnes: target, target_type, ip_valid, dns_resolved_ip, ping, tcp_22, tcp_443, notes

    # TODO: pour chaque cible:
    # 1) déterminer type IP/DNS
    # 2) si DNS: résoudre -> dns_resolved_ip
    # 3) choisir l'hôte de test: IP résolue si dispo, sinon la cible originale
    # 4) ping
    # 5) tests TCP 22 et 443
    # 6) écrire une ligne même si tout échoue, sans crash

    print(f"Cibles traitées: {len(targets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
