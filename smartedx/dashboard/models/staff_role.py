from dashboard.models import Department

from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User


class StaffRole(models.Model):
    """ staff roles """

    title = models.CharField(max_length=100, unique=True)
    only_one = models.BooleanField(default=False)
    one_per_dept = models.BooleanField(default=False)
    only_for_dept = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='specific_roles'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_staff_roles'
    )

    class Meta:
        verbose_name_plural = 'staff roles'

    def __str__(self):
        return self.title
    

class StaffRoleAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'only_one', 'one_per_dept', 'only_for_dept', 
        'get_staff_count', 'created_at', 'updated_at', 'updated_by'
    )

    def get_staff_count(self, obj):
        return len(obj.staff.all())
    
    get_staff_count.short_description = 'Staff Count'

    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        instance.updated_by = request.user
        instance.save()
        form.save_m2m()
        return instance