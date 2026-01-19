#!/usr/bin/env bash
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

# --- Pre-flight checks ---
# Determine if we need sudo or are already root
if [ "$(id -u)" -eq 0 ]; then
    SUDO=""
else
    if ! command -v sudo &>/dev/null; then
        echo -e "${RED}Error: Not running as root and sudo is not installed${NC}"
        echo "Run as root: su -c 'bash <(curl -sL ...)'"
        echo "Or install sudo: su -c 'apt install sudo && usermod -aG sudo \$USER'"
        exit 1
    fi
    if ! sudo -v; then
        echo -e "${RED}Error: sudo access required${NC}"
        exit 1
    fi
    SUDO="sudo"
fi

# --- Step 1: Install system dependencies ---
echo -e "${YELLOW}[1/7] Installing system dependencies...${NC}"
$SUDO apt update
$SUDO apt install -y python3 python3-pip network-manager curl git
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
    # Login and enable auto-connect on boot with saved credentials
    /usr/share/speedify/speedify_cli startupconnect on "$SPEEDIFY_EMAIL" "$SPEEDIFY_PASS"
else
    echo "Speedify already logged in"
    # Ensure auto-connect is enabled
    /usr/share/speedify/speedify_cli startupconnect on
fi
# Connect to Speedify server
if [ "$SPEEDIFY_STATE" != "CONNECTED" ]; then
    echo "Connecting to Speedify..."
    /usr/share/speedify/speedify_cli connect
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
$SUDO apt install -y python3-flask
echo -e "${GREEN}OK${NC}"

# --- Step 6: Configure WiFi Access Point ---
echo -e "${YELLOW}[6/7] Configuring WiFi Access Point...${NC}"
WIFI_IFACE=$(nmcli -t -f DEVICE,TYPE device status | grep ':wifi$' | cut -d: -f1 | head -1)
if [ -z "$WIFI_IFACE" ]; then
    echo -e "${YELLOW}No WiFi interface found - skipping AP setup${NC}"
else
    echo "Using WiFi interface: $WIFI_IFACE"
    read -s -p "Enter WiFi password (min 8 chars): " WIFI_PSK
    echo ""
    if [ ${#WIFI_PSK} -lt 8 ]; then
        echo -e "${RED}Password too short, using default${NC}"
        WIFI_PSK="ChangeMeNow123"
    fi
    $SUDO nmcli con delete speedify-share 2>/dev/null || true
    $SUDO nmcli con add con-name speedify-share \
        ifname "$WIFI_IFACE" type wifi ip4 192.168.145.1/24 ssid PokemonWifi
    $SUDO nmcli con modify speedify-share \
        802-11-wireless.mode ap 802-11-wireless.band bg 802-11-wireless.channel 6 \
        wifi-sec.key-mgmt wpa-psk wifi-sec.proto rsn wifi-sec.pairwise ccmp \
        wifi-sec.group ccmp wifi-sec.psk "$WIFI_PSK" ipv4.method shared
    $SUDO nmcli con up speedify-share
    echo -e "${GREEN}OK - PokemonWifi active${NC}"
fi

# --- Step 7: Install systemd service ---
echo -e "${YELLOW}[7/7] Installing systemd service...${NC}"
if ! command -v systemctl &>/dev/null; then
    echo -e "${YELLOW}systemd not found - skipping service install${NC}"
    echo "To start manually: cd $INSTALL_DIR && python3 app.py"
else
    $SUDO cp "$INSTALL_DIR/wifi-dashboard.service" /etc/systemd/system/
    $SUDO sed -i "s|/home/wifi|$HOME|g" /etc/systemd/system/wifi-dashboard.service
    $SUDO sed -i "s|User=wifi|User=$USER|g" /etc/systemd/system/wifi-dashboard.service
    $SUDO systemctl daemon-reload
    $SUDO systemctl enable wifi-dashboard.service
    $SUDO systemctl start wifi-dashboard.service
    echo -e "${GREEN}OK${NC}"
fi

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
echo "WiFi: PokemonWifi (password set during setup)"
echo ""
echo "Update: cd ~/wifi_dashboard && git pull && $SUDO systemctl restart wifi-dashboard"
echo ""
