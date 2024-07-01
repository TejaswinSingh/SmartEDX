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
    AttendanceRecord, AttendanceRecordAdmin,
    ContentSection, ContentSectionAdmin,
    SectionItemText, SectionItemTextAdmin,
    SectionItemFile, SectionItemFileAdmin,
    SectionItemAssignment, SectionItemAssignmentAdmin,
    AssignmentSubmission, AssignmentSubmissionAdmin,
    SubmissionReview, SubmissionReviewAdmin
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

admin.site.register(ContentSection, ContentSectionAdmin)

admin.site.register(SectionItemText, SectionItemTextAdmin)

admin.site.register(SectionItemFile, SectionItemFileAdmin)

admin.site.register(SectionItemAssignment, SectionItemAssignmentAdmin)

admin.site.register(AssignmentSubmission, AssignmentSubmissionAdmin)

admin.site.register(SubmissionReview, SubmissionReviewAdmin)