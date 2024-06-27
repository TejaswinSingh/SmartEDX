import uuid
from .utils import MIN_ESTABLISHED_YEAR, current_year

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from unfold.admin import ModelAdmin


class Department(models.Model):
    """ academic departments """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    established = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_departments'
    )

    class Meta:
        verbose_name_plural = 'departments'

    def __str__(self):
        return f'{self.name}'
    
    def get_current_students(self):
        from dashboard.models import Student
        q = Student.objects.none() # empty queryset
        for p in self.programmes.all():
            q |= p.get_current_students()
        return q
    
    def get_hod(self):
        from dashboard.models import Staff, StaffRole  # circular import fix
        try:
            hod = StaffRole.objects.get(title='Head of Department')
            s = Staff.objects.get(department=self, role=hod)
            return s.full_name()
        except (Staff.DoesNotExist, Staff.MultipleObjectsReturned):
            return None
        
    def clean(self):
        if not isinstance(self.established, int):
            return
        if self.established < MIN_ESTABLISHED_YEAR or self.established > current_year():
            raise ValidationError(f"Established year must lie between {MIN_ESTABLISHED_YEAR} and {current_year()}")
        self.slug = slugify(self.name)
    

class DepartmentAdmin(ModelAdmin):
    prepopulated_fields = {"slug": ["name"]}
    list_display = (
        'name', 'established', 'get_hod', 'count_programmes', 
        'count_staff', 'count_students', 'created_at', 'updated_at', 'updated_by'
    )
    
    def count_programmes(self, obj):
        return len(obj.programmes.all())
    
    def count_staff(self, obj):
        return len(obj.staff.all())
    
    def count_students(self, obj):
        return len(obj.get_current_students())
    
    def get_hod(self, obj):
        return obj.get_hod()
    
    count_programmes.short_description = 'Programmes'
    count_staff.short_description = 'Staff'
    count_students.short_description = 'Students'
    get_hod.short_description = 'Head of Department'

    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        instance.updated_by = request.user
        instance.save()
        form.save_m2m()
        return instance