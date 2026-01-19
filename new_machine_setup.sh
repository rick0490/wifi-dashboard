#!/bin/bash
# ===========================================
# Speedify Dashboard - New Machine Setup
# ===========================================
# Run this script on the NEW machine after transferring wifi_dashboard_backup.tar.gz
#
# Usage: bash new_machine_setup.sh
# ===========================================

set -e

echo "==========================================="
echo "  Speedify Dashboard - New Machine Setup"
echo "==========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# --- Step 1: Check if running as wifi user ---
echo -e "${YELLOW}[1/8] Checking user...${NC}"
if [ "$USER" != "wifi" ]; then
    echo -e "${RED}Warning: Running as '$USER', not 'wifi'${NC}"
    echo "Consider creating 'wifi' user: sudo adduser wifi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
echo -e "${GREEN}OK${NC}"

# --- Step 2: Install system dependencies ---
echo -e "${YELLOW}[2/8] Installing system dependencies...${NC}"
sudo apt update
sudo apt install -y python3 python3-pip network-manager curl
echo -e "${GREEN}OK${NC}"

# --- Step 3: Install Speedify ---
echo -e "${YELLOW}[3/8] Installing Speedify...${NC}"
if [ ! -f /usr/share/speedify/speedify_cli ]; then
    bash -c "$(curl -sL https://get.speedify.com)"
else
    echo "Speedify already installed"
fi
echo -e "${GREEN}OK${NC}"

# --- Step 4: Login to Speedify ---
echo -e "${YELLOW}[4/8] Speedify Login...${NC}"
echo "Enter your Speedify credentials:"
read -p "Email: " SPEEDIFY_EMAIL
read -s -p "Password: " SPEEDIFY_PASS
echo ""
/usr/share/speedify/speedify_cli login "$SPEEDIFY_EMAIL" "$SPEEDIFY_PASS"
echo -e "${GREEN}OK${NC}"

# --- Step 5: Extract dashboard backup ---
echo -e "${YELLOW}[5/8] Extracting dashboard...${NC}"
cd /home/$USER
if [ -f wifi_dashboard_backup.tar.gz ]; then
    tar -xzvf wifi_dashboard_backup.tar.gz
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}ERROR: wifi_dashboard_backup.tar.gz not found in /home/$USER${NC}"
    echo "Please copy the backup file and run this script again."
    exit 1
fi

# --- Step 6: Install Python dependencies ---
echo -e "${YELLOW}[6/8] Installing Flask...${NC}"
pip3 install flask
echo -e "${GREEN}OK${NC}"

# --- Step 7: Configure WiFi Access Point ---
echo -e "${YELLOW}[7/8] Configuring WiFi Access Point...${NC}"

# Get WiFi interface
WIFI_IFACE=$(nmcli device status | grep wifi | head -1 | awk '{print $1}')
if [ -z "$WIFI_IFACE" ]; then
    echo -e "${RED}ERROR: No WiFi interface found${NC}"
    echo "Please configure WiFi AP manually."
else
    echo "Detected WiFi interface: $WIFI_IFACE"

    # Delete existing connection if present
    sudo nmcli con delete speedify-share 2>/dev/null || true

    # Create new access point
    sudo nmcli con add con-name speedify-share \
        ifname "$WIFI_IFACE" \
        type wifi \
        ip4 192.168.145.1/24 \
        ssid PokemonWifi

    # Configure security and AP mode
    sudo nmcli con modify speedify-share \
        802-11-wireless.mode ap \
        802-11-wireless.band bg \
        802-11-wireless.channel 6 \
        wifi-sec.key-mgmt wpa-psk \
        wifi-sec.proto rsn \
        wifi-sec.pairwise ccmp \
        wifi-sec.group ccmp \
        wifi-sec.psk "Pokemon0490" \
        ipv4.method shared

    # Start the access point
    sudo nmcli con up speedify-share
    echo -e "${GREEN}OK - WiFi AP 'PokemonWifi' is active${NC}"
fi

# --- Step 8: Install and enable systemd service ---
echo -e "${YELLOW}[8/8] Installing systemd service...${NC}"
sudo cp /home/$USER/wifi_dashboard/wifi-dashboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable wifi-dashboard.service
sudo systemctl start wifi-dashboard.service
echo -e "${GREEN}OK${NC}"

# --- Final verification ---
echo ""
echo "==========================================="
echo "  Setup Complete! Running verification..."
echo "==========================================="
echo ""

sleep 2

# Check Speedify
echo -n "Speedify: "
if /usr/share/speedify/speedify_cli state | grep -q "CONNECTED"; then
    echo -e "${GREEN}CONNECTED${NC}"
else
    echo -e "${YELLOW}NOT CONNECTED (may need adapter setup)${NC}"
fi

# Check Dashboard
echo -n "Dashboard: "
if curl -s http://localhost:5000/api/status > /dev/null 2>&1; then
    echo -e "${GREEN}RUNNING${NC}"
else
    echo -e "${RED}NOT RESPONDING${NC}"
fi

# Check WiFi AP
echo -n "WiFi AP: "
if nmcli con show --active | grep -q "speedify-share"; then
    echo -e "${GREEN}ACTIVE (PokemonWifi)${NC}"
else
    echo -e "${YELLOW}NOT ACTIVE${NC}"
fi

echo ""
echo "==========================================="
echo "  Access dashboard at:"
echo "  - http://localhost:5000"
echo "  - http://192.168.145.1:5000 (from WiFi clients)"
echo "==========================================="
echo ""
echo "WiFi Network: PokemonWifi"
echo "WiFi Password: Pokemon0490"
echo ""
