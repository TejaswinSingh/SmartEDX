from datetime import timedelta, date, time

from django.utils import timezone
from django.core.exceptions import ValidationError


def current_year():
    return timezone.now().year

def current_date():
    return timezone.now().date()

def timedelta_to_years(td: timedelta):
    return td.days // 365

def timedelta_to_months(td: timedelta):
    return td.days // 30

def timedelta_to_mins(td: timedelta):
    return int(td.total_seconds() // 60)

def weekdays_in_range(start_date: date, end_date: date, weekday: int):
    cur_date = start_date
    dates = []

    while cur_date != (end_date + timedelta(days=1)):
        if cur_date.weekday() == weekday:
            dates.append(cur_date)
        cur_date += timedelta(days=1)

    return dates

def validate_condition(condition: bool, error_msg: str):
    if condition:
        raise ValidationError(error_msg.capitalize())
    
def formatted_date(date: date):
    return date.strftime("%b %d %Y")

def formatted_time(t: time):
    return t.strftime("%I:%M %p")


# NOTE: these variables must be accessible and changeable by admin

MIN_ESTABLISHED_YEAR = 1900
MIN_PROGRAMME_DURATION = timedelta(days=1 * 365)    # 1 year
MAX_PROGRAMME_DURATION = timedelta(days=5 * 365)    # 5 years
# MAX_GRADUATION_LIMIT = timedelta(days=10 * 365)   # 10 years
MAX_COURSE_DURATION = timedelta(days=(1/2) * 365)   # 6 months
MIN_COURSE_DURATION = timedelta(days=(1/12) * 365)  # 1 month
MAX_LECTURE_DURATION = timedelta(minutes=3 * 60)    # 3 hours
MIN_LECTURE_DURATION = timedelta(minutes=30)        # 30 mins
DEFAULT_MIN_ATTENDANCE = '75.00'                    # 75 %

SEMS = '1,2,3,4,5,6,7,8'.replace(' ', '')

MONDAY = '0'
TUESDAY = '1'
WEDNESDAY = '2'
THURSDAY = '3'
FRIDAY = '4'
SATURDAY = '5'
SUNDAY = '6'

DAYS_OF_WEEK_CHOICES = {
    MONDAY: "Monday",
    TUESDAY: "Tuesday",
    WEDNESDAY: "Wednesday",
    THURSDAY: "Thursday",
    FRIDAY: "Friday",
    SATURDAY: "Saturday",
    SUNDAY: "Sunday",
}