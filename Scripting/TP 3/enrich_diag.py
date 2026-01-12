#!/usr/bin/env python3
from __future__ import annotations

import csv
import ipaddress
import platform
import socket
import subprocess
from pathlib import Path

import requests

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
    out = {
        "ip_country": "",
        "ip_org": "",
        "ip_asn": "",
        "api_status": "ERROR",
        "notes": "",
    }

    url = f"https://ipapi.co/{ip}/json/"

    try:
        r = requests.get(url, timeout=TIMEOUT_S)
        if r.status_code != 200:
            out["api_status"] = "KO"
            out["notes"] = f"HTTP {r.status_code}"
            return out

        data = r.json()

        # Champs typiques ipapi.co (peuvent varier)
        out["ip_country"] = str(data.get("country_name", "") or "")
        out["ip_org"] = str(data.get("org", "") or "")
        # ipapi.co renvoie parfois "asn" et parfois "asn" absent selon IP / politique
        out["ip_asn"] = str(data.get("asn", "") or "")

        out["api_status"] = "OK"
        return out

    except requests.Timeout:
        out["api_status"] = "KO"
        out["notes"] = "API timeout"
        return out
    except ValueError:
        out["api_status"] = "KO"
        out["notes"] = "Invalid JSON"
        return out
    except Exception as e:
        out["api_status"] = "ERROR"
        out["notes"] = f"{type(e).__name__}"
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

    with REPORT_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for t in targets:
            row = {
                "target": t,
                "target_type": "DNS",
                "dns_resolved_ip": "",
                "ping": "ERROR",
                "tcp_22": "ERROR",
                "tcp_443": "ERROR",
                "ip_country": "",
                "ip_org": "",
                "ip_asn": "",
                "api_status": "ERROR",
                "notes": "",
            }

            try:
                # 1) Type + résolution DNS
                ip_for_api = ""

                if is_ip(t):
                    row["target_type"] = "IP"
                    ip_for_tests = t
                    ip_for_api = t
                else:
                    row["target_type"] = "DNS"
                    resolved = resolve_dns(t)
                    row["dns_resolved_ip"] = resolved
                    ip_for_tests = resolved if resolved else t
                    ip_for_api = resolved  # API seulement si on a une IP
                    if not resolved:
                        row["notes"] = "DNS failed"

                # 2) Tests réseau
                row["ping"] = ping(ip_for_tests)
                row["tcp_22"] = test_tcp(ip_for_tests, 22)
                row["tcp_443"] = test_tcp(ip_for_tests, 443)

                # 3) Enrichissement API
                if ip_for_api:
                    enriched = ip_enrich(ip_for_api)
                    row.update(enriched)
                else:
                    # Pas d'IP -> pas d'enrichissement possible
                    if row["notes"]:
                        row["notes"] += " | "
                    row["notes"] += "No IP for API"

            except Exception as e:
                row["notes"] = f"Unhandled error: {type(e).__name__}"

            writer.writerow(row)

    print(f"OK: rapport généré -> {REPORT_FILE.resolve()}")
    print(f"Cibles traitées: {len(targets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
