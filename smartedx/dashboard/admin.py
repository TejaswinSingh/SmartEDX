from .models import (
    Department, DepartmentAdmin,
    Programme, ProgrammeAdmin,
    Batch, BatchAdmin,
    Student, StudentAdmin,
    StaffRole, StaffRoleAdmin,
    Staff, StaffAdmin,
    Course, CourseAdmin,
    CourseInstance, CourseInstanceAdmin,
    CourseEnrollment, CourseEnrollmentAdmin,
    CourseSchedule, CourseScheduleAdmin,
    Lecture, LectureAdmin,
    AttendanceRecord, AttendanceRecordAdmin
)
from django.contrib import admin


admin.site.register(Department, DepartmentAdmin)

admin.site.register(Programme, ProgrammeAdmin)

admin.site.register(Batch, BatchAdmin)

admin.site.register(Student, StudentAdmin)

admin.site.register(StaffRole, StaffRoleAdmin)

admin.site.register(Staff, StaffAdmin)

admin.site.register(Course, CourseAdmin)

admin.site.register(CourseInstance, CourseInstanceAdmin)

admin.site.register(CourseEnrollment, CourseEnrollmentAdmin)

admin.site.register(CourseSchedule, CourseScheduleAdmin)

admin.site.register(Lecture, LectureAdmin)

admin.site.register(AttendanceRecord, AttendanceRecordAdmin)