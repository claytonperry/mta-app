"""Fetch real-time MTA subway arrival data using nyct-gtfs."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from nyct_gtfs import NYCTFeed


# Map line letters to the feed URL they belong to.
# The MTA groups lines into feeds; nyct-gtfs accepts a line letter and
# resolves it automatically, but we cache feeds per unique line group
# to avoid redundant requests when multiple lines share a feed.
# See https://api.mta.info/#/subwayRealTimeFeeds for groupings.
LINE_TO_FEED_GROUP: dict[str, str] = {
    "1": "1", "2": "1", "3": "1", "4": "1", "5": "1", "6": "1", "S": "1",
    "A": "A", "C": "A", "E": "A",
    "N": "N", "Q": "N", "R": "N", "W": "N",
    "B": "B", "D": "B", "F": "B", "M": "B",
    "L": "L",
    "G": "G",
    "J": "J", "Z": "J",
    "7": "7",
}


def get_arrivals(stop_id: str, lines: list[str], max_per_direction: int = 5) -> dict:
    """Return upcoming arrivals for a station, grouped by direction.

    Args:
        stop_id: Parent stop ID (e.g. "M11"). N/S suffixes are appended.
        lines: Line letters to check (e.g. ["J", "M", "Z"]).
        max_per_direction: Max arrivals to return per direction.

    Returns:
        Dict with "northbound" and "southbound" lists of arrival dicts,
        each containing "line", "destination", and "minutes_away".
    """
    now = datetime.now(timezone.utc)
    northbound: list[dict] = []
    southbound: list[dict] = []

    # Deduplicate feeds — e.g. J and Z share the same feed
    seen_feeds: set[str] = set()
    for line in lines:
        feed_group = LINE_TO_FEED_GROUP.get(line, line)
        if feed_group in seen_feeds:
            continue
        seen_feeds.add(feed_group)

        try:
            feed = NYCTFeed(line)
        except Exception:
            continue

        for trip in feed.trips:
            route = trip.route_id
            if route not in lines:
                continue

            for update in trip.stop_time_updates:
                if update.stop_id not in (f"{stop_id}N", f"{stop_id}S"):
                    continue

                arrival_time = update.arrival
                if arrival_time is None:
                    continue

                # nyct-gtfs returns naive datetimes in US/Eastern
                if arrival_time.tzinfo is None:
                    arrival_time = arrival_time.replace(tzinfo=ZoneInfo("America/New_York"))

                delta = (arrival_time - datetime.now(arrival_time.tzinfo)).total_seconds()
                minutes = int(delta // 60)
                if minutes < 0:
                    continue

                entry = {
                    "line": route,
                    "destination": trip.headsign_text or "",
                    "minutes_away": minutes,
                }

                if update.stop_id.endswith("N"):
                    northbound.append(entry)
                else:
                    southbound.append(entry)

    northbound.sort(key=lambda x: x["minutes_away"])
    southbound.sort(key=lambda x: x["minutes_away"])

    return {
        "northbound": northbound[:max_per_direction],
        "southbound": southbound[:max_per_direction],
    }
