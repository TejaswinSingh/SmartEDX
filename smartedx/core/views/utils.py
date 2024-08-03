from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def user_passes_test_or_render_error(test_func, template="core/error.html", context=None):
    """ decorator func that checks whether user passes the test_func or not """

    # default context
    if context is None:
        context = {
            'status': "403", 
            'status_text': "Forbidden",
            'err_msg': "You're not authorized to access this resource"
        }

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