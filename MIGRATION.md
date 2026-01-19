# Migration Guide: Moving to a New Machine

This guide covers migrating the Speedify Dashboard and all related configuration to a new machine.

## Current System Summary

| Component | Details |
|-----------|---------|
| Python | 3.12.3 |
| Flask | 3.0.2 |
| Speedify | 15.6.4 (build 12495) |
| WiFi SSID | PokemonWifi |
| WiFi Interface | wlp1s0 |
| Dashboard Port | 5000 |
| Service | wifi-dashboard.service (enabled) |

---

## Step 1: Backup Current Machine

### 1.1 Create a backup archive of the dashboard

```bash
# On the OLD machine
cd /home/wifi
tar -czvf wifi_dashboard_backup.tar.gz wifi_dashboard/
```

### 1.2 Export the WiFi access point configuration

```bash
# Export the NetworkManager connection (includes WiFi password)
sudo nmcli con export speedify-share > ~/speedify-share.nmconnection

# If that doesn't work, manually save the config:
sudo cp /etc/NetworkManager/system-connections/speedify-share.nmconnection ~/
sudo chown $USER:$USER ~/speedify-share.nmconnection
```

### 1.3 Export Speedify settings (optional)

```bash
# Speedify stores settings in:
# ~/.config/speedify/ (user settings)
# /etc/speedify/ (system settings)

# Backup Speedify config
tar -czvf ~/speedify_config_backup.tar.gz ~/.config/speedify/ 2>/dev/null
sudo tar -czvf ~/speedify_system_backup.tar.gz /etc/speedify/ 2>/dev/null
```

### 1.4 Note your Speedify account credentials

You'll need to log in again on the new machine. Make sure you have:
- Speedify account email
- Speedify account password
- Or: Dedicated server credentials if using Speedify Teams

### 1.5 Transfer files to new machine

```bash
# Using scp (replace NEW_MACHINE_IP with actual IP)
scp ~/wifi_dashboard_backup.tar.gz user@NEW_MACHINE_IP:~/
scp ~/speedify-share.nmconnection user@NEW_MACHINE_IP:~/

# Or use a USB drive, cloud storage, etc.
```

---

## Step 2: Set Up New Machine

### 2.1 Install base requirements

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv

# Install NetworkManager (usually pre-installed)
sudo apt install -y network-manager
```

### 2.2 Install Speedify

```bash
# Official Speedify installer
bash -c "$(curl -sL https://get.speedify.com)"

# Log in to Speedify
speedify_cli login YOUR_EMAIL YOUR_PASSWORD

# Or for Speedify Teams with dedicated server:
# speedify_cli login YOUR_EMAIL YOUR_PASSWORD
# speedify_cli dedicatedserver YOUR_SERVER_ADDRESS
```

### 2.3 Verify Speedify is working

```bash
# Check status
speedify_cli state

# Should show "CONNECTED" or similar
speedify_cli show currentserver
```

---

## Step 3: Restore Dashboard Application

### 3.1 Create the wifi user (if needed)

```bash
# If you want to use the same username
sudo adduser wifi
sudo usermod -aG sudo wifi

# Switch to wifi user
su - wifi
```

### 3.2 Extract the backup

```bash
cd /home/wifi
tar -xzvf wifi_dashboard_backup.tar.gz
```

### 3.3 Install Python dependencies

```bash
cd /home/wifi/wifi_dashboard
pip3 install flask
```

### 3.4 Test the application

```bash
python3 app.py
# Visit http://localhost:5000 to verify it works
# Ctrl+C to stop
```

---

## Step 4: Configure WiFi Access Point

### 4.1 Identify your WiFi interface

```bash
# List wireless interfaces
nmcli device status | grep wifi

# Note the interface name (e.g., wlp1s0, wlan0, etc.)
```

### 4.2 Option A: Import the saved connection

```bash
# Import the exported connection
sudo nmcli con load ~/speedify-share.nmconnection

# You may need to modify the interface name if it's different
sudo nmcli con modify speedify-share connection.interface-name YOUR_INTERFACE
```

### 4.2 Option B: Create a new access point from scratch

```bash
# Replace wlp1s0 with your interface name
# Replace YOUR_WIFI_PASSWORD with your desired password

# Create the connection
sudo nmcli con add con-name speedify-share \
    ifname wlp1s0 \
    type wifi \
    ip4 192.168.145.1/24 \
    ssid PokemonWifi

# Configure as access point with security
sudo nmcli con modify speedify-share \
    802-11-wireless.mode ap \
    802-11-wireless.band bg \
    802-11-wireless.channel 6 \
    wifi-sec.key-mgmt wpa-psk \
    wifi-sec.proto rsn \
    wifi-sec.pairwise ccmp \
    wifi-sec.group ccmp \
    wifi-sec.psk "YOUR_WIFI_PASSWORD"

# Set IPv4 to shared (enables NAT/DHCP)
sudo nmcli con modify speedify-share ipv4.method shared

# Start the access point
sudo nmcli con up speedify-share
```

### 4.3 Verify the access point is working

```bash
# Check connection status
nmcli con show --active

# Should see speedify-share listed
# Try connecting a device to "PokemonWifi"
```

---

## Step 5: Set Up Systemd Service

### 5.1 Copy the service file

```bash
sudo cp /home/wifi/wifi_dashboard/wifi-dashboard.service /etc/systemd/system/
```

### 5.2 Reload and enable the service

```bash
sudo systemctl daemon-reload
sudo systemctl enable wifi-dashboard.service
sudo systemctl start wifi-dashboard.service
```

### 5.3 Verify the service is running

```bash
sudo systemctl status wifi-dashboard.service

# Check the dashboard
curl http://localhost:5000/api/status
```

---

## Step 6: Final Verification Checklist

Run through this checklist to confirm everything is working:

- [ ] **Speedify connected**: `speedify_cli state` shows CONNECTED
- [ ] **Both carriers visible**: `speedify_cli show adapters` shows Verizon and T-Mobile
- [ ] **Dashboard running**: `curl http://localhost:5000/api/status` returns JSON
- [ ] **Service enabled**: `systemctl is-enabled wifi-dashboard.service` shows enabled
- [ ] **WiFi AP active**: Can connect a phone to "PokemonWifi"
- [ ] **Internet through AP**: Device connected to PokemonWifi can browse the web
- [ ] **Dashboard accessible**: Can open http://192.168.145.1:5000 from connected device

---

## Quick Setup Script

Save this as `setup_new_machine.sh` on the new machine:

```bash
#!/bin/bash
set -e

echo "=== Speedify Dashboard Migration Script ==="

# Check if running as correct user
if [ "$USER" != "wifi" ]; then
    echo "Warning: Running as $USER, not 'wifi'"
fi

# Install dependencies
echo "Installing dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip network-manager curl

# Install Speedify
echo "Installing Speedify..."
if [ ! -f /usr/share/speedify/speedify_cli ]; then
    bash -c "$(curl -sL https://get.speedify.com)"
else
    echo "Speedify already installed"
fi

# Install Flask
echo "Installing Flask..."
pip3 install flask

# Extract backup if present
if [ -f ~/wifi_dashboard_backup.tar.gz ]; then
    echo "Extracting dashboard backup..."
    cd /home/wifi
    tar -xzvf ~/wifi_dashboard_backup.tar.gz
fi

# Install service
if [ -f /home/wifi/wifi_dashboard/wifi-dashboard.service ]; then
    echo "Installing systemd service..."
    sudo cp /home/wifi/wifi_dashboard/wifi-dashboard.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable wifi-dashboard.service
fi

echo ""
echo "=== Next Steps ==="
echo "1. Log in to Speedify: speedify_cli login EMAIL PASSWORD"
echo "2. Configure WiFi AP (see MIGRATION.md Step 4)"
echo "3. Start the service: sudo systemctl start wifi-dashboard.service"
echo "4. Verify: curl http://localhost:5000/api/status"
```

---

## Troubleshooting

### Speedify not connecting

```bash
# Check Speedify logs
journalctl -u speedify -f

# Restart Speedify
sudo systemctl restart speedify

# Re-login
speedify_cli logout
speedify_cli login EMAIL PASSWORD
```

### WiFi AP not starting

```bash
# Check if interface exists
nmcli device status

# Check for conflicts
sudo nmcli con show

# Delete and recreate if needed
sudo nmcli con delete speedify-share
# Then follow Step 4.2 Option B
```

### Dashboard not accessible

```bash
# Check if running
sudo systemctl status wifi-dashboard.service

# Check logs
journalctl -u wifi-dashboard.service -f

# Test manually
cd /home/wifi/wifi_dashboard
python3 app.py
```

### Permission issues

```bash
# Fix ownership
sudo chown -R wifi:wifi /home/wifi/wifi_dashboard

# Fix service file permissions
sudo chmod 644 /etc/systemd/system/wifi-dashboard.service
```

---

## Hardware Recommendations for New Machine

Since this is used for events/conventions, consider:

| Component | Recommendation |
|-----------|----------------|
| **Form Factor** | Mini PC or NUC (portable, fanless preferred) |
| **CPU** | Intel N100 or better (low power, good performance) |
| **RAM** | 8GB minimum |
| **Storage** | 128GB SSD minimum |
| **WiFi** | Intel AX200/AX210 (good AP mode support) |
| **Ethernet** | At least 1 port (for wired hotspot connection) |
| **USB** | Multiple USB 3.0 ports (for USB hotspots) |
| **Power** | 12V DC input option (for battery/car power) |

**Recommended models:**
- Beelink Mini S12 Pro
- Intel NUC 12/13
- MinisForum UM560/UM780
- GMKtec NucBox

---

## Files to Transfer Summary

| File/Directory | Purpose |
|----------------|---------|
| `/home/wifi/wifi_dashboard/` | Entire dashboard application |
| `speedify-share.nmconnection` | WiFi AP configuration |
| `~/.config/speedify/` | Speedify user settings (optional) |
| Speedify account credentials | For logging in on new machine |
