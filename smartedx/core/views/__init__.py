from .authentication import (
    login_view, 
    logout_view, 
    redirect_user,
    tell
)
from .student_views import (
    student_dashboard,
)
from .error_handlers import (
    custom_bad_request_view,
    custom_permission_denied_view,
    custom_page_not_found_view, 
    custom_error_view,
)