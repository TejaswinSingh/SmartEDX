from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.tell, name='tell'),
    path('login/', views.login_view),
    path('logout/', views.logout_view),
]