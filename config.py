"""Station configuration for the MTA display app.

Loads from config.yaml if present, otherwise falls back to defaults.
Each Pi can have its own config.yaml to display different stations.
"""

from pathlib import Path

import yaml

_CONFIG_PATH = Path(__file__).parent / "config.yaml"

_DEFAULTS = {
    "stations": [
        {
            "stop_id": "M11",
            "name": "Myrtle Av-Broadway",
            "lines": ["J", "M", "Z"],
        },
    ],
    "refresh_interval_seconds": 30,
    "max_arrivals_per_direction": 5,
}


def _load_config() -> dict:
    if _CONFIG_PATH.exists():
        with open(_CONFIG_PATH) as f:
            return {**_DEFAULTS, **yaml.safe_load(f)}
    return _DEFAULTS


_config = _load_config()

STATIONS: list[dict] = _config["stations"]
REFRESH_INTERVAL_SECONDS: int = _config["refresh_interval_seconds"]
MAX_ARRIVALS_PER_DIRECTION: int = _config["max_arrivals_per_direction"]
