import datetime
from django.core.validators import MaxValueValidator

def current_year():
    return datetime.date.today().year

def max_value_current_year(value):
    return MaxValueValidator(current_year())(value)

MIN_YEAR_LIMIT = 1900
MAX_GRADUATION_LIMIT = 10
MIN_ADMISSION_GOBACK_LIMIT = 5