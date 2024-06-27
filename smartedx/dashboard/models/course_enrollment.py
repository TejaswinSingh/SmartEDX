from dashboard.models import (
    CourseInstance,
    Student
)

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from unfold.admin import ModelAdmin


class CourseEnrollment(models.Model):
    """ records of students enrolling for a particular course-instance """

    course_instance = models.ForeignKey(
        CourseInstance,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_course_enrollments'
    )

    class Meta:
        verbose_name_plural = 'course enrollments'
        constraints = [
            models.UniqueConstraint(
                fields=['course_instance', 'student'],   # a student can't enroll for a course more than once
                name='%(app_label)s_%(class)s_unique'
            )
        ]

    def __str__(self):
        return f'Course-Enrollment({self.student}, {self.course_instance})'
    
    def clean(self):
        if not hasattr(self, 'course_instance') or not hasattr(self, 'student'):
            return
        if not self.course_instance.is_active:
            raise ValidationError("Selected course instance is archived")
        
        if self.student.batch != self.course_instance.batch:
            raise ValidationError("Selected student doesn't belong to the batch associated with the course instance")


class CourseEnrollmentAdmin(ModelAdmin):
    list_display = ('course_instance', 'student', 'created_at', 'updated_at', 'updated_by')

    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        instance.updated_by = request.user
        instance.save()
        form.save_m2m()
        return instance