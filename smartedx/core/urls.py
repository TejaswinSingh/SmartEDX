from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.tell, name='tell'),
    path('login/', views.login_view),
    path('logout/', views.logout_view),
    path('redirect-user/', views.redirect_user, name='redirect-user'),
    path('student/dashboard/', views.student_dashboard, name='student-dashboard'),
    path('student/my-courses/', views.student_courses, name='student-my-courses'),
    path('student/course/<str:course_uuid>/home/', views.student_course_home, name='student-course-home'),
    path('student/course/<str:course_uuid>/attendance/', views.student_course_attendance, name='student-course-attendance'),
    path('student/course/<str:course_uuid>/grades/', views.student_course_grades, name='student-course-grades'),
    path('student/course/<str:course_uuid>/schedule/', views.student_course_schedule, name='student-course-schedule'),
    path('student/course/<str:course_uuid>/assignment/<str:assignment_id>/', views.student_course_assignment, name='student-course-assignment'),
]