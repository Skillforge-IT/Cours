#!/usr/bin/env python3
"""
TP2 — Diagnostic réseau automatisé.
Vous produisez un rapport CSV avec :
- IP/DNS + résolution DNS
- ping
- test de ports TCP (22/443)
- notes + gestion d'erreurs (script robuste)
"""

from __future__ import annotations

import csv
import ipaddress
import platform
import socket
import subprocess
from pathlib import Path

TARGETS_FILE = Path("targets.txt")
REPORT_FILE = Path("report.csv")

TIMEOUT_S = 2


def is_ip(value: str) -> bool:
    """Vous détectez si la cible est une IP valide."""
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def resolve_dns(name: str) -> str:
    """
    Vous tentez une résolution DNS.
    Retour :
    - IP sous forme de string si succès
    - "" si échec
    """
    try:
        return socket.gethostbyname(name)
    except socket.gaierror:
        return ""


def ping(host: str) -> str:
    """
    Ping OS-dépendant (Windows vs Linux/macOS).
    Retour : OK / KO / ERROR
    """
    try:
        system = platform.system().lower()

        if "windows" in system:
            cmd = ["ping", "-n", "1", "-w", str(TIMEOUT_S * 1000), host]
        else:
            cmd = ["ping", "-c", "1", host]

        r = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT_S + 1)
        return "OK" if r.returncode == 0 else "KO"

    except subprocess.TimeoutExpired:
        return "KO"
    except Exception:
        return "ERROR"


def test_tcp(host: str, port: int) -> str:
    """
    Vous testez si un port TCP est joignable.
    Retour :
    - OPEN : connexion TCP réussie
    - CLOSED : timeout / refus / pas de route (selon cas)
    - ERROR : exception inattendue
    """
    try:
        # create_connection gère timeout + handshake TCP
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

    targets = [
        line.strip()
        for line in TARGETS_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    fieldnames = [
        "target",
        "target_type",
        "ip_valid",
        "dns_resolved_ip",
        "ping",
        "tcp_22",
        "tcp_443",
        "notes",
    ]

    with REPORT_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for t in targets:
            # Vous initialisez une ligne "safe" pour garantir une sortie même en cas d'échec
            row = {
                "target": t,
                "target_type": "DNS",
                "ip_valid": "na",
                "dns_resolved_ip": "",
                "ping": "ERROR",
                "tcp_22": "ERROR",
                "tcp_443": "ERROR",
                "notes": "",
            }

            try:
                # Vous choisissez un hôte de test (IP directe ou IP résolue)
                if is_ip(t):
                    row["target_type"] = "IP"
                    row["ip_valid"] = "true"
                    host_for_tests = t
                else:
                    row["target_type"] = "DNS"
                    resolved = resolve_dns(t)
                    row["dns_resolved_ip"] = resolved

                    # Si DNS résout : vous testez l'IP résolue (plus stable)
                    # Sinon : vous testez quand même le nom (hosts/local DNS possible)
                    host_for_tests = resolved if resolved else t
                    if not resolved:
                        row["notes"] = "DNS failed"

                # Tests réseau
                row["ping"] = ping(host_for_tests)
                row["tcp_22"] = test_tcp(host_for_tests, 22)
                row["tcp_443"] = test_tcp(host_for_tests, 443)

            except Exception as e:
                # Vous ne laissez jamais planter : vous notez l'erreur
                row["notes"] = f"Unhandled error: {type(e).__name__}"

            # Vous écrivez toujours une ligne, quoi qu'il arrive
            writer.writerow(row)

    print(f"OK: rapport généré -> {REPORT_FILE.resolve()}")
    print(f"Cibles traitées: {len(targets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
