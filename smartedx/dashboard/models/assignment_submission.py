from dashboard.models import (
    SectionItemAssignment,
    Student
)
from .utils import current_time, formatted_datetime, timedelta_to_hours,timedelta_to_mins

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone
from unfold.admin import ModelAdmin


def file_path(instance, filename):
    return "courses/assignment-submissions/{0}".format(filename)

class AssignmentSubmission(models.Model):
    """ submissions for assignments """

    assignment = models.ForeignKey(
        SectionItemAssignment,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='assignment_submissions'
    )
    file = models.FileField(upload_to=file_path, max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_assignment_submissions'
    )

    class Meta:
        verbose_name_plural = 'assignment submissions'
        constraints = [
            models.UniqueConstraint(
                fields=['assignment', 'student'],   # a student can make only one submission per assignment
                name='%(app_label)s_%(class)s_unique'
            )
        ]

    def __str__(self):
        return f'submitted by {self.student.full_name()} for {self.assignment}'
    
    def clean(self):
        from dashboard.models import CourseEnrollment

        if not hasattr(self, 'assignment') or not hasattr(self, 'student'):
            return

        c = self.assignment.content_section.course_instance
        try:
            CourseEnrollment.objects.get(course_instance_id=c.pk, student_id=self.student.pk)
        except CourseEnrollment.DoesNotExist:
            raise ValidationError("This student is not registered for submitting assignments of this course.")

        cur = current_time()

        if cur < self.assignment.starts_at:
            raise ValidationError(f"Submissions for this assignment can be made after \
                {formatted_datetime(timezone.localtime(self.assignment.starts_at))}.")
        
        if cur > self.assignment.ends_at:
            raise ValidationError(f"Submissions for this assignment ended at \
                {formatted_datetime(timezone.localtime(self.assignment.ends_at))}, i.e \
                {(cur - self.assignment.ends_at).days} days, \
                {timedelta_to_hours(cur - self.assignment.ends_at)} hours, \
                {timedelta_to_mins(cur - self.assignment.ends_at)} mins ago.")

class AssignmentSubmissionAdmin(ModelAdmin):
    list_display = ('assignment', 'student', 'file', 'created_at')

    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        instance.updated_by = request.user
        instance.save()
        form.save_m2m()
        return instance
    

from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=AssignmentSubmission)
def delete_file(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(save=False)