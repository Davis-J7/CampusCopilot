"""
run.py
------
Thin launcher so users can simply run:

    python run.py

instead of needing the `-m` flag. Useful for non-technical demo judges.
"""

from src.main import run

if __name__ == "__main__":
    run()
