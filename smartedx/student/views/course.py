from decimal import Decimal
from core.views.utils import user_passes_test_or_render_error
from core.views.error_handlers import CONTEXT_TEMPLATES
from core.models import (
    CourseInstance, SectionItemAssignment, 
    AssignmentSubmission, SubmissionReview,
)
from core.models.utils import (
    current_time, 
    get_dates_of_week, 
    DAYS_OF_WEEK_CHOICES,
)
from student.forms import AssignmentSubmissionForm
from .utils import (
    err_template,
    context_not_student,
    context_not_enrolled,
    annotate_course_instance,
    annotate_content_section,
    is_student,
    is_student_enrolled,
    get_course_lectures,
    calculate_attendance,
)
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.http import HttpResponse

def validate_request(request, course_uuid):
    """ validates that course-instance with the uuid exists and student is enrolled for that course """
    try:
        course = CourseInstance.objects.get(pk=course_uuid)
        if not is_student_enrolled(request.user.student, course):
            return TemplateResponse(request, err_template, context_not_enrolled, status=403).render()
        return annotate_course_instance(course)
    except CourseInstance.DoesNotExist:
        return TemplateResponse(request, err_template, CONTEXT_TEMPLATES['404'], status=404).render()

@user_passes_test_or_render_error(is_student, template=err_template, context=context_not_student)
def student_course_home(request, course_uuid):
    """ renders course's home-page """

    # get course
    val = validate_request(request, course_uuid)
    if isinstance(val, TemplateResponse):
        return val
    course = val
    
    # get content-sections
    sections = []
    for section in course.content_sections.all().order_by("order"):
        sections.append(annotate_content_section(section, request.user))
    
    return render(
        request, "student/course.html", 
        context = {
            "course": course, 
            "home": True, 
            "sections": sections
        }
    )

@user_passes_test_or_render_error(is_student, template=err_template, context=context_not_student)
def student_course_attendance(request, course_uuid):
    """ renders course's attendance-page """

    # get course
    val = validate_request(request, course_uuid)
    if isinstance(val, TemplateResponse):
        return val
    course = val
    
    # get finished lectures
    total, attended, lectures = get_course_lectures(course, request.user.student)

    # calc attendance
    if lectures:
        cur_attendance = calculate_attendance(attended, total)
        next_attendance = calculate_attendance(attended+1, total+1)
        # sort lectures list
        lectures = sorted(
            lectures, 
            key = lambda lecture: (lecture.date, lecture.schedule.start_time), 
            reverse = True
        )
    else:
        cur_attendance = Decimal('0.00')
        next_attendance = calculate_attendance(attended+1, total+1) # always 100.00
    
    return render(request, "student/course.html", context = {
        "course": course, "attendance": True,  "lectures": lectures[:5], # last 5 lectures
        "lectures_held": total, "lectures_attended": attended,
        "cur_attendance": cur_attendance, "next_attendance": next_attendance
    })


@user_passes_test_or_render_error(is_student, template=err_template, context=context_not_student)
def student_course_grades(request, course_uuid):
    """ renders course's grades-page """

    # get course
    val = validate_request(request, course_uuid)
    if isinstance(val, TemplateResponse):
        return val
    course = val
    
    # get assignments
    assignments = []
    for section in course.content_sections.all().order_by("order"):
        for assignment in section.items_assignment.all():
            try:
                assignment.submission = AssignmentSubmission.objects.get(assignment=assignment, student=request.user.student)
                assignment.submission.review = assignment.submission.review
            except (AssignmentSubmission.DoesNotExist, SubmissionReview.DoesNotExist):
                pass
            assignments.append(assignment)
    
    return render(
        request, "student/course.html", 
        context = {
            "course": course, 
            "grades": True, 
            "assignments": assignments
        }
    )


@user_passes_test_or_render_error(is_student, template=err_template, context=context_not_student)
def student_course_schedule(request, course_uuid):
    """ renders course's schedule-page """

    # get course
    val = validate_request(request, course_uuid)
    if isinstance(val, TemplateResponse):
        return val
    course = val
    
    now = current_time()

    # today's schedule
    lectures_today = []
    for sched in course.schedule.filter(weekday=now.date().weekday()).order_by("start_time"):
        for l in sched.lectures.filter(date=now.date()):
            l.schedule = sched
            lectures_today.append(l)
            
    # weekly schedule
    lectures_week = []
    dates = get_dates_of_week(now)
    for sched in course.schedule.all():
        for l in sched.lectures.filter(date__range=(dates[0], dates[-1])):
            l.schedule = sched
            l.weekday = DAYS_OF_WEEK_CHOICES[str(l.date.weekday())]
            lectures_week.append(l)

    # sort weekly lectures
    lectures_week = sorted(
        lectures_week, 
        key = lambda lecture: (lecture.date.weekday(), lecture.schedule.start_time)
    )

    return render(
        request, "student/course.html", 
        context = {
            "course": course, "schedule": True, 
            "lectures_today": lectures_today, "lectures_week": lectures_week
        }
    )


@user_passes_test_or_render_error(is_student, template=err_template, context=context_not_student)
def student_course_assignment(request, course_uuid, assignment_id):
    """ renders student assignment-page """

    # get course
    val = validate_request(request, course_uuid)
    if isinstance(val, TemplateResponse):
        return val
    course = val

    # get assignment
    try:
        assignment = SectionItemAssignment.objects.get(pk=assignment_id)
        assignment.is_active = True
        if current_time() > assignment.ends_at:
            assignment.is_active = False
    except (CourseInstance.DoesNotExist, SectionItemAssignment.DoesNotExist):
        return render(request, err_template, CONTEXT_TEMPLATES['404'], status=404)
    
    # get assignment-submission
    try:
        submission = AssignmentSubmission.objects.get(assignment=assignment, student=request.user.student)
        form = AssignmentSubmissionForm(instance=submission)
    except AssignmentSubmission.DoesNotExist:
        submission = None
        form = AssignmentSubmissionForm(data={"assignment": assignment, "student": request.user.student})

    # delete submission
    if request.method == "POST" and 'delete' in request.POST and submission:   
        submission.delete()
        submission = None
        form = AssignmentSubmissionForm(data={"assignment": assignment, "student": request.user.student})

    # create or update submisison
    elif request.method == "POST":
        form = AssignmentSubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            form.save()
            submission = AssignmentSubmission.objects.get(assignment=assignment, student=request.user.student)
            form = AssignmentSubmissionForm(instance=submission)

    # get submission-review
    review = None
    if submission:
        try:
            review = submission.review
        except SubmissionReview.DoesNotExist:
            pass

    return render(
        request, "student/assignment.html", 
        context = {
            "course": course, "assignment": assignment, 
            "submission": submission, "form": form, "review": review
        }
    )