from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.utils import timezone

DEFAULT_TIMEZONE = 'Asia/Dhaka'


def zone_for(settings_obj):
    name = getattr(settings_obj, 'timezone', None) or DEFAULT_TIMEZONE
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        return ZoneInfo(DEFAULT_TIMEZONE)


def local_today(settings_obj):
    """Calendar date where the student is, not the UTC date on the server."""
    return timezone.now().astimezone(zone_for(settings_obj)).date()
