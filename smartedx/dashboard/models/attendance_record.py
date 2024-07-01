from dashboard.models import (
    Lecture,
    Student
)
from .utils import current_date

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from unfold.admin import ModelAdmin


class AttendanceRecord(models.Model):
    """ attendance records for lectures """

    lecture = models.ForeignKey(
        Lecture,
        on_delete=models.CASCADE,
        related_name='attendance_record'
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendance_record'
    )
    is_present = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_attendance_records'
    )

    class Meta:
        verbose_name_plural = 'attendance records'
        constraints = [
            models.UniqueConstraint(
                fields=['lecture', 'student'],    # a student can't have multiple attendance records for a lecture
                name='%(app_label)s_%(class)s_unique'
            )
        ]

    def __str__(self):
        return f'Lecture({self.lecture}), Student({self.student}), Present-{self.is_present}'
    
    def clean(self):
        from dashboard.models import CourseEnrollment
        
        if not hasattr(self, 'lecture') or not hasattr(self, 'student'):
            return
        if self.lecture.date != current_date():
            raise ValidationError(f"Attendance records for this lecture can only be created/updated on {self.lecture.date}.")
        if self.lecture.is_finished:
            raise ValidationError("Can't create/update attendance records for a lecture that is marked as finished.") 
        try:
            self.student.enrollments.get(course_instance_id=self.lecture.course_schedule.course_instance.pk)
        except CourseEnrollment.DoesNotExist:
            raise ValidationError("This student is not registered to attend the selected lecture.")


class AttendanceRecordAdmin(ModelAdmin):
    list_display = ('lecture', 'student', 'is_present', 'created_at', 'updated_at', 'updated_by')

    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        instance.updated_by = request.user
        instance.save()
        form.save_m2m()
        return instance