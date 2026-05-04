"""Miscellaneous helpers."""

import pandas as pd

from btools.db.oracle import oracle_execute


def drop_tmp_tables(query_list: list[str]) -> None:
    """Attempt to drop each table in query_list, silently skip if not found."""
    for i, query in enumerate(query_list):
        try:
            oracle_execute(query)
            print(f"  [{i + 1}] dropped")
        except Exception:
            print(f"  [{i + 1}] not found, skipping")


def set_float_format() -> None:
    """Set pandas display format to 2 decimal places with thousands separator."""
    pd.set_option("display.float_format", lambda x: "{:,.2f}".format(x))
