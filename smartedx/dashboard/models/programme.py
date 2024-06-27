import uuid
from datetime import timedelta
from dashboard.models import Department
from .utils import (
    current_date, timedelta_to_years,
    MAX_PROGRAMME_DURATION, MIN_PROGRAMME_DURATION, 
)

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from unfold.admin import ModelAdmin


class Programme(models.Model):
    """ department programmes """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='programmes'
    )
    duration = models.IntegerField()    # in years
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_programmes'
    )

    class Meta:
        verbose_name_plural = 'programmes'

    def __str__(self):
        return f'{self.name}, {self.department}'
    
    @property
    def duration_td(self):
        return timedelta(days=self.duration * 365)
        
    def get_current_batches(self):
        # lookup active batches only
        return self.batches.filter(graduation_date__gt=current_date(), has_graduated=False)

    def get_current_students(self):
        from dashboard.models import Student
        q = Student.objects.none() # empty queryset
        for b in self.get_current_batches():
            q |= b.students.all()
        return q
    
    def clean(self):
        if not isinstance(self.duration, int):
            return
        l, u = timedelta_to_years(MIN_PROGRAMME_DURATION), timedelta_to_years(MAX_PROGRAMME_DURATION)
        if self.duration < l or self.duration > u:
            raise ValidationError(f"Duration must lie between {l} and {u} years")
        
    
class ProgrammeAdmin(ModelAdmin):
    list_display = (
        'name', 'department', 'get_duration', 
        'count_courses', 'count_batches', 'count_students',
        'created_at', 'updated_at', 'updated_by'
    )

    def get_duration(self, obj):
        return obj.duration
    
    def count_courses(self, obj):
        return len(obj.courses.all())
    
    def count_batches(self, obj):
        return len(obj.get_current_batches())
    
    def count_students(self, obj):
        return len(obj.get_current_students())
    
    get_duration.short_description = 'Duration (years)'
    count_courses.short_description = 'Courses'
    count_batches.short_description = 'Batches'
    count_students.short_description = 'Students'

    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        instance.updated_by = request.user
        instance.save()
        form.save_m2m()
        return instance