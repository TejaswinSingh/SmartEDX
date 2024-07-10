from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout


def tell(request):
    if request.user.is_authenticated:
        return HttpResponse(f"you're logged in as {request.user.username}")
    return HttpResponse("you're not logged in!")


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(None, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # redirect to a home view, that would further redirect to student-home view
                # or staff-home view depending upon the user
                return redirect('core:tell')
              
        return render(request, "core/login.html", context={'form':form}) 
    else:
        form = AuthenticationForm()
    return render(request, "core/login.html", context={'form':form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect('core:tell')

    return render(request, "core/logout.html")