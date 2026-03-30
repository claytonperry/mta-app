# MTA App

Raspberry Pi subway train times display. Fetches real-time arrival data from
the NYC MTA GTFS-realtime API and displays it on an HDMI screen via a local
web app running in kiosk mode.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Then open http://localhost:5000 in a browser (or configure Chromium kiosk mode
on the Pi).

## Configuration

Edit `config.py` to set which stations to display (up to 3).

## Kiosk Mode (Raspberry Pi)

To auto-launch in fullscreen on boot, add to `~/.config/autostart/mta.desktop`:

```ini
[Desktop Entry]
Type=Application
Name=MTA Display
Exec=chromium-browser --kiosk --noerrdialogs --disable-infobars http://localhost:5000
```
