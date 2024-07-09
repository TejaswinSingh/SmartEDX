from datetime import datetime, time
from core.models import CourseInstance
from .utils import (
    weekdays_in_range ,timedelta_to_mins, validate_condition, formatted_time,
    DAYS_OF_WEEK_CHOICES, MAX_LECTURE_DURATION, MIN_LECTURE_DURATION
)

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from unfold.admin import ModelAdmin


class CourseSchedule(models.Model):
    """ weekly lecture schedule for a course instance """

    course_instance = models.ForeignKey(
        CourseInstance,
        on_delete=models.CASCADE,
        related_name='schedule'
    )
    weekday = models.CharField(
        max_length=1,
        choices=DAYS_OF_WEEK_CHOICES
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_course_schedules'
    )

    class Meta:
        verbose_name_plural = 'course schedules'
        constraints = [
            models.UniqueConstraint(
                fields=['course_instance', 'weekday', 'start_time', 'end_time'],    # schedules must not clash
                name='%(app_label)s_%(class)s_unique'
            )
        ]

    def __str__(self):
        return f'{self.course_instance}, {DAYS_OF_WEEK_CHOICES[self.weekday]}, {self.timeslot()}'
    
    def clean(self):
        def timeslots_clash(start1, end1, start2, end2):
            # if second schedule starts during the first (or vice versa), then the timeslots clash
            if (start2 >= start1 and start2 < end1) or (start1 >= start2 and start1 < end2):
                return True
            return False
        
        if not hasattr(self, 'course_instance'):
            return
        if not isinstance(self.start_time, time) or not isinstance(self.end_time, time):
            return

        validate_condition(
            condition=(not self.course_instance.is_active),
            error_msg="Selected course instance is archived."
        )
        validate_condition(
            not (self.end_time > self.start_time),
            "End time must be greater than start time."
        )

        # convert to datetime first and then to timedelta
        # (unlike datetime.datetime, comparison operations on datetime.time are not possible )
        date = datetime.today().date()  # take any example date, like today
        start_time, endtime = datetime.combine(date, self.start_time), datetime.combine(date, self.end_time)
        duration = endtime - start_time

        validate_condition(
            duration < MIN_LECTURE_DURATION,
            f"Scheduled lecture's duration can't be less than {timedelta_to_mins(MIN_LECTURE_DURATION)} minutes."
        )
        validate_condition(
            duration > MAX_LECTURE_DURATION,
            f"Scheduled lecture's duration can't be greater than {timedelta_to_mins(MAX_LECTURE_DURATION)} minutes."
        )
        
        # fetch other schedules of the course instance that occur on the same weekday
        q = CourseSchedule.objects.filter(course_instance_id=self.course_instance.pk, weekday=self.weekday)

        # check that timeslot(start_time - end_time) doesn't clash with any schedule
        for s in q:
            if s == self:
                continue
            st, et = datetime.combine(date, s.start_time), datetime.combine(date, s.end_time)
            if timeslots_clash(start_time, endtime, st, et):
                raise ValidationError(f"Timeslot is colliding with that of schedule {s}.")

    def timeslot(self):
        return f'{formatted_time(self.start_time)} - {formatted_time(self.end_time)}'
    
    def get_dates(self):
        """ returns dates b/w course start_date and end_date that correspond to the schedule """
        return weekdays_in_range(self.course_instance.start_date, self.course_instance.end_date, int(self.weekday))


class CourseScheduleAdmin(ModelAdmin):
    list_display = ('course_instance', 'weekday', 'timeslot', 'created_at', 'updated_at', 'updated_by')

    def timeslot(self, obj):
        return obj.timeslot()
    
    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        instance.updated_by = request.user
        instance.save()
        form.save_m2m()
        return instance