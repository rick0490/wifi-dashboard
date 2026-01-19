# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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

**Important:** The initial Speedify install creates an access point with insecure default settings. A custom NetworkManager connection was created to replace it:

```bash
sudo nmcli con add con-name speedify-share ifname wlp1s0 type wifi ip4 192.168.145.1/24 ssid PokemonWifi
```

Additional `nmcli connection modify speedify-share` commands were used to configure:
- WiFi security (WPA2/WPA3)
- Channel and band settings
- Power save options

The connection is named `speedify-share` with SSID `PokemonWifi`.

## Running the Application

```bash
python3 app.py
```

The server runs on `http://localhost:5000` with debug mode enabled.

## Architecture

**Single-file Flask backend** (`app.py`) with **single-page frontend** (`templates/index.html`).

### Backend API Endpoints
- `GET /` - Serves the dashboard UI
- `GET /api/status` - Real-time network performance data (latency, jitter, MOS, packet loss, session stats)
- `GET /api/server` - Current server location and public IP
- `POST /api/change-mode` - Switch bonding modes (speed/streaming/redundant)

### Data Flow
1. Frontend polls `/api/status` every 3 seconds
2. Backend executes `speedify_cli stats` via subprocess
3. CLI JSON output is parsed and transformed for the UI
4. Status indicators (good/warn/bad) are calculated based on thresholds:
   - Latency: <50ms good, <100ms warn, ≥100ms bad
   - Jitter: <10ms good, <30ms warn, ≥30ms bad
   - Packet loss: 0% good, <1% warn, ≥1% bad
   - MOS: ≥4.0 good, ≥3.5 warn, <3.5 bad

### Frontend
Vanilla HTML/CSS/JavaScript with Material design-inspired dark theme. No build process or external JS frameworks.

## Dependencies

- Python 3.12+ with Flask 3.0.2
- Speedify CLI at `/usr/share/speedify/speedify_cli` (system-level installation)

### Installing Speedify

```bash
bash -c "$(curl -sL https://get.speedify.com)"
```

## Key Files

- `app.py` - All backend logic, API routes, and Speedify CLI integration
- `templates/index.html` - Complete frontend (HTML, CSS, and JavaScript in one file)
