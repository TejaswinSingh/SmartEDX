from decimal import Decimal
from datetime import datetime
from dashboard.models import ContentSection

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from unfold.admin import ModelAdmin


def file_path(instance, filename):
    return "courses/content/assignments/{0}".format(filename)

class SectionItemAssignment(models.Model):
    """ content section items of type assignment """

    content_section = models.ForeignKey(
        ContentSection,
        on_delete=models.CASCADE,
        related_name='items_assignment'
    )
    description = models.CharField(max_length=2000)
    file = models.FileField(upload_to=file_path, max_length=255)
    min_grade = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=Decimal('0.0'),
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('100.00'))
        ]    
    )
    max_grade = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=Decimal('10.0'),
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('100.00'))
        ]    
    )
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_section_items_assignment'
    )

    class Meta:
        verbose_name_plural = 'section items(assignment)'
    
    def __str__(self):
        return f'Assignment: {self.file.name}'
    
    def clean(self):
        if hasattr(self, 'content_section') and not self.content_section.course_instance.is_active:
            raise ValidationError("Course instance for the selected content section is archived.")
        
        if not isinstance(self.starts_at, datetime) or not isinstance(self.ends_at, datetime):
            return
        
        if not self.ends_at > self.starts_at:
            raise ValidationError("Ends at time must be greater than starts at time.")
        
        c = self.content_section.course_instance
        if self.starts_at.date() < c.start_date or self.starts_at.date() > c.end_date:
            raise ValidationError(f"Assignment must start between the dates, {c.start_date} and {c.end_date}.")
        
        if self.ends_at.date() < c.start_date or self.ends_at.date() > c.end_date:
            raise ValidationError(f"Assignment must end between the dates, {c.start_date} and {c.end_date}.")
        
        if not isinstance(self.min_grade, Decimal) or not isinstance(self.max_grade, Decimal):
            return
        
        if not self.max_grade > self.min_grade:
            raise ValidationError("Max grade must be greater than min grade.")
    

class SectionItemAssignmentAdmin(ModelAdmin):
    list_display = (
        'content_section', 'file', 'get_description', 
        'min_grade', 'max_grade', 'starts_at', 'ends_at'
    )

    def get_description(self, obj):
        return obj.description[:50]
    
    get_description.short_description = 'Description'

    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        instance.updated_by = request.user
        instance.save()
        form.save_m2m()
        return instance
    

from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=SectionItemAssignment)
def delete_file(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(save=False)