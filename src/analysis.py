"""
analysis.py
-----------
Financial & student analytics functions. Pure pandas/NumPy work -- no plotting
(that's visualization.py's job) and no user interaction.

Keeping analysis pure means every function here is unit-testable: pass in a
DataFrame, get out a DataFrame or a number. Easy to verify in Q&A:
>>> from src.analysis import department_utilization
>>> department_utilization(finance_df)
"""

from typing import Dict, List

import numpy as np
import pandas as pd

from .models import Student


def fees_distribution(students: List[Student]) -> Dict[str, float]:
    """
    Returns {department -> total_fees_paid} for a pie chart.

    Note we accept a list of Student objects (not a DataFrame). That's the
    benefit of OOP: downstream code doesn't need to know the CSV schema.
    """
    distribution: Dict[str, float] = {}
    for s in students:
        # dict.get(key, default) avoids KeyError on first sighting of a dept.
        distribution[s.department] = distribution.get(s.department, 0) + s.fees_paid
    return distribution


def total_fees_collected(students: List[Student]) -> float:
    """sum() with a generator expression -- no intermediate list built."""
    return sum(s.fees_paid for s in students)


def total_fees_pending(students: List[Student]) -> float:
    return sum(s.fees_due for s in students)


def department_student_count(students: List[Student]) -> Dict[str, int]:
    """Count students per department -- showcases dict usage cleanly."""
    counts: Dict[str, int] = {}
    for s in students:
        counts[s.department] = counts.get(s.department, 0) + 1
    return counts
