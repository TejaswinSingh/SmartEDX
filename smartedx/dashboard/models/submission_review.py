from decimal import Decimal
from dashboard.models import AssignmentSubmission
from .utils import (
    current_time, formatted_datetime,
    MAX_ASSIGNMENT_REVIEW_TIME
)

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from unfold.admin import ModelAdmin


class SubmissionReview(models.Model):
    """ instructor reviews on assignment submissions """

    assignment_submission = models.OneToOneField(
        AssignmentSubmission,
        on_delete=models.CASCADE,
        related_name='review'
    )
    remarks = models.CharField(max_length=2000)
    grade = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('100.00'))
        ]    
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_submission_reviews'
    )

    class Meta:
        verbose_name_plural = 'submission reviews'

    def __str__(self):
        return f'review on {self.assignment_submission}'

    def clean(self):
        if not hasattr(self, 'assignment_submission') or not isinstance(self.grade, Decimal):
            return
        
        cur = current_time()
        assignment = self.assignment_submission.assignment
        end = assignment.ends_at

        if (cur - end) > MAX_ASSIGNMENT_REVIEW_TIME:
            raise ValidationError(f"Reviews for this assignment could be created till {formatted_datetime(end+MAX_ASSIGNMENT_REVIEW_TIME)} only.")
        
        if self.grade < assignment.min_grade or self.grade > assignment.max_grade:
            raise ValidationError(f"Grade assigned must be between {assignment.min_grade} and {assignment.max_grade}.")
    
    def calc_percentage(self):
        assignment = self.assignment_submission.assignment
        return ((self.grade - assignment.min_grade) / (assignment.max_grade - assignment.min_grade)) * 100
    

class SubmissionReviewAdmin(ModelAdmin):
    list_display = ('assignment_submission', 'grade', 'get_percentage', 'get_remarks')

    def get_percentage(self, obj):
        return obj.calc_percentage()
    
    def get_remarks(self, obj):
        return obj.remarks[:50]
    
    get_percentage.short_description = 'Percentage'
    get_remarks.short_description = 'Remarks'

    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        instance.updated_by = request.user
        instance.save()
        form.save_m2m()
        return instance