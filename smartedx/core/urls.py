from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.tell, name='tell'),
    path('login/', views.login_view),
    path('logout/', views.logout_view),
    path('redirect-user/', views.redirect_user, name='redirect-user'),
    path('student/dashboard/', views.student_dashboard, name='student-dashboard'),
]