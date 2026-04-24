"""
algorithms.py
-------------
THE DSA SHOWCASE MODULE. This is the technical heart of CampusCopilot.

Contains four classical algorithms, each mapped to a concrete feature:

  1. Levenshtein Distance      (Dynamic Programming)
       -> Fuzzy chatbot matching (typo tolerance: "evnts" -> "events").
  2. Activity Selection        (Greedy)
       -> Picks the maximum number of non-overlapping events a student
          can attend in a day.
  3. 0/1 Knapsack              (Dynamic Programming)
       -> Given a sponsorship budget, chooses events to fund that
          maximise total student reach.
  4. Binary Search             (Divide & Conquer)
       -> Finds events by target date in O(log n) instead of O(n).

Why these four:
- Each algorithm solves a DIFFERENT real feature, not bolted-on.
- Together they cover DP (x2), Greedy, and Binary Search -- a wide
  sweep of your DSA syllabus in one module.

Big-O summary (memorise for Q&A):
  Levenshtein:    O(m * n) time, O(m * n) space
  Activity Sel.:  O(n log n) time (dominated by the sort)
  Knapsack:       O(n * W) time, O(n * W) space  (pseudo-polynomial)
  Binary Search:  O(log n) time
"""

from typing import List, Optional, Tuple

from .models import Event


# =============================================================================
# 1. LEVENSHTEIN DISTANCE  (Dynamic Programming)
# =============================================================================
def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Computes the minimum number of single-character edits (insert, delete,
    or substitute) to turn s1 into s2.

    Why DP?  The recursive version recomputes the same subproblems over and
    over, which is exponential. We fill a 2-D table so each subproblem is
    solved once -> O(m*n).

    Recurrence:
        dp[i][j] = dp[i-1][j-1]                      if s1[i-1] == s2[j-1]
                 = 1 + min(dp[i-1][j],   # delete
                           dp[i][j-1],   # insert
                           dp[i-1][j-1]) # substitute   otherwise

    Base cases:
        dp[0][j] = j   (empty -> j inserts to build s2[:j])
        dp[i][0] = i   (i deletes to go from s1[:i] -> empty)
    """
    m, n = len(s1), len(s2)

    # Build a (m+1) x (n+1) table initialised to 0.
    # The +1 is because we include the "empty prefix" row/column.
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Base cases: cost of transforming to/from an empty string.
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    # Fill the table row-by-row.
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                # Characters match -> no edit needed, inherit diagonal.
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],      # delete from s1
                    dp[i][j - 1],      # insert into s1
                    dp[i - 1][j - 1],  # substitute
                )

    return dp[m][n]


def find_closest_keyword(user_word: str, keywords: List[str], max_distance: int = 3) -> Optional[str]:
    """
    Uses Levenshtein to find the keyword closest to what the user typed.

    Returns None if nothing is within `max_distance` edits -- we'd rather
    say "I didn't understand" than confidently match the wrong intent.
    """
    user_word = user_word.lower().strip()
    best_match, best_distance = None, float("inf")

    for kw in keywords:
        d = levenshtein_distance(user_word, kw.lower())
        if d < best_distance:
            best_distance, best_match = d, kw

    return best_match if best_distance <= max_distance else None


# =============================================================================
# 2. ACTIVITY SELECTION  (Greedy)
# =============================================================================
def select_max_events(events: List[Event]) -> List[Event]:
    """
    Classic Activity Selection problem.
    Returns the maximum number of non-overlapping events a student could
    attend in a single day.

    GREEDY STRATEGY:
      Sort events by END time, then iterate and always pick the next event
      whose start >= the end of the last picked event.

    Why this greedy choice is OPTIMAL (important for Q&A):
      Picking the earliest-ending event leaves the maximum room for
      subsequent events. This is provable by an exchange argument:
      swapping in the earliest-ending event never reduces the final count.

    Time:  O(n log n)  -- dominated by the sort.
    Space: O(n)        -- for the result list.
    """
    if not events:
        return []

    # sorted() returns a NEW list -- doesn't mutate the caller's data.
    # "key=lambda" is a tiny anonymous function: sort by end-time.
    sorted_events = sorted(events, key=lambda e: (e.date, e.end_time))

    selected: List[Event] = [sorted_events[0]]
    for ev in sorted_events[1:]:
        last = selected[-1]
        # Non-overlap check via the domain method on Event (SRP).
        if not ev.conflicts_with(last):
            selected.append(ev)

    return selected


# =============================================================================
# 3. 0/1 KNAPSACK  (Dynamic Programming)
# =============================================================================
def optimize_event_budget(
    events: List[Event],
    budget: int,
) -> Tuple[List[Event], int]:
    """
    0/1 Knapsack: given a sponsorship budget, pick the subset of events that
    maximises total students_reached without exceeding budget.

    Why 0/1 and not fractional: you can't run "half an event".

    Recurrence:
      dp[i][w] = max(
          dp[i-1][w],                                   # skip event i
          dp[i-1][w - cost_i] + reach_i  (if cost_i<=w) # take event i
      )

    Time:  O(n * W)   n = #events, W = budget
    Space: O(n * W)   (can be reduced to O(W) but we keep 2-D for clarity
                       and for easier backtracking to reconstruct the picks).

    Returns: (list_of_chosen_events, total_students_reached)
    """
    n = len(events)
    if n == 0 or budget <= 0:
        return [], 0

    # dp[i][w] = best reach using first i events with capacity w.
    dp = [[0] * (budget + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        ev = events[i - 1]
        for w in range(budget + 1):
            # Option A: skip this event.
            dp[i][w] = dp[i - 1][w]
            # Option B: take this event if it fits.
            if ev.cost <= w:
                dp[i][w] = max(
                    dp[i][w],
                    dp[i - 1][w - ev.cost] + ev.students_reached,
                )

    # ---- Backtrack to reconstruct WHICH events were chosen ----
    # Starting from dp[n][budget], walk backwards: if the value differs from
    # the row above, that event was taken.
    chosen: List[Event] = []
    w = budget
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            ev = events[i - 1]
            chosen.append(ev)
            w -= ev.cost
    chosen.reverse()   # restore original order

    return chosen, dp[n][budget]


# =============================================================================
# 4. BINARY SEARCH  (for locating events by date)
# =============================================================================
def binary_search_event_by_date(
    sorted_events: List[Event],
    target_date_str: str,
) -> int:
    """
    Standard iterative binary search.

    PRECONDITION: `sorted_events` MUST already be sorted by date ascending.
    (Binary search on unsorted data is a classic bug we avoid.)

    Returns the index of the first event on `target_date_str` (YYYY-MM-DD),
    or -1 if none exists.

    Time:  O(log n)
    Space: O(1)
    """
    from datetime import datetime as _dt
    target = _dt.strptime(target_date_str, "%Y-%m-%d").date()

    low, high = 0, len(sorted_events) - 1
    while low <= high:
        # (low + high) // 2 is fine in Python (no integer overflow), but
        # low + (high - low) // 2 is the overflow-safe idiom carried from C/Java.
        mid = low + (high - low) // 2
        mid_date = sorted_events[mid].date.date()

        if mid_date == target:
            return mid
        elif mid_date < target:
            low = mid + 1
        else:
            high = mid - 1

    return -1   # sentinel: "not found"
