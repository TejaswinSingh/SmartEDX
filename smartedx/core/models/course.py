import uuid
from core.models import Programme

from django.db import models
from django.contrib.auth.models import User
from unfold.admin import ModelAdmin


class Course(models.Model):
    """ programme courses """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    course_code = models.CharField(max_length=20, unique=True)
    programme = models.ForeignKey(
        Programme,
        on_delete=models.PROTECT,
        related_name='courses'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_courses'
    )

    class Meta:
        verbose_name_plural = 'courses'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'course_code'],    # courses with same title but different course_code can exist
                name='%(app_label)s_%(class)s_unique'
            )
        ]

    def __str__(self):
        return f'{self.course_code} - {self.title}'


class CourseAdmin(ModelAdmin):
    list_display = (
        'title', 'course_code', 'programme', 'count_active_instances',
        'created_at', 'updated_at', 'updated_by'
    )

    def count_active_instances(self, obj):
        return len(obj.instances.filter(is_active=True))
    
    count_active_instances.short_description = 'Instances (Active)'

    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        instance.updated_by = request.user
        instance.save()
        form.save_m2m()
        return instance