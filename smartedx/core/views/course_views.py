from decimal import Decimal
from .utils import (
    user_passes_test_or_render_error, annotate_course_instance,
    annotate_content_section
)
from .error_handlers import CONTEXT_TEMPLATES
from core.models import (
    CourseInstance, CourseEnrollment, 
    AttendanceRecord, SectionItemAssignment,
    AssignmentSubmission, SubmissionReview
)
from core.models.utils import truncate_float, current_time, get_dates_of_week, DAYS_OF_WEEK_CHOICES
from core.forms import AssignmentSubmissionForm

from django.shortcuts import render
from django.http import HttpResponse


err_template='core/error.html'
context_not_student = {'status':"403", 'status_text': "Forbidden" ,'err_msg':"Only students are allowed to access this page"}
context_not_enrolled = {'status':"403", 'status_text': "Forbidden" ,'err_msg':"You're not enrolled for this course"}

def is_student(user):
    return hasattr(user, 'student')

def is_student_enrolled(student, course):
    try:
        CourseEnrollment.objects.get(student=student, course_instance=course)
        return True
    except CourseEnrollment.DoesNotExist:
        return False

@user_passes_test_or_render_error(is_student, template=err_template, context=context_not_student)
def student_course_home(request, course_uuid):
    try:
        course = CourseInstance.objects.get(pk=course_uuid)
        course = annotate_course_instance(course)
    except CourseInstance.DoesNotExist:
        return render(request, err_template, CONTEXT_TEMPLATES['404'], status=404)
    
    if not is_student_enrolled(request.user.student, course):
        return render(request, err_template, context_not_enrolled, status=403)
    
    sections = []
    for section in course.content_sections.all().order_by("order"):
        sections.append(annotate_content_section(section, request.user))
    
    return render(request, "core/student_course_view.html", {"course": course, "home": True, "sections": sections})


@user_passes_test_or_render_error(is_student, template=err_template, context=context_not_student)
def student_course_attendance(request, course_uuid):
    try:
        course = CourseInstance.objects.get(pk=course_uuid)
        course = annotate_course_instance(course)
    except CourseInstance.DoesNotExist:
        return render(request, err_template, CONTEXT_TEMPLATES['404'], status=404)
    
    if not is_student_enrolled(request.user.student, course):
        return render(request, err_template, context_not_enrolled, status=403)

    total, attended = 0, 0
    lectures = []
    for sched in course.schedule.all():
        # lectures |= sched.lectures.filter(is_finished=True)
        for l in sched.lectures.filter(is_finished=True):
            total += 1
            l.schedule = sched
            l.weekday = DAYS_OF_WEEK_CHOICES[str(l.date.weekday())]
            try:
                l.attended = False
                if l.attendance_record.get(student=request.user.student).is_present:
                    l.attended = True
                    attended += 1   
            except AttendanceRecord.DoesNotExist:
                pass
            lectures.append(l)

    if lectures:
        cur_attendance = Decimal(truncate_float((attended/total) * 100, n=2))
        next_attendance = Decimal(truncate_float(((attended+1)/(total+1)) * 100, n=2))
        # sort lectures in desc
        lectures = sorted(lectures, key=lambda lecture: (lecture.date.weekday(), lecture.schedule.start_time), reverse=True)
    else:
        cur_attendance = Decimal('0.00')
        next_attendance = Decimal(truncate_float(((attended+1)/(total+1)) * 100, n=2))
    
    return render(request, "core/student_course_view.html", {
        "course": course, "attendance": True,  "lectures": lectures[:5],
        "lectures_held": total, "lectures_attended": attended,
        "cur_attendance": cur_attendance, "next_attendance": next_attendance
    })


@user_passes_test_or_render_error(is_student, template=err_template, context=context_not_student)
def student_course_grades(request, course_uuid):
    try:
        course = CourseInstance.objects.get(pk=course_uuid)
        course = annotate_course_instance(course)
    except CourseInstance.DoesNotExist:
        return render(request, err_template, CONTEXT_TEMPLATES['404'], status=404)
    
    if not is_student_enrolled(request.user.student, course):
        return render(request, err_template, context_not_enrolled, status=403)
    
    assignments = []
    for section in course.content_sections.all().order_by("order"):
        for assignment in section.items_assignment.all():
            try:
                assignment.submission = AssignmentSubmission.objects.get(assignment=assignment, student=request.user.student)
                assignment.submission.review = assignment.submission.review
            except (AssignmentSubmission.DoesNotExist, SubmissionReview.DoesNotExist):
                pass
            assignments.append(assignment)
    
    return render(request, "core/student_course_view.html", {"course": course, "grades": True, "assignments": assignments})


@user_passes_test_or_render_error(is_student, template=err_template, context=context_not_student)
def student_course_schedule(request, course_uuid):
    try:
        course = CourseInstance.objects.get(pk=course_uuid)
        course = annotate_course_instance(course)
    except CourseInstance.DoesNotExist:
        return render(request, err_template, CONTEXT_TEMPLATES['404'], status=404)
    
    if not is_student_enrolled(request.user.student, course):
        return render(request, err_template, context_not_enrolled, status=403)
    
    now = current_time()
    lectures_today = []
    for sched in course.schedule.filter(weekday=now.date().weekday()).order_by("start_time"):
        for l in sched.lectures.filter(date=now.date()):
            l.schedule = sched
            lectures_today.append(l)
            
    lectures_week = []
    dates = get_dates_of_week(now)
    for sched in course.schedule.all():
        for l in sched.lectures.filter(date__range=(dates[0], dates[-1])):
            l.schedule = sched
            l.weekday = DAYS_OF_WEEK_CHOICES[str(l.date.weekday())]
            lectures_week.append(l)
    # sort lectures
    lectures_week = sorted(lectures_week, key=lambda lecture: (lecture.date.weekday(), lecture.schedule.start_time))

    return render(request, "core/student_course_view.html", {"course": course, "schedule": True, "lectures_today": lectures_today, "lectures_week": lectures_week})


@user_passes_test_or_render_error(is_student, template=err_template, context=context_not_student)
def student_course_assignment(request, course_uuid, assignment_id):
    try:
        course = CourseInstance.objects.get(pk=course_uuid)
        course = annotate_course_instance(course)
        if not is_student_enrolled(request.user.student, course):
            return render(request, err_template, context_not_enrolled, status=403)
        assignment = SectionItemAssignment.objects.get(pk=assignment_id)
        assignment.is_active = True
        if current_time() > assignment.ends_at:
            assignment.is_active = False
    except (CourseInstance.DoesNotExist, SectionItemAssignment.DoesNotExist):
        return render(request, err_template, CONTEXT_TEMPLATES['404'], status=404)
    
    try:
        submission = AssignmentSubmission.objects.get(assignment=assignment, student=request.user.student)
        form = AssignmentSubmissionForm(instance=submission)
    except AssignmentSubmission.DoesNotExist:
        submission = None
        form = AssignmentSubmissionForm(data={"assignment": assignment, "student": request.user.student})

    if request.method == "POST" and 'delete' in request.POST and submission:   
        submission.delete()
        submission = None
        form = AssignmentSubmissionForm(data={"assignment": assignment, "student": request.user.student})

    elif request.method == "POST":
        form = AssignmentSubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            form.save()
            submission = AssignmentSubmission.objects.get(assignment=assignment, student=request.user.student)
            form = AssignmentSubmissionForm(instance=submission)
            print(submission.filename())

    review = None
    if submission:
        try:
            review = submission.review
        except SubmissionReview.DoesNotExist:
            pass

    return render(request, "core/student_assignment_view.html", {"course": course, "assignment": assignment, "submission": submission, "form": form, "review": review})