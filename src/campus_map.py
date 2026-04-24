"""
campus_map.py
-------------
Folium-based interactive campus map showing event locations.

Folium wraps Leaflet.js -- a popular JavaScript mapping library.
We create a Python Map object, add markers, and save as a standalone HTML
file that opens in any browser. No server required.

Q&A notes on Folium:
- folium.Map(location=[lat, lon], zoom_start=N)  -> base tile layer
- folium.Marker(...)        -> pin with popup text on click
- folium.CircleMarker(...)  -> scalable dot; radius in PIXELS (not metres)
- map_obj.save("file.html") -> writes a self-contained HTML file

Defensive note: circle radius must be > 0 or folium silently skips it.
We clamp with max(1, ...) to be safe.
"""

import os
from typing import List, Optional, Set

import folium

from .models import Event


OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")


def generate_campus_map(events: List[Event], selected_ids: Optional[Set[str]] = None) -> str:
    """
    Creates a Folium map with a marker per event.
      - Green markers = events picked by the greedy scheduler.
      - Blue  markers = other events.
      - Circle size is proportional to students_reached.

    Returns the path to the saved HTML file.
    """
    if not events:
        raise ValueError("Cannot build a campus map with zero events.")

    selected_ids = selected_ids or set()

    # Centre the map on the average location of all events -- quick but effective.
    avg_lat = sum(e.latitude  for e in events) / len(events)
    avg_lon = sum(e.longitude for e in events) / len(events)

    # "OpenStreetMap" tiles are free and attribution-correct by default.
    # Setting tiles=None and re-adding would let us use custom tile providers.
    campus_map = folium.Map(
        location=[avg_lat, avg_lon],
        zoom_start=17,
        tiles="OpenStreetMap",
    )

    for ev in events:
        is_selected = ev.event_id in selected_ids
        color = "green" if is_selected else "blue"

        # Human-readable popup -- triple-quoted f-string for multi-line HTML.
        popup_html = f"""
        <b>{ev.name}</b><br>
        Date: {ev.date.date()}<br>
        Time: {ev.start_time} - {ev.end_time}<br>
        Location: {ev.location}<br>
        Students Reached: {ev.students_reached}<br>
        Cost: INR {ev.cost}<br>
        <b>Requirements:</b> {ev.requirements}
        """

        # Pin marker (click to open popup).
        folium.Marker(
            location=[ev.latitude, ev.longitude],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=ev.name,
            icon=folium.Icon(color=color, icon="info-sign"),
        ).add_to(campus_map)

        # Circle overlay whose size shows the event's reach.
        # max(1, ...) guards against a zero-radius circle being skipped.
        folium.CircleMarker(
            location=[ev.latitude, ev.longitude],
            radius=max(1, ev.students_reached / 20),
            color=color,
            fill=True,
            fill_opacity=0.3,
        ).add_to(campus_map)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, "campus_map.html")
    campus_map.save(path)
    return path
