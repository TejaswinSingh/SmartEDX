from .error_handlers import (
    custom_bad_request_view,
    custom_permission_denied_view,
    custom_page_not_found_view, 
    custom_server_error_view,
)
from .authentication import (
    login_view, 
    logout_view, 
    redirect_user,
    tell,
)
from .student_views import (
    student_dashboard,
    student_courses,
)
from .course_views import (
    student_course_home,
    student_course_attendance,
    student_course_grades,
    student_course_schedule,
    student_course_assignment,
)