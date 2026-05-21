"""
network_scanner.py
------------------
Scans a network range and reports which devices are online.
Usage: python network_scanner.py --range 192.168.1.0/24
"""

import subprocess
import platform
import ipaddress
import argparse
import socket
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


def ping(ip: str) -> dict:
    """Ping a single IP address and return status."""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", "-W", "1", str(ip)]
    try:
        result = subprocess.run(command, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, timeout=2)
        online = result.returncode == 0
    except subprocess.TimeoutExpired:
        online = False

    hostname = ""
    if online:
        try:
            hostname = socket.gethostbyaddr(str(ip))[0]
        except socket.herror:
            hostname = "Unknown"

    return {"ip": str(ip), "online": online, "hostname": hostname}


def scan_network(network_range: str, max_workers: int = 50) -> list:
    """Scan all hosts in a given network range concurrently."""
    try:
        network = ipaddress.ip_network(network_range, strict=False)
    except ValueError as e:
        print(f"[ERROR] Invalid network range: {e}")
        return []

    hosts = list(network.hosts())
    print(f"\n[*] Scanning {len(hosts)} hosts in {network_range} ...")
    print(f"[*] Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(ping, ip): ip for ip in hosts}
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            if result["online"]:
                label = f"  {result['hostname']}" if result["hostname"] else ""
                print(f"  [ONLINE]  {result['ip']}{label}")
            results.append(result)
            # Progress indicator every 20 hosts
            if i % 20 == 0:
                print(f"  ... scanned {i}/{len(hosts)} hosts")

    return results


def print_summary(results: list):
    """Print a summary of scan results."""
    online = [r for r in results if r["online"]]
    offline = [r for r in results if not r["online"]]

    print("\n" + "=" * 50)
    print("  SCAN SUMMARY")
    print("=" * 50)
    print(f"  Total hosts scanned : {len(results)}")
    print(f"  Online              : {len(online)}")
    print(f"  Offline             : {len(offline)}")
    print("=" * 50)

    if online:
        print("\n  Online devices:")
        for r in sorted(online, key=lambda x: ipaddress.ip_address(x["ip"])):
            host = f"  ({r['hostname']})" if r["hostname"] else ""
            print(f"    {r['ip']}{host}")
    print(f"\n[*] Scan completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def save_report(results: list, filename: str = None):
    """Save scan results to a text file."""
    if not filename:
        filename = f"scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    online = [r for r in results if r["online"]]
    with open(filename, "w") as f:
        f.write(f"Network Scan Report\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n")
        f.write(f"Total scanned : {len(results)}\n")
        f.write(f"Online        : {len(online)}\n\n")
        f.write("Online Hosts:\n")
        for r in sorted(online, key=lambda x: ipaddress.ip_address(x["ip"])):
            host = f"  ({r['hostname']})" if r["hostname"] else ""
            f.write(f"  {r['ip']}{host}\n")
    print(f"\n[*] Report saved to: {filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Network Ping Scanner")
    parser.add_argument("--range", default="192.168.1.0/24",
                        help="Network range to scan (default: 192.168.1.0/24)")
    parser.add_argument("--save", action="store_true",
                        help="Save results to a report file")
    parser.add_argument("--workers", type=int, default=50,
                        help="Number of concurrent threads (default: 50)")
    args = parser.parse_args()

    results = scan_network(args.range, args.workers)
    print_summary(results)
    if args.save:
        save_report(results)
