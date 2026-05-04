"""Date helpers for campaign/reporting work."""

import datetime as dt


def month_date_select(prev_month: int, datetime: dt.datetime) -> str:
    """Return the last date of a previous month as 'YYYYMMDD'.

    Examples:
        month_date_select(0, today)  → last day of current month
        month_date_select(1, today)  → last day of previous month
    """
    if prev_month == 0:
        return datetime.strftime("%Y%m%d")
    elif prev_month == 1:
        return (datetime.replace(day=1) - dt.timedelta(days=1)).strftime("%Y%m%d")
    else:
        return month_date_select(
            prev_month - 1,
            (datetime.replace(day=1) - dt.timedelta(days=1)).replace(day=1),
        )


def month_range(n_months: int, base: dt.datetime = None) -> list[str]:
    """Return a list of n_months last-day strings going back from base date.

    Useful for building partition date variables without the repetition.

    Example:
        month_range(3)  → ['20250228', '20250131', '20241231']
    """
    if base is None:
        base = dt.datetime.today().replace(day=1)
    return [month_date_select(i, base) for i in range(1, n_months + 1)]
