from dashboard.models import CourseInstance

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from unfold.admin import ModelAdmin


class ContentSection(models.Model):
    """ CourseInstance content sections """

    course_instance = models.ForeignKey(
        CourseInstance,
        on_delete=models.CASCADE,
        related_name='content_sections'
    )
    title = models.CharField(max_length=255)
    order = models.PositiveSmallIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_content_sections'
    )

    class Meta:
        verbose_name_plural = 'content sections'
        constraints = [
            models.UniqueConstraint(
                fields=['course_instance', 'order'],    # each content section in a course must have a unique order no.
                name='%(app_label)s_%(class)s_unique'
            )
        ]

    def __str__(self):
        return f'{self.course_instance}, Section: {self.title}'
    
    def clean(self):
        if hasattr(self, 'course_instance') and not self.course_instance.is_active:
            raise ValidationError("Selected course instance is archived.")
    

class ContentSectionAdmin(ModelAdmin):
    list_display = ('course_instance', 'title', 'order', 'updated_by')

    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        instance.updated_by = request.user
        instance.save()
        form.save_m2m()
        return instance