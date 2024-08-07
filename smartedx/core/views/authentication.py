from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm

def tell(request):
    if request.user.is_authenticated:
        return HttpResponse(f"you're logged in as {request.user.username}")
    return HttpResponse("you're not logged in!")


def login_view(request):
    """ renders login page """

    next_url = request.GET.get('next', 'core:redirect-user')

    if request.method == "POST":   
        form = AuthenticationForm(None, data=request.POST)
        # unlike other forms, AuthenticationForm's is_valid() validates
        # that a user object with the provided credential exists
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect(next_url) 
    else:
        form = AuthenticationForm()

    return render(
        request, 
        template_name = "core/login.html", 
        context = {
            'form':form, 
            'next_url': '' if next_url == 'core:redirect-user' else next_url
        }
    )


def logout_view(request):
    """ renders logout page """

    if request.method == "POST":
        logout(request)
        return redirect('core:tell')

    return render(request, "core/logout.html")


@login_required
def redirect_user(request):
    """ redirects user to their default page depending on their type """

    # for admin site
    if request.user.is_staff:
        return redirect('/admin/')
    
    # students
    if hasattr(request.user, 'student'):
        return redirect('student:dashboard')
    
    # instructors
    if hasattr(request.user, 'staff'):
        return HttpResponse("no redirect for staff yet")
    
    # if neither case
    return HttpResponse("no redirect for this user")