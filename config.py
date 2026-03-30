"""Station configuration for the MTA display app."""

# Each station entry needs:
#   - stop_id: MTA GTFS parent stop ID (direction suffixes N/S added automatically)
#   - name: Display name
#   - lines: List of subway line identifiers to fetch feeds for
#
# Find stop IDs in the MTA GTFS static data:
#   http://web.mta.info/developers/data/nyct/subway/google_transit.zip (stops.txt)
#
# Up to 3 stations supported.

STATIONS: list[dict] = [
    {
        "stop_id": "M11",
        "name": "Myrtle Av-Broadway",
        "lines": ["J", "M", "Z"],
    },
    # Uncomment to add more stations (max 3):
    # {
    #     "stop_id": "G36",
    #     "name": "Hoyt-Schermerhorn Sts",
    #     "lines": ["A", "C", "G"],
    # },
    # {
    #     "stop_id": "L17",
    #     "name": "Myrtle-Wyckoff Avs",
    #     "lines": ["L", "M"],
    # },
]

# How often the frontend polls for new data (seconds)
REFRESH_INTERVAL_SECONDS = 30

# How many upcoming arrivals to show per direction per station
MAX_ARRIVALS_PER_DIRECTION = 5
