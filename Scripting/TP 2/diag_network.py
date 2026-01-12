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


def main() -> int:
    if not TARGETS_FILE.exists():
        print(f"ERREUR: fichier introuvable: {TARGETS_FILE}")
        return 2

    targets = [line.strip() for line in TARGETS_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]

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
                if is_ip(t):
                    row["target_type"] = "IP"
                    row["ip_valid"] = "true"
                    host_for_tests = t
                else:
                    row["target_type"] = "DNS"
                    resolved = resolve_dns(t)
                    row["dns_resolved_ip"] = resolved
                    host_for_tests = resolved if resolved else t
                    if not resolved:
                        row["notes"] = "DNS failed"

                # Ping (même si DNS KO: on tente sur le nom, cela peut marcher si DNS local/hosts)
                row["ping"] = ping(host_for_tests)

                # Tests TCP
                row["tcp_22"] = test_tcp(host_for_tests, 22)
                row["tcp_443"] = test_tcp(host_for_tests, 443)

            except Exception as e:
                row["notes"] = f"Unhandled error: {type(e).__name__}"
                # On garde ERROR dans les champs déjà initialisés

            writer.writerow(row)

    print(f"OK: rapport généré -> {REPORT_FILE.resolve()}")
    print(f"Cibles traitées: {len(targets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
