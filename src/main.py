"""
main.py
-------
CLI entry point for CampusCopilot.

RESPONSIBILITIES (thin layer only):
  1. Load data via data_loader.
  2. Wire up handlers that call analysis / visualization / algorithms.
  3. Run the chatbot loop.

This file should stay SHORT. Business logic lives in the dedicated modules;
main.py is just the conductor of the orchestra.

Run:
    python -m src.main          (from project root)
    # or
    python main.py              (from project root, using the thin shim below)
"""

from __future__ import annotations

import sys
from typing import List, Optional

from .algorithms import (
    binary_search_event_by_date,
    optimize_event_budget,
    select_max_events,
)
from .analysis import (
    department_student_count,
    fees_distribution,
    total_fees_collected,
    total_fees_pending,
)
from .campus_map import generate_campus_map
from .chatbot import Chatbot
from .data_loader import (
    load_department_fees,
    load_events,
    load_schedule,
    load_students,
)
from .models import DepartmentFees, Event, Student
from .visualization import (
    plot_event_dashboard,
    plot_fees_distribution,
)


# =============================================================================
# Small presentation helpers. Kept local because they're only used here.
# =============================================================================
def _banner(title: str) -> str:
    """Pretty divider for CLI output."""
    line = "=" * 60
    return f"\n{line}\n  {title}\n{line}"


def _format_currency(amount: float) -> str:
    """Indian-style comma formatting: 1,00,000 readability bonus."""
    return f"INR {amount:,.0f}"


# =============================================================================
# INTENT HANDLERS
# Each handler is a plain function (no self, no state) that returns a string.
# We use closures (functions-within-a-function) to bind them to the loaded
# data without making every handler take 5 arguments.
# =============================================================================
def build_handlers(
    students: List[Student],
    events: List[Event],
    schedule_df,
    dept_fees: List[DepartmentFees],
):
    # Get a list of all unique departments from our data to use for filtering.
    all_depts = sorted(list(set(s.department for s in students) | 
                           set(e.department for e in events)))

    def _get_target_dept(query: str) -> Optional[str]:
        """Helper to find if a department was mentioned as a distinct word in the query."""
        query_words = query.upper().split()
        for dept in all_depts:
            if dept in query_words:
                return dept
        return None

    # --------- events ---------
    def show_events(query: str = "") -> str:
        target_dept = _get_target_dept(query)
        filtered = [e for e in events if e.department == target_dept] if target_dept else events
        
        title = f"UPCOMING EVENTS ({target_dept})" if target_dept else "UPCOMING EVENTS"
        lines = [_banner(title)]
        
        for ev in sorted(filtered, key=lambda e: (e.date, e.start_time)):
            lines.append(
                f"  {ev.date.date()}  {ev.start_time}-{ev.end_time}  "
                f"[{ev.department:>4}]  {ev.name:30s}  @ {ev.location}"
            )
        
        if not filtered and target_dept:
            lines.append(f"  No events found for {target_dept}.")
        elif not target_dept:
            lines.append("\n  Tip: Try 'events in CS' to filter by department.")
            
        return "\n".join(lines)

    def show_requirements(query: str = "") -> str:
        query_lower = query.lower()
        # Look for specific event names in the query string
        matched = [e for e in events if e.name.lower() in query_lower]

        if not matched:
            return (_banner("REQUIREMENTS") + 
                    "\n  Please specify which event you're asking about.\n"
                    "  Example: 'requirements for AI Workshop'")

        lines = [_banner("EVENT REQUIREMENTS")]
        for ev in matched:
            lines.append(f"  {ev.name}:\n    -> {ev.requirements}")
        return "\n".join(lines)

    # --------- fees ---------
    def show_fees(query: str = "") -> str:
        target_dept = _get_target_dept(query)
        
        filtered_fees = [df for df in dept_fees if df.department == target_dept] if target_dept else dept_fees
        title = f"FEE STRUCTURE ({target_dept})" if target_dept else "FULL FEE STRUCTURE"
        
        lines = [_banner(title)]
        lines.append(f"  {'Dept':<10} {'Current Sem':<15} {'Next Sem':<15}")
        lines.append(f"  {'-'*40}")
        for df in filtered_fees:
            lines.append(
                f"  {df.department:<10} "
                f"{_format_currency(df.current_semester_fees):<15} "
                f"{_format_currency(df.next_semester_fees):<15}"
            )
            
        if not target_dept:
            lines.append("\n  Tip: Try 'fees for CS' to see a specific department.")
            
        return "\n".join(lines)

    # --------- schedule ---------
    def show_schedule(query: str = "") -> str:
        target_dept = _get_target_dept(query)
        df = schedule_df[schedule_df["Department"] == target_dept] if target_dept else schedule_df
        
        title = f"EXAM SCHEDULE ({target_dept})" if target_dept else "EXAM SCHEDULE"
        lines = [_banner(title)]
        
        for _, row in df.sort_values("Date").iterrows():
            lines.append(
                f"  {row['Date'].date()}  {row['StartTime']}-{row['EndTime']}  "
                f"[{row['Department']:>4}]  {row['Subject']:25s}  Room: {row['Room']}"
            )
            
        if df.empty and target_dept:
            lines.append(f"  No exams found for {target_dept}.")
            
        return "\n".join(lines)

    # --------- students ---------
    def show_students(query: str = "") -> str:
        target_dept = _get_target_dept(query)
        filtered_students = [s for s in students if s.department == target_dept] if target_dept else students
        
        counts = department_student_count(filtered_students)

        title = f"STUDENT OVERVIEW ({target_dept})" if target_dept else "STUDENT OVERVIEW"
        lines = [_banner(title)]
        lines.append(f"  Total students: {len(filtered_students)}")
        
        if not target_dept:
            lines.append("\n  Students per department:")
            for dept, n in sorted(counts.items()):
                lines.append(f"    {dept:>4}: {n}")

        return "\n".join(lines)

    # --------- map ---------
    def show_map(query: str = "") -> str:
        path = generate_campus_map(events)
        return (f"{_banner('CAMPUS MAP GENERATED')}\n"
                f"  Interactive map saved to: {path}\n"
                f"  Open it in your browser to explore.")

    # --------- optimize: THE DSA SHOWCASE ---------
    def show_optimize(query: str = "") -> str:
        lines = [_banner("ALGORITHMIC RECOMMENDATIONS")]

        # --- Greedy: Activity Selection ---
        lines.append("\n  [Greedy] Max non-overlapping events a student can attend:")
        selected = select_max_events(events)
        for ev in selected:
            lines.append(f"    - {ev.date.date()}  "
                         f"{ev.start_time}-{ev.end_time}  {ev.name}")
        lines.append(f"  Count: {len(selected)} events")

        # --- Knapsack: budget-constrained event funding ---
        sponsor_budget = 100_000
        chosen, reach = optimize_event_budget(events, sponsor_budget)
        lines.append(f"\n  [DP/Knapsack] Best events to fund under budget "
                     f"{_format_currency(sponsor_budget)}:")
        for ev in chosen:
            lines.append(f"    - {ev.name:30s}  "
                         f"cost={_format_currency(ev.cost)}  reach={ev.students_reached}")
        lines.append(f"  Total students reached: {reach}")

        # --- Binary search demo ---
        target = "2026-04-25"
        sorted_events = sorted(events, key=lambda e: e.date)
        idx = binary_search_event_by_date(sorted_events, target)
        if idx != -1:
            lines.append(f"\n  [Binary Search] First event on {target}: "
                         f"{sorted_events[idx].name}")
        else:
            lines.append(f"\n  [Binary Search] No event found on {target}.")

        # Save the combined dashboard PNG.
        chart = plot_event_dashboard(events, selected)
        lines.append(f"\n  Visual dashboard saved: {chart}")

        # Save a map with selected events highlighted.
        selected_ids = {e.event_id for e in selected}
        map_path = generate_campus_map(events, selected_ids)
        lines.append(f"  Campus map (highlighted) saved: {map_path}")

        return "\n".join(lines)

    # --------- help ---------
    def show_help(query: str = "") -> str:
        return (_banner("HELP") +
                "\n  Ask me things like:\n"
                "    'show events'            -> list all events\n"
                "    'department fees'        -> current and next semester fee structure\n"
                "    'exam schedule'          -> exam timetable\n"
                "    'show students'          -> enrollment overview\n"
                "    'campus map'             -> interactive Folium map\n"
                "    'optimize events'        -> run DSA recommendations\n"
                "    'help'                   -> this menu\n"
                "    'quit'                   -> exit\n"
                "\n  Typos are fine -- fuzzy matching handles them.")

    def do_quit(query: str = "") -> str:
        return "__QUIT__"   # sentinel the loop looks for

    return {
        "events":       show_events,
        "requirements": show_requirements,
        "fees":     show_fees,
        "schedule": show_schedule,
        "students": show_students,
        "map":      show_map,
        "optimize": show_optimize,
        "help":     show_help,
        "quit":     do_quit,
    }


# =============================================================================
# THE CLI LOOP
# =============================================================================
def run() -> None:
    print(_banner("CAMPUSCOPILOT - Intelligent University Assistant"))
    print("  Loading data...")

    # Load everything up-front so every query is instant afterwards.
    try:
        students    = load_students()
        events      = load_events()
        schedule_df = load_schedule()
        dept_fees   = load_department_fees()
    except FileNotFoundError as exc:
        # Graceful failure with a clear message (vs a Python traceback).
        print(f"\n[ERROR] {exc}")
        sys.exit(1)

    
    print("  Type 'help' for commands or 'quit' to exit.\n")

    handlers = build_handlers(students, events, schedule_df, dept_fees)
    bot = Chatbot(handlers)

    while True:
        try:
            query = input("You > ").strip()
        except (EOFError, KeyboardInterrupt):
            # Ctrl-D or Ctrl-C -> clean exit instead of an ugly traceback.
            print("\nGoodbye!")
            break

        if not query:
            continue

        response = bot.handle(query)
        if response == "__QUIT__":
            print("Goodbye!")
            break
        print(response)


if __name__ == "__main__":
    run()
