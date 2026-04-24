"""
visualization.py
----------------
All matplotlib plotting lives here.

Design rule: plotting functions ACCEPT already-processed data. They do NOT
compute analytics themselves. This keeps analysis (analysis.py) and
presentation (this file) separate -- a core software-design principle.

Q&A notes on matplotlib:
- plt.figure(figsize=(w,h))  -> fresh figure in inches
- plt.subplots(r, c)         -> returns (fig, axes); axes is a NumPy array
                                of AxesSubplot objects for multi-panel plots.
- plt.tight_layout()         -> auto-adjusts spacing so labels don't overlap.
- plt.savefig(path, dpi=...) -> writes PNG; higher dpi = sharper.
"""

import os
from typing import Dict, List

import matplotlib

# "Agg" is a NON-INTERACTIVE backend -- renders to file without opening a
# window. Important for headless servers and for the hackathon demo where
# we want reliable screenshot-able output. Must be set BEFORE importing pyplot.
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402  (intentional import-after-config)

import pandas as pd

from .models import Event


# Where we save chart PNGs. Created lazily on first plot.
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")


def _ensure_output_dir() -> None:
    """Create output/ if missing. os.makedirs(exist_ok=True) = idempotent."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def plot_fees_distribution(distribution: Dict[str, float]) -> str:
    """Pie chart of fees collected per department."""
    _ensure_output_dir()

    fig, ax = plt.subplots(figsize=(8, 8))
    labels = list(distribution.keys())
    sizes  = list(distribution.values())

    ax.pie(sizes,
           labels=labels,
           autopct="%1.1f%%",          # each slice's % with 1 decimal
           startangle=90,               # start at 12 o'clock, clockwise
           wedgeprops={"edgecolor": "white", "linewidth": 2})
    ax.set_title("Fees Collected by Department")
    ax.axis("equal")   # keep it circular, not elliptical

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fees_distribution.png")
    plt.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_event_dashboard(events: List[Event], selected: List[Event]) -> str:
    """
    2x1 subplot dashboard:
      - Top:    All events coloured by whether they made the greedy selection.
      - Bottom: Cost vs students_reached scatter -> shows knapsack trade-off.

    This single plot demonstrates plt.subplots() AND directly visualises two
    of our algorithms. Great demo-talking-point.
    """
    _ensure_output_dir()

    fig, axes = plt.subplots(2, 1, figsize=(12, 9))
    selected_ids = {e.event_id for e in selected}   # set -> O(1) lookup

    # ---- Top panel: event timeline (selected vs not) ----
    names  = [e.name for e in events]
    counts = [e.students_reached for e in events]
    colors = ["#5cb85c" if e.event_id in selected_ids else "#d9d9d9" for e in events]

    axes[0].barh(names, counts, color=colors, edgecolor="black")
    axes[0].set_xlabel("Students Reached")
    axes[0].set_title("Events (Green = picked by greedy scheduler)")
    axes[0].invert_yaxis()   # first event on top

    # ---- Bottom panel: cost vs reach (knapsack trade-off) ----
    costs    = [e.cost for e in events]
    reaches  = [e.students_reached for e in events]
    axes[1].scatter(costs, reaches, s=100, c="#0275d8", alpha=0.7, edgecolors="black")
    for e in events:
        axes[1].annotate(e.name[:10], (e.cost, e.students_reached), fontsize=8)
    axes[1].set_xlabel("Cost (Rupees)")
    axes[1].set_ylabel("Students Reached")
    axes[1].set_title("Event Cost vs Student Reach (Knapsack Trade-off)")
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "event_dashboard.png")
    plt.savefig(path, dpi=120)
    plt.close(fig)
    return path
