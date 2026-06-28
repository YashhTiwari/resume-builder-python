"""
main.py - Entry point for Resume Builder System.

Run:
    python main.py
"""

import sys
import os

# Ensure the project root is on sys.path so sibling modules are importable
sys.path.insert(0, os.path.dirname(__file__))

from gui import ResumeApp


def main():
    app = ResumeApp()
    app.mainloop()


if __name__ == "__main__":
    main()
