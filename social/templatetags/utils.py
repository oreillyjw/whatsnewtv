import datetime

from django.template import Library
from django.template.defaultfilters import stringfilter
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.dateformat import format, time_format
from django.contrib.humanize.templatetags.humanize import naturaltime
from datetime import datetime, timedelta
from django.utils import timezone, formats


register = Library()

@register.filter(name='parse_date')
def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return None


@register.filter(name='currency')
def currency(dollars):
    dollars = round(float(dollars), 2)
    return "$%s%s" % (intcomma(int(dollars)), ("%0.2f" % dollars)[-3:])


@register.filter(name='elapsed')
def elapsed(timestamp, arg=None):
    """
    https://stackoverflow.com/questions/6194589/django-create-template-filter-for-nice-time
    This filter accepts a datetime and computes an elapsed time from "now".
    The elapsed time is displayed as a "humanized" string.
    Examples:
        1 minute ago
        5 minutes ago
        1 hour ago
        10 hours ago
        1 day ago
        7 days ago

    """

    time_since_insertion = timezone.now() - timestamp

    if time_since_insertion.days < 1:
        return naturaltime(timestamp)
    else:
        return formats.date_format(timestamp, arg)


# https://stackoverflow.com/questions/7481750/check-for-presence-in-a-list-django-template
@register.filter(name='ifinlist')
def ifinlist(value, list):
    return True if value in list else False
