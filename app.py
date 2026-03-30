"""Flask app serving real-time MTA train arrival data."""

from flask import Flask, jsonify, render_template

import config
from mta import get_arrivals

app = Flask(__name__)


@app.route("/")
def index() -> str:
    return render_template(
        "index.html",
        stations=config.STATIONS,
        refresh_interval=config.REFRESH_INTERVAL_SECONDS,
    )


@app.route("/api/arrivals")
def arrivals() -> tuple:
    results = []
    for station in config.STATIONS:
        data = get_arrivals(
            stop_id=station["stop_id"],
            lines=station["lines"],
            max_per_direction=config.MAX_ARRIVALS_PER_DIRECTION,
        )
        results.append({
            "name": station["name"],
            "stop_id": station["stop_id"],
            "lines": station["lines"],
            **data,
        })
    return jsonify(results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
