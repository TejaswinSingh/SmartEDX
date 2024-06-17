from .models import Department, Programme, Batch, Student, Staff, StaffRole

from django.contrib import admin

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'established', 'programmes', 'staff', 'students')
    
    def programmes(self, obj):
        return obj.count_programmes()
    def staff(self, obj):
        return obj.count_staff()
    def students(self, obj):
        return obj.count_current_students()
    students.short_description = 'Current Students'

@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('programme', 'admission_year', 'semester', 'students', 'has_graduated', 'graduation_year')
    def students(self, obj):
        return obj.count_students()

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'batch')

@admin.register(StaffRole)
class StaffRoleAdmin(admin.ModelAdmin):
    list_display = ('title', 'only_one', 'one_per_dept', 'only_for_dept')

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'department', 'role')