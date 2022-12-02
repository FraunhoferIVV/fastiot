from datetime import datetime, timezone


def get_time_now() -> datetime:
    return datetime.utcnow()


def ensure_tzinfo(v):
    # if TZ isn't provided, we assume UTC, but you can do w/e you need
    if v.tzinfo is None:
        return v.replace(tzinfo=timezone.utc)
    # else we convert to utc
    return v.astimezone(timezone.utc)
