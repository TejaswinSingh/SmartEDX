from dashboard.models import ContentSection

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from unfold.admin import ModelAdmin


class SectionItemText(models.Model):
    """ content section items of type text """

    content_section = models.ForeignKey(
        ContentSection,
        on_delete=models.CASCADE,
        related_name='items_text'
    )
    link = models.URLField(max_length=255, blank=True)
    description = models.CharField(max_length=2000)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_section_items_text'
    )

    class Meta:
        verbose_name_plural = 'section items(text)'

    def __str__(self):
        return f'Text: {self.description[:50]}'
    
    def clean(self):
        if hasattr(self, 'content_section') and not self.content_section.course_instance.is_active:
            raise ValidationError("Course instance for the selected content section is archived.")
    

class SectionItemTextAdmin(ModelAdmin):
    list_display = ('content_section', 'link', 'get_description')

    def get_description(self, obj):
        return obj.description[:50]
    
    get_description.short_description = 'Description'

    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        instance.updated_by = request.user
        instance.save()
        form.save_m2m()
        return instance