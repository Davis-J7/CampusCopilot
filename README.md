# CampusCopilot — Intelligent University Assistant

An interactive command-line university assistant that combines pandas analytics,
matplotlib/Folium visualisation, and four classical DSA algorithms behind a
fuzzy-matching chatbot.

Built for a 5-hour hackathon by a team of 5.

---

## Quick Start (VS Code)

1. Open the project folder in VS Code: `File → Open Folder… → campuscopilot/`
2. Open an integrated terminal: `` Ctrl+` `` (backtick)
3. Create & activate a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Mac / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the app:
   ```bash
   python run.py
   ```
6. Try these queries:
   - `help`
   - `show events`
   - `fees`
   - `exam schedule`
   - `show students`
   - `campus map`
   - `optimize events` ← this is the DSA showcase
   - `evnts` (intentional typo — fuzzy matching will still resolve it)
   - `quit`

PNG charts are written to `output/`, and the Folium map opens as
`output/campus_map.html` (double-click it in VS Code's file explorer).

---

## Project Structure

```
campuscopilot/
├── data/                      # CSV input files (source of truth)
│   ├── students.csv
│   ├── finance.csv
│   ├── events.csv
│   └── schedule.csv
│
├── src/                       # All Python source
│   ├── __init__.py
│   ├── models.py              # OOP domain classes (Student, Event, Department)
│   ├── data_loader.py         # CSV → Python objects / DataFrames
│   ├── algorithms.py          # DSA: Levenshtein, Greedy, Knapsack, Binary Search
│   ├── analysis.py            # Pure pandas analytics
│   ├── visualization.py       # matplotlib charts
│   ├── campus_map.py          # Folium interactive map
│   ├── chatbot.py             # Intent classifier + Command-pattern dispatcher
│   └── main.py                # CLI loop, wiring
│
├── output/                    # Generated charts & map (created on first run)
├── run.py                     # Thin launcher (python run.py)
├── requirements.txt
└── README.md
```

---

## Algorithms Used (the 25% Python-Concepts score)

| # | Algorithm | Paradigm | Where It's Used | Complexity |
|---|-----------|----------|-----------------|------------|
| 1 | Levenshtein Distance | Dynamic Programming | Fuzzy keyword matching for typo-tolerant chatbot | O(m·n) |
| 2 | Activity Selection | Greedy | Max non-overlapping events a student can attend | O(n log n) |
| 3 | 0/1 Knapsack | Dynamic Programming | Best events to fund under a sponsor budget (max student reach) | O(n·W) |
| 4 | Binary Search | Divide & Conquer | Locating events by date in sorted list | O(log n) |
| 5 | Hash-table lookup | Data Structure | O(1) intent-keyword matching in the chatbot | O(1) avg |

All four are implemented **from scratch** in `src/algorithms.py` — no
third-party algorithm library.

---

## Python Concepts Demonstrated

- **OOP**: `@dataclass`, properties, instance methods (`Event.conflicts_with`)
- **Type hints**: on every public function
- **List / dict / generator comprehensions**
- **Decorators**: `@dataclass`, `@property`, `@staticmethod`
- **Error handling**: custom `FileNotFoundError` message, graceful Ctrl-C exit
- **Modules & packages**: relative imports (`from .models import ...`)
- **Design patterns**: Command (intent → handler dict), Single Responsibility
- **Closures**: handlers bind to data without globals
- **File I/O**: CSV read, PNG write, HTML write
- **pandas**: `read_csv`, `groupby`, `agg`, `merge`, vectorised ops
- **NumPy**: `np.where` for vectorised branching
- **matplotlib**: `subplots`, `tight_layout`, non-interactive `Agg` backend
- **Folium**: `Map`, `Marker`, `CircleMarker`, popups

---

## Library Cheat-Sheet (for Q&A)

**pandas** — data-analysis library built on NumPy.
- `pd.read_csv(path, parse_dates=[...])` — loads CSV; `parse_dates` converts
  string columns to `datetime64`.
- `df.groupby(col).agg({...})` — split-apply-combine. Aggregates each group.
- `df.itertuples(index=False)` — faster than `iterrows()` (returns namedtuples,
  not Series).
- `pd.to_datetime(s)` — converts strings to datetimes.

**NumPy** — n-dimensional arrays and vectorised maths.
- `np.where(cond, a, b)` — vectorised if/else, runs in C.

**matplotlib** — plotting library.
- `matplotlib.use("Agg")` — switches to non-interactive backend (no window).
- `plt.subplots(r, c)` — creates figure + grid of axes.
- `ax.bar / ax.plot / ax.pie / ax.scatter` — chart types used.
- `plt.close(fig)` — releases memory; important when generating many charts.

**Folium** — Python wrapper for Leaflet.js mapping.
- `folium.Map(location=[lat,lon], zoom_start=N)` — base map.
- `folium.Marker(...)`, `folium.CircleMarker(...)` — markers.
- `.save("file.html")` — writes a self-contained interactive HTML file.

---

## Division of Work (Team of 5, 5 Hours)

| Person | Files owned | Deliverable |
|--------|-------------|-------------|
| 1 | `data/*.csv`, `models.py`, `data_loader.py` | Data layer ready in 1.5h |
| 2 | `algorithms.py` | All four algorithms + unit tests |
| 3 | `analysis.py`, `visualization.py` | Analytics + all four charts |
| 4 | `campus_map.py`, `chatbot.py` | Map + intent classifier |
| 5 | `main.py`, `run.py`, integration, demo prep | CLI, end-to-end testing, slides |

Timeline:
- 0:00–0:30 — Setup: clone repo, agree interfaces, Person 1 publishes CSVs.
- 0:30–3:30 — Parallel implementation per the table.
- 3:30–4:15 — Integration & end-to-end test (Person 5 driving).
- 4:15–4:45 — Demo script rehearsal + Q&A prep.
- 4:45–5:00 — Buffer for last-minute fixes.

---

## 2-Minute Demo Script

> **"Hi judges. We built CampusCopilot — an intelligent university assistant
> that solves a real problem: students and admin staff waste time hunting
> through portals for fees, events, and schedules. Our tool is a single
> chatbot that answers all of it — AND uses classical algorithms to make
> smart recommendations.**
>
> *[Type `help`]*
>
> **Here's our command menu. It accepts natural-language queries. Watch —
> let me type `evnts` with a typo. It still works, because under the hood
> we use the Levenshtein distance dynamic-programming algorithm for fuzzy
> matching.**
>
> *[Type `fees`]*
>
> **Financial overview: fees collected, pending, department utilization.
> Charts are auto-generated — here's the bar chart, the monthly trend line,
> and the pie chart.**
>
> *[Type `optimize events`]*
>
> **This is our DSA showcase. First, the Greedy activity-selection algorithm
> finds the maximum non-overlapping events a student can attend. Second,
> the 0/1 Knapsack algorithm — dynamic programming — picks which events the
> university should sponsor to maximize student reach under a 1-lakh budget.
> Third, a binary search in O(log n) finds events by date.**
>
> *[Open `output/campus_map.html`]*
>
> **And our interactive Folium map highlights the chosen events in green.**
>
> **The whole system is modular — four DSA algorithms, clean pandas analytics,
> and a keyword + fuzzy-matching chatbot. 500 lines of code, fully documented,
> zero ML black boxes — every decision is explainable. Thank you."**

---

## Anticipated Judge Questions & Answers

**Q: Why not use a real NLP library like spaCy or a transformer?**
A: For a closed-vocabulary campus assistant, keyword + fuzzy matching is
genuinely sufficient and fully explainable. A transformer would be a black
box we can't defend in Q&A. Our approach also showcases the Levenshtein DP
algorithm directly.

**Q: Why 0/1 Knapsack instead of Fractional Knapsack?**
A: You can't fund half an event. 0/1 is the correct physical model. Fractional
would be Greedy, but it doesn't fit the problem.

**Q: What's the time complexity of your chatbot?**
A: Per query: O(T · K) where T = tokens in query, K = total keywords. Exact
matching is O(1) per keyword via hash-set lookup. Fuzzy fallback adds
Levenshtein's O(m·n) per unmatched token — capped by our `max_distance=2` bail.

**Q: Why keep finance as a DataFrame but students as a list of objects?**
A: Finance needs heavy groupby/aggregation — pandas excels at that. Student
records need domain methods like `is_defaulter` and `total_fees` — OOP
expresses that cleanly. We use the right tool per job.

**Q: How do you handle missing data?**
A: `data_loader.py` uses `fillna(0)` on numeric columns and `dropna` on
critical string columns, plus a `FileNotFoundError` wrapper that surfaces a
clear message if a CSV is absent.

**Q: How would you scale this?**
A: Three hooks: (1) swap `data_loader` to read from SQL instead of CSV — no
other file changes; (2) cache `build_departments` results; (3) the 0/1
Knapsack can be reduced to O(W) space for larger budgets.

**Q: Why Agg backend for matplotlib?**
A: Non-interactive rendering. Runs headlessly (no GUI required), which is
critical if we demo in a cloud IDE or a locked-down lab machine.

---

## Key Insights the Project Surfaces

1. **Department budget health** — at a glance you can see which departments
   are overspending vs under-utilising their budgets.
2. **Fee collection gaps** — defaulter list with exact pending amounts.
3. **Event scheduling optimum** — most students currently double-book; our
   greedy scheduler shows the optimum non-overlapping plan.
4. **Sponsorship ROI** — knapsack reveals the cost-per-student-reached
   trade-off; the highest-reach event is not always the best sponsorship
   choice once its cost is factored in.
