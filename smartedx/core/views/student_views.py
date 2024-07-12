from .utils import user_passes_test_or_render_error

from django.shortcuts import render, redirect
from django.http import HttpResponse


err_template='core/error.html'
context = {'status':"403", 'status_text': "Forbidden" ,'err_msg':"Only students are allowed to access this page"}

def student_check(user):
    return hasattr(user, 'student')

@user_passes_test_or_render_error(student_check, template=err_template, context=context)
def student_dashboard(request):
    return render(request, "core/student_base.html")