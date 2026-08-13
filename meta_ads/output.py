"""Formatting helpers for CLI output."""
from __future__ import annotations

import json
from typing import Any


def print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, sort_keys=False))


def print_table(rows: list[dict[str, Any]], columns: list[str] | None = None) -> None:
    if not rows:
        print("(no results)")
        return
    columns = columns or list(rows[0].keys())
    try:
        from tabulate import tabulate

        table = [[_cell(r.get(c)) for c in columns] for r in rows]
        print(tabulate(table, headers=columns, tablefmt="github"))
        return
    except ImportError:
        pass

    widths = [max(len(c), *(len(_cell(r.get(c))) for r in rows)) for c in columns]
    header = "  ".join(c.ljust(w) for c, w in zip(columns, widths))
    print(header)
    print("  ".join("-" * w for w in widths))
    for r in rows:
        print("  ".join(_cell(r.get(c)).ljust(w) for c, w in zip(columns, widths)))


def _cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    return str(value)
