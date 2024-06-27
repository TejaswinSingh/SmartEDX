from datetime import date
from dashboard.models import Programme
from .utils import validate_condition, SEMS

from django.db import models
from django.contrib.auth.models import User
from unfold.admin import ModelAdmin


def get_sems():
    return {i: i for i in SEMS.split(',')}

class Batch(models.Model):
    """ admission batches """

    programme = models.ForeignKey(
        Programme,
        on_delete=models.PROTECT,
        related_name='batches'
    )
    admission_date = models.DateField()
    graduation_date = models.DateField()
    semester = models.CharField(max_length=2, choices=get_sems, default='1')
    has_graduated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_batches'
    )

    class Meta:
        verbose_name_plural = 'batches'
        constraints = [
            models.UniqueConstraint(
                fields=['programme', 'admission_date', 'graduation_date', 'semester'], 
                name='%(app_label)s_%(class)s_unique'
            )
        ]

    def __str__(self):
        return f'{self.programme.name}, SEM {self.semester}, {self.admission_date.year}-{self.graduation_date.year}'
    
    def clean(self):
        if not isinstance(self.admission_date, date) or not isinstance(self.graduation_date, date):
            return
        if not hasattr(self, 'programme'):
            return
        validate_condition(
            condition=not(self.graduation_date > self.admission_date),
            error_msg="graduation date must be greater than admission date"
        )
        duration = self.graduation_date - self.admission_date
        # validate_condition(
        #     duration > MAX_GRADUATION_LIMIT,
        #     f"maximum graduation limit is {timedelta_to_years(MAX_GRADUATION_LIMIT)} years"
        # )
        validate_condition(
            duration.days > self.programme.duration_td.days,
            f"selected programme's duration of {self.programme.duration} years was exceeded by {duration.days - self.programme.duration_td.days} days"
        )
        validate_condition(
            duration.days < (self.programme.duration_td / 2).days,
            f"batch cannot graduate in less than half the duration of the selected programme ({self.programme.duration} years)"
        )
            

class BatchAdmin(ModelAdmin):
    list_display = (
        'programme', 'admission_date', 'graduation_date',
        'current_semester', 'count_students', 'count_active_courses', 
        'count_courses', 'has_graduated', 'created_at', 'updated_at', 'updated_by'
    )

    def current_semester(self, obj):
        return obj.semester

    def count_students(self, obj):
        return len(obj.students.all())
    
    def count_courses(self, obj):
        return len(obj.courses.all())
    
    def count_active_courses(self, obj):
        return len(obj.courses.filter(is_active=True))
    
    count_students.short_description = 'Students'
    count_courses.short_description = 'Total Courses'
    count_active_courses.short_description = 'Active Courses'

    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        instance.updated_by = request.user
        instance.save()
        form.save_m2m()
        return instance