# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## System Information

| Component | Details |
|-----------|---------|
| Hostname | `wifi-pc` |
| OS | Debian GNU/Linux 13 (trixie) |
| Kernel | 6.12.63+deb13-amd64 |
| Architecture | x86_64 |
| CPU | Intel Core i5-9500T @ 2.20GHz (6 cores) |
| RAM | 16 GB |
| Storage | 110 GB NVMe (~103 GB free) |
| Primary NIC | `eno1` - 192.168.1.31 (LAN) |
| WiFi AP | `wlp2s0` - 192.168.145.1 (Speedify share) |

## Use Case

This machine is a portable network bonding solution designed for **conventions, in-person events, and outdoor settings**. It provides reliable internet connectivity for:

- **Point of Sale (POS) Systems** - Processing credit card transactions and sales at vendor booths, merchandise tables, and pop-up shops where traditional internet is unavailable or unreliable
- **Live Streaming** - Broadcasting live video of in-person events, panels, performances, and activities to online audiences with redundant connectivity to prevent stream drops
- **Event Operations** - Supporting registration systems, badge printing, attendee check-in, and other event management tools that require stable internet

The system bonds multiple cellular connections (Verizon + T-Mobile) to provide failover protection and increased bandwidth in environments where single-carrier coverage may be spotty or congested due to high attendee density.

## Project Overview

Speedify Dashboard - a Flask web application that provides real-time monitoring of Speedify network bonding statistics. It wraps the Speedify CLI tool (`/usr/share/speedify/speedify_cli`) with a web UI.

## Network Setup

This machine provides internet connectivity using Speedify to bond two cellular hotspots:
- Verizon Wireless hotspot
- T-Mobile hotspot

The machine also functions as a WiFi access point, allowing other devices to connect and take advantage of the bonded internet connection from Speedify.

### Access Point Configuration

**Important:** The initial Speedify install creates an access point with insecure default settings. The setup script creates a secure custom NetworkManager connection to replace it.

The setup script prompts for:
- **SSID** - Network name (default: PokemonWifi)
- **Password** - WPA2 password (minimum 8 characters)

The connection is named `speedify-share` and configured with:
- WPA2-PSK security (RSN/CCMP)
- 2.4GHz band, channel 6
- IP sharing via 192.168.145.1/24

To manually create or modify the access point:

```bash
nmcli con add con-name speedify-share ifname <wifi-interface> type wifi ip4 192.168.145.1/24 ssid <YOUR_SSID>
nmcli con modify speedify-share 802-11-wireless.mode ap 802-11-wireless.band bg \
    wifi-sec.key-mgmt wpa-psk wifi-sec.psk "<YOUR_PASSWORD>" ipv4.method shared
nmcli con up speedify-share
```

## Running the Application

```bash
python3 app.py
```

The server runs on `http://localhost:5000`. Debug mode is controlled via the `FLASK_DEBUG` environment variable:

```bash
# Production (default)
python3 app.py

# Development with debug mode
FLASK_DEBUG=true python3 app.py
```

## Architecture

**Single-file Flask backend** (`app.py`) with **single-page frontend** (`templates/index.html`).

### Backend API Endpoints
- `GET /` - Serves the dashboard UI
- `GET /api/status` - Real-time network performance data (latency, jitter, MOS, packet loss, session stats)
- `GET /api/server` - Current server location and public IP
- `POST /api/change-mode` - Switch bonding modes (speed/streaming/redundant)

### Data Flow
1. Frontend polls `/api/status` every 3 seconds (server info every 30 seconds)
2. Backend checks response cache (2-second TTL) before executing CLI commands
3. On cache miss, backend executes `speedify_cli stats` via subprocess
4. CLI JSON output is parsed, cached, and transformed for the UI
5. Status indicators (good/warn/bad) are calculated based on thresholds:
   - Latency: <50ms good, <100ms warn, ≥100ms bad
   - Jitter: <10ms good, <30ms warn, ≥30ms bad
   - Packet loss: 0% good, <1% warn, ≥1% bad
   - MOS: ≥4.0 good, ≥3.5 warn, <3.5 bad

### Response Caching
The backend implements a 2-second TTL cache to reduce subprocess calls:
- Thread-safe using `Lock` for concurrent request handling
- Caches: CLI stats, server info, settings
- Cache is invalidated when bonding mode is changed

### Frontend
Vanilla HTML/CSS/JavaScript with Material design-inspired dark theme. No build process or external JS frameworks.

**Primary Display:** The dashboard is primarily viewed on **tablets and mobile devices** at event venues. Design decisions should prioritize touch-friendly interactions, readable text at arm's length, and responsive layouts that work well on smaller screens.

## Dependencies

- Python 3.12+ with Flask 3.0.2
- Speedify CLI at `/usr/share/speedify/speedify_cli` (system-level installation)

### Installing Speedify

```bash
bash -c "$(curl -sL https://get.speedify.com)"
```

### Speedify CLI Reference

See `SPEEDIFY_CLI.md` for complete CLI command documentation. Key commands used by this dashboard:

| Command | Purpose |
|---------|---------|
| `speedify_cli stats 1` | Get real-time connection statistics |
| `speedify_cli show settings` | Get current bonding mode and settings |
| `speedify_cli show currentserver` | Get server location and public IP |
| `speedify_cli mode <mode>` | Switch bonding mode (speed/streaming/redundant) |
| `speedify_cli show adapters` | List all network adapters |

**Planned CLI Integrations:** See the "CLI-Based Features" section in `ROADMAP.md` for 20+ additional CLI commands that can be leveraged to enhance the dashboard (adapter priority control, data limits, speed tests, captive portal detection, etc.).

Full CLI documentation: [Speedify CLI Support Article](https://support.speedify.com/article/285-speedify-cli)

## New Machine Setup

A setup script automates the full installation on Debian/Ubuntu systems:

```bash
bash <(curl -sL https://raw.githubusercontent.com/rick0490/wifi-dashboard/main/new_machine_setup.sh)
```

The script handles:
1. Installing system dependencies (python3, network-manager, git, etc.)
2. Installing Speedify and configuring auto-connect on boot
3. Cloning the dashboard repository
4. Installing Flask via apt (python3-flask)
5. Configuring the WiFi access point (prompts for SSID and password)
6. Installing and enabling the systemd service

**Compatibility:**
- Debian 12+ / Ubuntu 22.04+
- Works as root (no sudo required) or with sudo
- Handles PEP 668 (externally-managed-environment) on modern systems

## Key Files

- `app.py` - All backend logic, API routes, Speedify CLI integration, and response caching
- `templates/index.html` - Complete frontend (HTML, CSS, and JavaScript in one file)
- `test_e2e.py` - Comprehensive E2E test suite (69 tests)
- `new_machine_setup.sh` - Automated setup script for new Debian/Ubuntu machines
- `wifi-dashboard.service` - systemd service unit file
- `ROADMAP.md` - Project roadmap, completed features, planned improvements, and CLI-Based Features reference
- `SPEEDIFY_CLI.md` - Complete Speedify CLI command reference

## Running Tests

```bash
# Start the server first
python3 app.py &

# Run the E2E test suite
python3 test_e2e.py
```

The test suite covers:
- All API endpoints and response validation
- Response caching behavior and expiration
- Health score calculation
- Concurrent request handling
- Input validation (invalid JSON, missing fields)
