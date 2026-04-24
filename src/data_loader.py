"""
data_loader.py
--------------
Loads all CSV files into pandas DataFrames and converts them into the
domain objects from models.py.

WHY A SEPARATE LOADER MODULE:
- Single Responsibility Principle -> one module = one job.
- If tomorrow we switch from CSV to SQL, only this file changes.
- Makes the rest of the code testable (other modules depend on objects,
  not on file paths).

Pandas notes (answer these if a judge asks):
- read_csv(parse_dates=[...])   -> converts the date column to datetime64
                                  so we can do date arithmetic.
- dropna(subset=[...])          -> drops rows missing CRITICAL fields only.
- .fillna(0)                    -> replaces missing numeric values with 0.
- .astype(int)                  -> enforces integer dtype after fillna.
"""

from __future__ import annotations   # lets us use forward references in type hints

import os
from datetime import datetime
from typing import Dict, List

import pandas as pd

from .models import DepartmentFees, Event, Student


# -----------------------------------------------------------------------------
# Centralised file paths. If folder layout changes, we fix one place.
# os.path.join keeps the code portable across Windows / Mac / Linux (it uses
# the OS-correct separator automatically).
# -----------------------------------------------------------------------------
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

FILES = {
    "students": os.path.join(DATA_DIR, "students.csv"),
    "events":   os.path.join(DATA_DIR, "events.csv"),
    "schedule": os.path.join(DATA_DIR, "schedule.csv"),
    "fees":     os.path.join(DATA_DIR, "fees.csv"),
}


def _safe_read_csv(path: str) -> pd.DataFrame:
    """
    Wrapper around pd.read_csv that fails loudly with a helpful message.

    Why a private helper (leading underscore):
    -> Signals to other developers "don't call me from outside this module".
       Python doesn't enforce it, but it's the standard convention.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Could not find data file: {path}. "
            "Run the app from the project root, or check the data/ folder."
        )
    return pd.read_csv(path)


def load_students() -> List[Student]:
    """Loads students.csv and returns a list of Student objects."""
    df = _safe_read_csv(FILES["students"])

    # Clean numeric columns: replace NaNs with 0 so we don't crash later.
    df["FeesPaid"] = df["FeesPaid"].fillna(0).astype(int)
    df["FeesDue"]  = df["FeesDue"].fillna(0).astype(int)

    # List comprehension -> Pythonic, one line, readable.
    # df.itertuples() is faster than iterrows() because it returns namedtuples
    # instead of full pandas Series. (Good perf fact to mention in Q&A.)
    return [
        Student(
            student_id=row.StudentID,
            name=row.Name,
            department=row.Department,
            year=int(row.Year),
            fees_paid=float(row.FeesPaid),
            fees_due=float(row.FeesDue),
        )
        for row in df.itertuples(index=False)
    ]


def load_events() -> List[Event]:
    """Loads events.csv and returns a list of Event objects."""
    # parse_dates -> pandas converts "2026-04-25" strings into real datetime64.
    df = _safe_read_csv(FILES["events"])
    df["Date"] = pd.to_datetime(df["Date"])

    events: List[Event] = []
    for row in df.itertuples(index=False):
        # Parse "HH:MM" strings into datetime.time objects.
        # datetime.strptime returns a full datetime; .time() extracts just the time.
        start = datetime.strptime(row.StartTime, "%H:%M").time()
        end   = datetime.strptime(row.EndTime,   "%H:%M").time()

        events.append(Event(
            event_id=row.EventID,
            name=row.EventName,
            date=row.Date.to_pydatetime(),   # pandas Timestamp -> native datetime
            start_time=start,
            end_time=end,
            location=row.Location,
            department=row.Department,
            cost=int(row.Cost),
            students_reached=int(row.StudentsReached),
            latitude=float(row.Latitude),
            longitude=float(row.Longitude),
            requirements=str(row.Requirements),
        ))
    return events


def load_schedule() -> pd.DataFrame:
    """Exam schedule stays a DataFrame for easy filtering/sorting."""
    df = _safe_read_csv(FILES["schedule"])
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def load_department_fees() -> List[DepartmentFees]:
    """Loads fees.csv and returns a list of DepartmentFees objects."""
    df = _safe_read_csv(FILES["fees"])
    return [
        DepartmentFees(
            department=row.Department,
            current_semester_fees=float(row.CurrentSemesterFees),
            next_semester_fees=float(row.NextSemesterFees),
        )
        for row in df.itertuples(index=False)
    ]
