from core.models import ContentSection
from .utils import CustomFileField, MAX_FILE_UPLOAD_SIZE, ALLOWED_CONTENT_TYPES

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from unfold.admin import ModelAdmin


def file_path(instance, filename):
    return "courses/content/files/{0}".format(filename)

class SectionItemFile(models.Model):
    """ content section items of type file """

    content_section = models.ForeignKey(
        ContentSection,
        on_delete=models.CASCADE,
        related_name='items_file'
    )
    description = models.CharField(max_length=2000)
    file = CustomFileField(
        upload_to=file_path, 
        max_length=255, 
        content_types=ALLOWED_CONTENT_TYPES,
        max_upload_size=MAX_FILE_UPLOAD_SIZE
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_section_items_file'
    )

    class Meta:
        verbose_name_plural = 'section items(file)'
    
    def __str__(self):
        return self.file.name
    
    def clean(self):
        if hasattr(self, 'content_section') and not self.content_section.course_instance.is_active:
            raise ValidationError("Course instance for the selected content section is archived.")
        

class SectionItemFileAdmin(ModelAdmin):
    list_display = ('content_section', 'file', 'get_description')

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

@receiver(post_delete, sender=SectionItemFile)
def delete_file(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(save=False)