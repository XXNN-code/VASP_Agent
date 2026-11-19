#!/usr/bin/env python3
"""Repository root entry point: ``python main.py``.

Default mode is the interactive terminal REPL (no GUI/web needed):
  python main.py                 # interactive CLI chat with the agent
  python main.py --prompt "..."  # one-shot: single instruction, print reply, exit
  python main.py --mode web      # optional browser UI (headless machines can ignore it)
"""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from src.main import main as _main

    _main()


if __name__ == "__main__":
    main()
