#!/usr/bin/env python3
"""
WiFi Scanner Logger for Termux
Logs nearby WiFi networks over time using termux-wifi-scaninfo.
Tracks signal strength trends and flags new/disappeared networks.
"""

import subprocess
import json
import sqlite3
import time
from datetime import datetime

DB_PATH = "wifi_log.db"
SCAN_INTERVAL = 60  # seconds between scans

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            ssid TEXT,
            bssid TEXT,
            level INTEGER,
            frequency INTEGER,
            capabilities TEXT
        )
    """)
    conn.commit()
    return conn

def run_scan():
    """Run termux-wifi-scaninfo and parse JSON output."""
    try:
        result = subprocess.run(
            ["termux-wifi-scaninfo"],
            capture_output=True, text=True, timeout=20
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"[!] Scan failed: {e}")
        return []

def log_scan(conn, networks):
    c = conn.cursor()
    timestamp = datetime.now().isoformat()
    seen_bssids = set()

    for net in networks:
        ssid = net.get("ssid", "<hidden>")
        bssid = net.get("bssid", "unknown")
        level = net.get("level", 0)
        freq = net.get("frequency", 0)
        caps = net.get("capabilities", "")

        seen_bssids.add(bssid)

        c.execute("""
            INSERT INTO scans (timestamp, ssid, bssid, level, frequency, capabilities)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (timestamp, ssid, bssid, level, freq, caps))

    conn.commit()
    return seen_bssids

def get_known_bssids(conn):
    c = conn.cursor()
    c.execute("SELECT DISTINCT bssid FROM scans")
    return set(row[0] for row in c.fetchall())

def print_summary(networks, new_bssids, gone_bssids):
    print(f"\n--- Scan @ {datetime.now().strftime('%H:%M:%S')} ---")
    print(f"Networks seen: {len(networks)}")

    for net in sorted(networks, key=lambda n: n.get("level", -999), reverse=True):
        ssid = net.get("ssid", "<hidden>")
        level = net.get("level", "?")
        freq = net.get("frequency", "?")
        flag = " 🆕 NEW" if net.get("bssid") in new_bssids else ""
        print(f"  {ssid:25s} {level:>5} dBm  {freq} MHz{flag}")

    if gone_bssids:
        print(f"  ⚠️  {len(gone_bssids)} previously seen network(s) not detected this scan")

def main():
    conn = init_db()
    known_bssids = get_known_bssids(conn)
    print(f"[*] Starting WiFi logger. Scanning every {SCAN_INTERVAL}s. Ctrl+C to stop.")
    print(f"[*] Logging to {DB_PATH}")

    try:
        while True:
            networks = run_scan()
            if networks:
                current_bssids = {n.get("bssid") for n in networks}
                new_bssids = current_bssids - known_bssids
                gone_bssids = known_bssids - current_bssids

                log_scan(conn, networks)
                print_summary(networks, new_bssids, gone_bssids)

                known_bssids = known_bssids.union(current_bssids)
            else:
                print("[!] No networks returned this scan")

            time.sleep(SCAN_INTERVAL)
    except KeyboardInterrupt:
        print("\n[*] Stopped. Data saved in wifi_log.db")
        conn.close()

if __name__ == "__main__":
    main()



