WiFi Scanner Logger
A lightweight WiFi network scanner and logger built for Termux on Android — no root required.
What it does
Uses Android's native WifiManager (via termux-wifi-scaninfo from Termux:API) to passively scan and log nearby WiFi networks over time.
Scans every 60 seconds
Logs SSID, BSSID, signal strength (dBm), frequency, and security capabilities to a local SQLite database
Flags networks that newly appear (🆕) or disappear between scans
Prints a live summary sorted by signal strength after every scan
Why this approach
Most wireless tooling assumes root access and monitor-mode-capable hardware. This works entirely through Android's permitted APIs — making passive WiFi visibility practical on stock, unrooted devices.
Requirements
Termux (GitHub release, not the outdated Play Store version)
Termux:API (same source as Termux)
Python 3
Setup

pkg install python termux-api

On first run, Android will prompt for location permission (required for WiFi scan results) — grant it.
Usage

python wifi_logger.py


Press Ctrl+C to stop. All scan history is saved to wifi_log.db in the same folder.
Query the database for historical analysis:

sqlite3 wifi_log.db "SELECT * FROM scans;"

Scope
This tool is passive recon only — it observes broadcast signals that any phone already sees when WiFi is on. It does not connect to networks, capture handshakes, or attempt to access any network's credentials.
Roadmap
Tie into a SOC-style alerting layer for rogue/unexpected AP detection
Export scan history to CSV for easier analysis
Configurable scan interval via CLI flag
Author
Kazeem Abubakri — GitHub
