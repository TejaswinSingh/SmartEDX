from django.shortcuts import render

template="core/error.html"

CONTEXT_TEMPLATES = {
    '400': {
        'status': "400", 
        'status_text': "Bad Request", 
        'err_msg': "Please check the url"
    },
    '403': {
        'status': "403", 
        'status_text': "Forbidden", 
        'err_msg': "You're not authorized to access this resource"
    },
    '404': {
        'status':"404", 
        'status_text': "Page Not Found", 
        'err_msg': "The requested resource does not exist"
    },
    '500': {
        'status':"500", 
        'status_text': "Internal Server Error", 
        'err_msg':"Something went wrong on our side"
    },
}


def custom_bad_request_view(request, exception=None):
    context = CONTEXT_TEMPLATES['400']
    return render(request, template, context, status=400)

def custom_permission_denied_view(request, exception=None):
    context = CONTEXT_TEMPLATES['403']
    return render(request, template, context, status=403)

def custom_page_not_found_view(request, exception):
    context = CONTEXT_TEMPLATES['404']
    return render(request, template, context, status=404)

def custom_server_error_view(request, exception=None):
    context = CONTEXT_TEMPLATES['500']
    return render(request, template, context, status=500)