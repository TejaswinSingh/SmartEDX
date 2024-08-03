from django.urls import path
from . import views

app_name = 'student'

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('my-courses/', views.student_courses, name='my-courses'),
    path('course/<str:course_uuid>/home/', views.student_course_home, name='course-home'),
    path('course/<str:course_uuid>/attendance/', views.student_course_attendance, name='course-attendance'),
    path('course/<str:course_uuid>/grades/', views.student_course_grades, name='course-grades'),
    path('course/<str:course_uuid>/schedule/', views.student_course_schedule, name='course-schedule'),
    path('course/<str:course_uuid>/assignment/<str:assignment_id>/', views.student_course_assignment, name='course-assignment'),
]