from django.shortcuts import render

template="core/error.html"


def custom_bad_request_view(request, exception=None):
    context = {
        'status': "400", 
        'status_text': "Bad Request", 
        'err_msg': "Please check the url"
    }
    return render(request, template, context, status=400)

def custom_permission_denied_view(request, exception=None):
    context = {
        'status': "403", 
        'status_text': "Forbidden", 
        'err_msg': "You're not authorized to access this resource"
    }
    return render(request, template, context, status=403)

def custom_page_not_found_view(request, exception):
    context = {
        'status':"404", 
        'status_text': "Page Not Found", 
        'err_msg': "The requested resource does not exist"
    }
    return render(request, template, context, status=404)

def custom_error_view(request, exception=None):
    context = {
        'status':"500", 
        'status_text': "Internal Server Error", 
        'err_msg':"Something went wrong on our side"
    }
    return render(request, template, context, status=500)