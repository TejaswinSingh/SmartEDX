import uuid
from core.models import Batch

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from unfold.admin import ModelAdmin


class Student(models.Model):
    """ batch students """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, 
        on_delete=models.PROTECT, 
        related_name='student'
    )
    batch = models.ForeignKey(
        Batch,
        on_delete=models.PROTECT,
        related_name='students'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_students'
    )

    class Meta:
        verbose_name_plural = 'students'

    def __str__(self):
        name = self.full_name()
        return f'{name}, {self.user.username}, {self.batch}'
    
    def full_name(self):
        if not self.user.first_name and not self.user.last_name:
            return f'User({self.user.username})'
        return f'{self.user.first_name} {self.user.last_name}'.strip().title()

    def clean(self):
        # Check if the user is associated with a Staff instance
        if hasattr(self, 'user') and hasattr(self.user, 'staff'):
            raise ValidationError('This user is already registered as a staff member.')
        
        
class StudentAdmin(ModelAdmin):
    list_display = (
        'full_name', 'get_roll', 'get_department', 
        'get_programme', 'get_batch', 'get_semester',
        'created_at', 'updated_at', 'updated_by'
    )

    def get_roll(self, obj):
        return f'{obj.user.username}'
    
    def get_department(self, obj):
        return obj.batch.programme.department.name

    def get_programme(self, obj):
        return obj.batch.programme.name
    
    def get_semester(self, obj):
        return obj.batch.semester
    
    def get_batch(self, obj):
        b = obj.batch
        return f'{b.admission_date.year} - {b.graduation_date.year}'
    
    get_roll.short_description = 'Username/Roll'
    get_department.short_description = 'Department'
    get_programme.short_description = 'Programme'
    get_semester.short_description = 'Semester'
    get_batch.short_description = 'Batch'

    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        instance.updated_by = request.user
        instance.save()
        form.save_m2m()
        return instance