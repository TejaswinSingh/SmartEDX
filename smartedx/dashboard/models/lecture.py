import uuid
from datetime import date
from dashboard.models import CourseSchedule
from .utils import formatted_date, DAYS_OF_WEEK_CHOICES

from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS


class Lecture(models.Model):
    """ lectures of a course instance, generated from its course schedule """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course_schedule = models.ForeignKey(
        CourseSchedule,
        on_delete=models.PROTECT,
        related_name='lectures'
    )
    date = models.DateField()
    is_finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_lectures'
    )

    class Meta:
        verbose_name_plural = 'lectures'
        constraints = [
            models.UniqueConstraint(
                fields=['course_schedule', 'date'],    # to prevent duplicate lectures on the same date
                name='%(app_label)s_%(class)s_unique'
            )
        ]

    def __str__(self):
        return f'{self.course_schedule.course_instance}, Date: {self.date}, Time: {self.course_schedule.timeslot()}'
    
    def clean(self):
        if not hasattr(self, 'course_schedule'):
            return
        if not isinstance(self.date, date):
            return
        c = self.course_schedule.course_instance
        if self.date < c.start_date or self.date > c.end_date:
            raise ValidationError(f"Lecture date must lie between {formatted_date(c.start_date)} and {formatted_date(c.end_date)}")
        
    def create_for_schedule(schedule: CourseSchedule, dates: list):
        lectures = []
        for d in dates:
            try:
                obj = Lecture(course_schedule=schedule, date=d)
                obj.full_clean()
                lectures.append(obj)
            except ValidationError as e:
                raise ValidationError(f'{e.message_dict[NON_FIELD_ERRORS][0]} Course Schedule - {schedule}, Date - {d}')
        # only save after all objects are validated, i.e all or none
        for l in lectures:
            l.save()

class LectureAdmin(admin.ModelAdmin):
    list_display = (
        'get_course', 'get_instructor', 'get_timeslot', 'date',
        'get_weekday', 'is_finished', 'created_at', 'updated_at', 'updated_by'
    )

    def get_course(self, obj):
        q = obj.course_schedule.course_instance
        return f'{q.course}, {q.start_date.strftime("%b %d %Y")} - {q.end_date.strftime("%b %d %Y")}'
    
    def get_instructor(self, obj):
        return obj.course_schedule.course_instance.instructor.full_name()
    
    def get_timeslot(self, obj):
        return obj.course_schedule.timeslot()
    
    def get_weekday(self, obj):
        return DAYS_OF_WEEK_CHOICES[obj.course_schedule.weekday]
    
    get_course.short_description = 'Course'
    get_timeslot.short_description = 'Timeslot'
    get_instructor.short_description = 'Instructor'
    get_weekday.short_description = 'Weekday'

    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        instance.updated_by = request.user
        instance.save()
        form.save_m2m()
        return instance