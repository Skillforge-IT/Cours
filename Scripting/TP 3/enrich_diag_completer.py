#!/usr/bin/env python3
from __future__ import annotations

import csv
import ipaddress
import platform
import socket
import subprocess
from pathlib import Path

import requests  # nécessite: pip install requests

TARGETS_FILE = Path("targets.txt")
REPORT_FILE = Path("report.csv")

TIMEOUT_S = 2
PORTS = [22, 443]


def is_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def resolve_dns(name: str) -> str:
    try:
        return socket.gethostbyname(name)
    except socket.gaierror:
        return ""


def ping(host: str) -> str:
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
    try:
        with socket.create_connection((host, port), timeout=TIMEOUT_S):
            return "OPEN"
    except (TimeoutError, OSError):
        return "CLOSED"
    except Exception:
        return "ERROR"


def ip_enrich(ip: str) -> dict:
    """
    Appelle l'API REST et retourne un dict avec:
    ip_country, ip_org, ip_asn, api_status, notes
    """
    out = {
        "ip_country": "",
        "ip_org": "",
        "ip_asn": "",
        "api_status": "ERROR",
        "notes": "",
    }

    # TODO:
    # 1) appeler https://ipapi.co/<ip>/json/
    # 2) vérifier le code HTTP
    # 3) parser le JSON
    # 4) remplir out (si champs présents)
    # 5) gérer timeout et erreurs

    return out


def main() -> int:
    if not TARGETS_FILE.exists():
        print(f"ERREUR: fichier introuvable: {TARGETS_FILE}")
        return 2

    targets = [line.strip() for line in TARGETS_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]

    fieldnames = [
        "target", "target_type", "dns_resolved_ip",
        "ping", "tcp_22", "tcp_443",
        "ip_country", "ip_org", "ip_asn",
        "api_status", "notes"
    ]

    # TODO: ouvrir report.csv, écrire l'en-tête
    # TODO: pour chaque cible:
    #  - identifier IP/DNS + résolution éventuelle
    #  - déterminer l'IP à enrichir (si dispo)
    #  - ping + tests de ports
    #  - appel ip_enrich() si IP dispo
    #  - writer.writerow(row)

    print(f"Cibles traitées: {len(targets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
