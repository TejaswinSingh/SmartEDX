import uuid
from dashboard.models import (
    Department,
    StaffRole
)

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from unfold.admin import ModelAdmin


def validate_role(instance):
    """ validates role field constraints """

    def validate_only_one():
        try:
            s = Staff.objects.get(role=instance.role)
            # if the object returned is same as instance, then pass
            if s != instance:
                raise ValidationError('A staff member with this role already exists.')
        except Staff.DoesNotExist:
            pass

    def validate_one_per_dept():
        try:
            s = Staff.objects.get(department=instance.department, role=instance.role)
            if s != instance:
                raise ValidationError(f'A staff member with this role already exists in {instance.department}.')
        except Staff.DoesNotExist:
            pass

    def validate_only_for_dept():
        if instance.department != instance.role.only_for_dept:
            raise ValidationError(f'This role can be assigned only for staff in {instance.role.only_for_dept}.')

    if instance.role.only_one:
        validate_only_one()
    if instance.role.one_per_dept:
        validate_one_per_dept()
    if instance.role.only_for_dept:
        validate_only_for_dept()


class Staff(models.Model):
    """ department staff """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, 
        on_delete=models.PROTECT, 
        related_name='staff'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='staff'
    )
    role = models.ForeignKey(
        StaffRole,
        on_delete=models.PROTECT,
        related_name='staff'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_staff'
    )

    class Meta:
        verbose_name_plural = 'staff'

    def __str__(self):
        name = self.full_name()
        return f'{name}, {self.role}, {self.department}'
    
    def full_name(self):
        if not self.user.first_name and not self.user.last_name:
            return f'User({self.user.username})'
        return f'{self.user.first_name} {self.user.last_name}'.strip().title()

    def clean(self):   
        if not hasattr(self, 'user') or not hasattr(self, 'role') or not hasattr(self, 'department'):
            return
            
        # check role constraints
        validate_role(self)
        # Check if the user is associated with a Student instance
        if hasattr(self.user, 'student'):
            raise ValidationError('This user is already registered as a student.')
        

class StaffAdmin(ModelAdmin):
    list_display = (
        'full_name', 'department', 'role', 'count_courses_active', 
        'count_courses', 'created_at', 'updated_at', 'updated_by'
    )

    def count_courses(self, obj):
        return len(obj.courses.all())
    
    def count_courses_active(self, obj):
        return len(obj.courses.filter(is_active=True))
    
    count_courses.short_description = 'Courses (Total)'
    count_courses_active.short_description = 'Courses (Active)'

    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        instance.updated_by = request.user
        instance.save()
        form.save_m2m()
        return instance