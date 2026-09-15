"""
DGCA Canonical Interactive Chat REPL (R3-MIN-1.0).

Pure text interface to canonical CognitiveAgent.chat().
No /learn, /ask, /code, /analogy, or hidden mode routing (R3 §35).
"""

from __future__ import annotations

import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dgca import CognitiveAgent


def main() -> None:
    agent = CognitiveAgent()
    print("DGCA Canonical Chat Runtime (R3-MIN-1.0)")
    print("Type /quit or /exit to leave.\n")

    while True:
        try:
            line = input("DGCA> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not line:
            continue

        if line in ("/quit", "/exit"):
            print("Exiting.")
            break

        try:
            reply = agent.chat(line)
            print(reply)
            print()
        except (TypeError, ValueError, RuntimeError, KeyError) as err:
            print(f"Error: {err}\n")


if __name__ == "__main__":
    main()
