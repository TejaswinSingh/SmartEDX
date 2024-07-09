from datetime import timedelta, date, time, datetime
from mimetypes import guess_type

from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import FileField
from django.forms import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _


def current_time():
    return timezone.now()

def current_year():
    return timezone.now().year

def current_date():
    return timezone.now().date()

def timedelta_to_years(td: timedelta):
    return td.days // 365

def timedelta_to_months(td: timedelta):
    return td.days // 30

def timedelta_to_hours(td):
    return td.seconds // 3600

def timedelta_to_mins(td: timedelta):
    return (td.seconds // 60) % 60

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

def formatted_datetime(dt: datetime) -> str:
    return dt.strftime("%b %d %Y %I:%M %p")


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
MAX_ASSIGNMENT_REVIEW_TIME = timedelta(days=7)      # 7 days
MAX_FILE_UPLOAD_SIZE = 10485760                     # 10 MB


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

ALLOWED_CONTENT_TYPES = [
    'text/plain', 'application/pdf', 
    'application/vnd.ms-powerpoint', 'application/msword', 
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.ms-excel'
]


class CustomFileField(FileField):
    """
    Same as FileField, but you can specify:
        * content_types - list containing allowed content_types. Example: ['application/pdf', 'image/jpeg']
        See for more details: https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
        * max_upload_size - a number indicating the maximum file size allowed for upload.
            2.5MB - 2621440
            5MB - 5242880
            10MB - 10485760
            20MB - 20971520
            50MB - 5242880
            100MB - 104857600
            250MB - 214958080
            500MB - 429916160
    """
    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop("content_types", [])
        self.max_upload_size = kwargs.pop("max_upload_size", 0)

        super(CustomFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(CustomFileField, self).clean(*args, **kwargs)
        file = data.file

        try:
            content_type = guess_type(file.name)[0]
            if not content_type:
                raise forms.ValidationError(_('Unknown filetype.'))
            if content_type in self.content_types:
                if file.size > self.max_upload_size:
                    raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(self.max_upload_size), filesizeformat(file.size)))
            else:
                raise forms.ValidationError(_('Filetype not supported.'))
        except AttributeError:
            pass

        return data