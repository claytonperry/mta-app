# MTA App

Raspberry Pi subway train times display. Fetches real-time arrival data from
the NYC MTA GTFS-realtime API and displays it on an HDMI screen via a local
web app running in kiosk mode.

## Hardware

- Raspberry Pi 3B+ or Pi 4 recommended (Zero 2W works but is tight on memory)
- MicroSD card (16GB+, Samsung EVO or SanDisk Endurance recommended)
- HDMI cable + display/monitor
- 5V/2.5A micro-USB power supply (Pi 3B+) or 5V/3A USB-C (Pi 4)

## Raspberry Pi Setup

### 1. System dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git chromium-browser wmctrl
```

### 2. Clone and install

```bash
cd ~
git clone https://github.com/claytonperry/mta-app.git
cd mta-app
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure stations

Copy one of the example configs to `config.yaml`:

```bash
# For Myrtle Av-Broadway (J/M/Z):
# The default config.py fallback already covers this, or create config.yaml:
cat > config.yaml << 'EOF'
stations:
  - stop_id: "M11"
    name: "Myrtle Av-Broadway"
    lines: ["J", "M", "Z"]

refresh_interval_seconds: 30
max_arrivals_per_direction: 5
EOF

# For 23rd St (all four stations):
cp config.23rd-st.yaml config.yaml
```

`config.yaml` is gitignored so each Pi keeps its own station list. Find stop
IDs in the [MTA GTFS static data](http://web.mta.info/developers/data/nyct/subway/google_transit.zip)
(see `stops.txt`). Up to 6 stations supported.

### 4. Test it

```bash
source .venv/bin/activate
python app.py
```

Open http://localhost:5000 in Chromium to verify.

### 5. Auto-start Flask on boot

Replace `YOUR_USERNAME` with your Pi's username (check with `whoami`):

```bash
sudo tee /etc/systemd/system/mta-app.service << EOF
[Unit]
Description=MTA Arrival Display
After=network-online.target
Wants=network-online.target

[Service]
User=$USER
WorkingDirectory=/home/$USER/mta-app
ExecStart=/home/$USER/mta-app/.venv/bin/python app.py
Restart=always
RestartSec=5
Environment=FLASK_ENV=production

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
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
Exec=sh -c "sleep 10 && chromium-browser --kiosk --disable-gpu --disable-software-rasterizer --disable-extensions --disable-dev-shm-usage --no-sandbox --disable-translate --disable-sync --process-per-site --single-process --disable-background-networking --disable-default-apps --disable-hang-monitor --disable-prompt-on-repost --disable-domain-reliability --no-first-run http://localhost:5000"
EOF
```

The 10-second delay ensures Chromium launches after the desktop is ready.

### 7. Prevent screen blanking and sleep

```bash
# Disable DPMS and screensaver
tee ~/.config/autostart/disable-screensaver.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Disable Screensaver
Exec=sh -c "xset s off; xset -dpms; xset s noblank"
EOF

# Persist via lightdm
sudo mkdir -p /etc/lightdm/lightdm.conf.d
sudo tee /etc/lightdm/lightdm.conf.d/99-no-blanking.conf << 'EOF'
[Seat:*]
xserver-command=X -s 0 -dpms
EOF
```

### 8. Force HDMI output

Prevents black screen on boot if the monitor is slow to handshake:

```bash
sudo sed -i "s/#hdmi_force_hotplug=1/hdmi_force_hotplug=1/" /boot/config.txt
```

### 9. Performance tuning

```bash
# Increase swap (important for Pi Zero 2W / Pi 3B+)
sudo sed -i "s/CONF_SWAPSIZE=100/CONF_SWAPSIZE=512/" /etc/dphys-swapfile
sudo systemctl restart dphys-swapfile

# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl stop bluetooth

# Reduce SD card wear
grep -q "/tmp" /etc/fstab || echo "tmpfs /tmp tmpfs defaults,noatime,nosuid,size=100m 0 0" | sudo tee -a /etc/fstab
grep -q "/var/log" /etc/fstab || echo "tmpfs /var/log tmpfs defaults,noatime,nosuid,size=50m 0 0" | sudo tee -a /etc/fstab
```

### 10. Reboot

```bash
sudo reboot
```

The Pi will start Flask, launch Chromium fullscreen, and display live train
times automatically on every boot.

## Remote Access

To manage the Pi over SSH:

```bash
# Enable SSH on the Pi
sudo systemctl enable ssh
sudo systemctl start ssh

# If your Mac and Pi can't see each other on the local network
# (common with routers that isolate 2.4GHz and 5GHz bands),
# install Tailscale on the Pi:
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --shields-up=false
```

## Local Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Requires Python 3.11 or 3.12 (3.14 has protobuf compatibility issues).
