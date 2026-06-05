from datetime import datetime, timedelta


def time_diff_str(start: datetime, end: datetime) -> str:
    diff: timedelta = end - start

    total_seconds = int(diff.total_seconds())
    days: int = diff.days
    hours: int = (total_seconds % 86400) // 3600
    minutes: int = (total_seconds % 3600) // 60
    seconds: int = total_seconds % 60

    return f"{days}d {hours:02}h {minutes:02}m {seconds:02}s"
