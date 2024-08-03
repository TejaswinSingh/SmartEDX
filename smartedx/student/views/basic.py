from core.views.utils import user_passes_test_or_render_error
from .utils import (
    err_template,
    context_not_student,
    annotate_course_instance,
    is_student,
)
from django.shortcuts import render
from django.http import HttpResponse

@user_passes_test_or_render_error(is_student, template=err_template, context=context_not_student)
def student_dashboard(request):
    """ renders student dashboard-page """

    # annotate student
    student = request.user.student
    student.full_name = student.full_name()

    context = {
        "student": student,
    }
    return render(request, "student/base.html", context)

@user_passes_test_or_render_error(is_student, template=err_template, context=context_not_student)
def student_courses(request):
    """ renders student my-courses-page """

    # annotate student
    student = request.user.student
    student.full_name = student.full_name()
    student.sem = student.batch.semester

    # get currently active course-instances
    courses = []
    for enrollment in student.enrollments.all():
        c = enrollment.course_instance
        if c.is_active:
            courses.append(annotate_course_instance(c))

    context = {
        "student": student,
        "courses": courses,
    }
    return render(request, "student/my_courses.html", context)