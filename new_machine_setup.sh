#!/bin/bash
# ===========================================
# Speedify Dashboard - New Machine Setup
# ===========================================
#
# QUICK SETUP (copy & paste this on the new machine):
#
#   bash <(curl -sL https://raw.githubusercontent.com/rick0490/wifi-dashboard/main/new_machine_setup.sh)
#
# ===========================================

set -e

echo "==========================================="
echo "  Speedify Dashboard - New Machine Setup"
echo "==========================================="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# --- Step 1: Install system dependencies ---
echo -e "${YELLOW}[1/7] Installing system dependencies...${NC}"
sudo apt update
sudo apt install -y python3 python3-pip network-manager curl git
echo -e "${GREEN}OK${NC}"

# --- Step 2: Install Speedify ---
echo -e "${YELLOW}[2/7] Installing Speedify...${NC}"
if [ ! -f /usr/share/speedify/speedify_cli ]; then
    bash -c "$(curl -sL https://get.speedify.com)"
else
    echo "Speedify already installed"
fi
echo -e "${GREEN}OK${NC}"

# --- Step 3: Login to Speedify ---
echo -e "${YELLOW}[3/7] Speedify Login...${NC}"
SPEEDIFY_STATE=$(/usr/share/speedify/speedify_cli state 2>/dev/null | grep -o '"state":"[^"]*"' | cut -d'"' -f4 || echo "UNKNOWN")
if [ "$SPEEDIFY_STATE" != "CONNECTED" ] && [ "$SPEEDIFY_STATE" != "LOGGED_IN" ]; then
    echo "Enter your Speedify credentials:"
    read -p "Email: " SPEEDIFY_EMAIL
    read -s -p "Password: " SPEEDIFY_PASS
    echo ""
    /usr/share/speedify/speedify_cli login "$SPEEDIFY_EMAIL" "$SPEEDIFY_PASS"
else
    echo "Speedify already logged in"
fi
echo -e "${GREEN}OK${NC}"

# --- Step 4: Clone dashboard from GitHub ---
echo -e "${YELLOW}[4/7] Cloning dashboard from GitHub...${NC}"
INSTALL_DIR="$HOME/wifi_dashboard"

if [ -d "$INSTALL_DIR/.git" ]; then
    echo "Repository exists, pulling latest..."
    cd "$INSTALL_DIR"
    git pull || true
elif [ -d "$INSTALL_DIR" ]; then
    echo "Directory exists, backing up..."
    mv "$INSTALL_DIR" "${INSTALL_DIR}.bak.$(date +%s)"
    git clone https://github.com/rick0490/wifi-dashboard.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
else
    git clone https://github.com/rick0490/wifi-dashboard.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi
echo -e "${GREEN}OK${NC}"

# --- Step 5: Install Flask ---
echo -e "${YELLOW}[5/7] Installing Flask...${NC}"
pip3 install flask
echo -e "${GREEN}OK${NC}"

# --- Step 6: Configure WiFi Access Point ---
echo -e "${YELLOW}[6/7] Configuring WiFi Access Point...${NC}"
WIFI_IFACE=$(nmcli device status | grep wifi | grep -v "wifi-p2p" | head -1 | awk '{print $1}')
if [ -z "$WIFI_IFACE" ]; then
    echo -e "${YELLOW}No WiFi interface found - skipping AP setup${NC}"
else
    echo "Using WiFi interface: $WIFI_IFACE"
    sudo nmcli con delete speedify-share 2>/dev/null || true
    sudo nmcli con add con-name speedify-share \
        ifname "$WIFI_IFACE" type wifi ip4 192.168.145.1/24 ssid PokemonWifi
    sudo nmcli con modify speedify-share \
        802-11-wireless.mode ap 802-11-wireless.band bg 802-11-wireless.channel 6 \
        wifi-sec.key-mgmt wpa-psk wifi-sec.proto rsn wifi-sec.pairwise ccmp \
        wifi-sec.group ccmp wifi-sec.psk "Pokemon0490" ipv4.method shared
    sudo nmcli con up speedify-share
    echo -e "${GREEN}OK - PokemonWifi active${NC}"
fi

# --- Step 7: Install systemd service ---
echo -e "${YELLOW}[7/7] Installing systemd service...${NC}"
sudo cp "$INSTALL_DIR/wifi-dashboard.service" /etc/systemd/system/
sudo sed -i "s|/home/wifi|$HOME|g" /etc/systemd/system/wifi-dashboard.service
sudo sed -i "s|User=wifi|User=$USER|g" /etc/systemd/system/wifi-dashboard.service
sudo systemctl daemon-reload
sudo systemctl enable wifi-dashboard.service
sudo systemctl start wifi-dashboard.service
echo -e "${GREEN}OK${NC}"

# --- Verification ---
sleep 2
echo ""
echo "==========================================="
echo -n "Speedify:  "; /usr/share/speedify/speedify_cli state 2>/dev/null | grep -q CONNECTED && echo -e "${GREEN}CONNECTED${NC}" || echo -e "${YELLOW}NOT CONNECTED${NC}"
echo -n "Dashboard: "; curl -s http://localhost:5000/api/status >/dev/null 2>&1 && echo -e "${GREEN}RUNNING${NC}" || echo -e "${RED}NOT RUNNING${NC}"
echo -n "WiFi AP:   "; nmcli con show --active 2>/dev/null | grep -q speedify-share && echo -e "${GREEN}ACTIVE${NC}" || echo -e "${YELLOW}NOT ACTIVE${NC}"
echo "==========================================="
echo ""
echo "Dashboard: http://localhost:5000"
echo "           http://192.168.145.1:5000 (WiFi)"
echo ""
echo "WiFi: PokemonWifi / Pokemon0490"
echo ""
echo "Update: cd ~/wifi_dashboard && git pull && sudo systemctl restart wifi-dashboard"
echo ""
