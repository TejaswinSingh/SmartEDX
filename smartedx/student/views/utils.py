from decimal import Decimal
from core.models import (
    CourseInstance, 
    ContentSection,
    CourseEnrollment,
    AssignmentSubmission,
    AttendanceRecord,
)
from core.models.utils import (
    DAYS_OF_WEEK_CHOICES,
    truncate_float,
)

err_template = 'core/error.html'
context_not_student = {
    'status': "403", 
    'status_text': "Forbidden", 
    'err_msg': "Only students are allowed to access this page"
}
context_not_enrolled = {
    'status': "403", 
    'status_text': "Forbidden", 
    'err_msg': "You're not enrolled for this course"
}


def is_student(user):
    """ returns true if user is a student """
    return hasattr(user, 'student')

def is_student_enrolled(student, course):
    """ returns true if user is enrolled for the course """
    try:
        CourseEnrollment.objects.get(student=student, course_instance=course)
        return True
    except CourseEnrollment.DoesNotExist:
        return False

def annotate_course_instance(c: CourseInstance, user=None):
    course = c.course
    c.title = course.title
    c.course_code = course.course_code
    c.instructor.name = c.instructor.full_name()
    return c

def annotate_content_section(obj: ContentSection, user=None):
    obj.items = []
    for i in obj.items_text.all():
        if i.link:
            i.type = 'link'
        else:
            i.type = 'text'
        obj.items.append(i)

    for i in obj.items_file.all():
        i.type = 'file'
        obj.items.append(i)

    for i in obj.items_assignment.all():
        i.type = 'assignment'
        try:
            AssignmentSubmission.objects.get(student=user.student, assignment=i)
            i.submitted = True
        except AssignmentSubmission.DoesNotExist:
            i.submitted = False
        obj.items.append(i)

    # Can sort items list based on creation date or order of items

    return obj

def get_course_lectures(course, student):
    """ returns annotated lectures """

    total, attended, lectures = 0, 0, []
    for sched in course.schedule.all():
        for l in sched.lectures.filter(is_finished=True):
            total += 1
            l.schedule = sched
            l.weekday = DAYS_OF_WEEK_CHOICES[str(l.date.weekday())]
            try:
                l.attended = False
                if l.attendance_record.get(student=student).is_present:
                    l.attended = True
                    attended += 1   
            except AttendanceRecord.DoesNotExist:
                pass
            lectures.append(l)

    return total, attended, lectures

def calculate_attendance(attended, total):
    """ given total lectures and attended lectures, it returns attendance % """
    return Decimal(truncate_float((attended/total) * 100, n=2))