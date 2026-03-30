# MTA App

Raspberry Pi subway train times display. Fetches real-time arrival data from
the NYC MTA GTFS-realtime API and displays it on an HDMI screen via a local
web app running in kiosk mode.

## Hardware

- Raspberry Pi (any model with wifi — Pi 3B+, 4, or Zero 2W)
- MicroSD card (16GB+) with Raspberry Pi OS (Bookworm)
- HDMI cable + display/monitor
- Power supply for the Pi

## Raspberry Pi Setup

### 1. System dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git chromium-browser
```

### 2. Clone and install

```bash
cd ~
git clone https://github.com/claytonperry/mta-app.git
cd mta-app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Test it

```bash
python app.py
```

Open http://localhost:5000 in Chromium to verify.

### 4. Configure stations

Edit `config.py` to set which stations to display (up to 3). Find stop IDs in
the [MTA GTFS static data](http://web.mta.info/developers/data/nyct/subway/google_transit.zip)
(see `stops.txt`).

### 5. Auto-start the Flask server on boot

Create a systemd service:

```bash
sudo tee /etc/systemd/system/mta-app.service << 'EOF'
[Unit]
Description=MTA Arrival Display
After=network-online.target
Wants=network-online.target

[Service]
User=pi
WorkingDirectory=/home/pi/mta-app
ExecStart=/home/pi/mta-app/.venv/bin/python app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable mta-app
sudo systemctl start mta-app
```

### 6. Auto-launch Chromium in kiosk mode

```bash
mkdir -p ~/.config/autostart
tee ~/.config/autostart/mta-display.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=MTA Display
Exec=chromium-browser --kiosk --noerrdialogs --disable-infobars --disable-session-crashed-bubble http://localhost:5000
EOF
```

### 7. Disable screen blanking

```bash
sudo raspi-config
# Display Options -> Screen Blanking -> No
```

Reboot. The Pi will start the Flask server, launch Chromium fullscreen, and
show live train times automatically.

## Local Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Requires Python 3.11 or 3.12 (3.14 has protobuf compatibility issues).
