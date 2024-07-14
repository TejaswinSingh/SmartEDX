from .utils import user_passes_test_or_render_error, annotate_course_instance
from core.models import CourseInstance

from django.shortcuts import render, redirect
from django.http import HttpResponse


err_template='core/error.html'
context = {'status':"403", 'status_text': "Forbidden" ,'err_msg':"Only students are allowed to access this page"}

def student_check(user):
    return hasattr(user, 'student')

@user_passes_test_or_render_error(student_check, template=err_template, context=context)
def student_dashboard(request):
    student = request.user.student
    student.full_name = student.full_name()
    context = {
        "student": student,
    }
    return render(request, "core/student_base.html", context)


@user_passes_test_or_render_error(student_check, template=err_template, context=context)
def student_courses(request):
    student = request.user.student
    student.full_name = student.full_name()
    student.sem = student.batch.semester
    courses = []
    for c in student.batch.courses.filter(is_active=True):
        courses.append(annotate_course_instance(c)) # add some extra details to each course instance
    context = {
        "student": student,
        "courses": courses,
    }
    return render(request, "core/student_my_courses.html", context)