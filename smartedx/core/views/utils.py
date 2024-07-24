from functools import wraps
from core.models import (
    CourseInstance, ContentSection,
    AssignmentSubmission
)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def user_passes_test_or_render_error(test_func, template="core/error.html", context=None):
    if context is None:
        context = {'status': "403", 'status_text': "Forbidden" ,'err_msg': "You're not authorized to access this resource"}
    def decorator(view_func):
        @wraps(view_func)
        @login_required # check authentication first
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            else:
                return render(request, template, context, status=context['status'])
        return _wrapped_view
    return decorator


def annotate_course_instance(c: CourseInstance, user=None):
    course = c.course
    c.title = course.title
    c.course_code = course.course_code
    c.instructor.name = c.instructor.full_name()
    return c

def annotate_content_section(obj: ContentSection, user=None):
    obj.items = []
    for i in obj.items_text.all():
        if i.link:
            i.type = 'link'
        else:
            i.type = 'text'
        obj.items.append(i)

    for i in obj.items_file.all():
        i.type = 'file'
        obj.items.append(i)

    for i in obj.items_assignment.all():
        i.type = 'assignment'
        try:
            AssignmentSubmission.objects.get(student=user.student, assignment=i)
            i.submitted = True
        except AssignmentSubmission.DoesNotExist:
            i.submitted = False
        obj.items.append(i)

    # Can sort items list based on creation date or order of items

    return obj