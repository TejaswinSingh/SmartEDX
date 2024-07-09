import uuid
from datetime import date
from decimal import Decimal
from core.models import (
    Course,
    Staff,
    Batch,
)
from .utils import (
    validate_condition, formatted_date,
    current_date, timedelta_to_months, 
    MAX_COURSE_DURATION, MIN_COURSE_DURATION,
    SEMS, DEFAULT_MIN_ATTENDANCE
)

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from unfold.admin import ModelAdmin


def get_sems():
    return {i: i for i in SEMS.split(',')}

class CourseInstance(models.Model):
    """ 
    Course(s) are abstract, they are not used directly. CourseInstance(s) are entities
    that instantiate a particular course, and they have real world characterstics -
    like a batch, start_date, instructor, syllabus etc associated with it.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name='instances'
    )
    instructor = models.ForeignKey(
        Staff,
        on_delete=models.PROTECT,
        related_name='courses'
    )
    batch = models.ForeignKey(
        Batch,
        on_delete=models.PROTECT,
        related_name='courses'
    )
    min_attendance = models.DecimalField(
        max_digits=5, decimal_places=2, 
        default=Decimal(DEFAULT_MIN_ATTENDANCE), 
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('100.00'))
        ]
    )
    # it tells in which semester the batch was enrolled for this course instance
    batch_sem = models.CharField(max_length=2, choices=get_sems, blank=True, editable=False)
    start_date = models.DateField()
    end_date = models.DateField()
    # set to False on end_date (archived), can make changes only before that date
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_course_instances'
    )

    class Meta:
        verbose_name_plural = 'course instances'
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'batch'],   # a batch can't study the same course again
                name='%(app_label)s_%(class)s_unique'
            )
        ]

    def __str__(self):
        return f'{self.course}, {formatted_date(self.start_date)} - {formatted_date(self.end_date)}, {self.instructor.full_name()}'
    
    def clean(self):
        # NOTE: fields checked here are the one being used inside clean()
        if not hasattr(self, 'batch') or not hasattr(self, 'course'):
            return
        if not isinstance(self.start_date, date) or not isinstance(self.end_date, date):
            return
        validate_condition(
            condition=not self.is_active and current_date() >= self.end_date,
            error_msg="Can't update archived Course Instance."
        )
        validate_condition(
            self.batch.programme != self.course.programme,
            "Batch and Course must be from the same programme."
        )
        validate_condition(
            self.batch.has_graduated,
            "This batch has already graduated."
        )
        validate_condition(
            not (self.end_date > self.start_date),
            "end date must be greater than start date."
        )
        validate_condition(
            (self.start_date < self.batch.admission_date) or (self.start_date > self.batch.graduation_date),
            "start date can't lie outside batch's programme duration."
        )
        validate_condition(
            (self.end_date < self.batch.admission_date) or (self.end_date > self.batch.graduation_date),
            "end date can't lie outside batch's programme duration."
        )
        duration = self.end_date - self.start_date
        validate_condition(
            duration.days > MAX_COURSE_DURATION.days,
            f"maximum course duration of {timedelta_to_months(MAX_COURSE_DURATION)} months exceeded by {duration.days - MAX_COURSE_DURATION.days} days."
        )
        validate_condition(
            duration.days < MIN_COURSE_DURATION.days, 
            f"minimum course duration of {timedelta_to_months(MIN_COURSE_DURATION)} months not met by {MIN_COURSE_DURATION.days - duration.days} days."
        )
        # set this field only the first time
        if not self.batch_sem:
            self.batch_sem = self.batch.semester

    def get_finished_lectures(self):
        from core.models import Lecture
        q = Lecture.objects.none() # empty queryset
        for s in self.schedule.all():
            q |= s.lectures.filter(is_finished=True, date__lte=current_date())
        return q

    def enroll_batch(self, ignore_existing=False):
        """ enrolls every student in the batch for the course """
        from core.models import CourseEnrollment

        students = self.batch.students.all()
        if not students:
            raise ValidationError("No students exist in the batch.")
        records = []
        for s in students:
            try:
                obj = CourseEnrollment(course_instance=self, student=s)
                obj.full_clean()
                records.append(obj)
            except ValidationError as e:
                # pass in case of exisisting enrollments
                specific_error_message = "Course enrollment with this Course instance and Student already exists."
                if ignore_existing and len(e.messages) == 1 and specific_error_message in e.messages:
                    continue
                else:
                    raise ValidationError(f'{e.message_dict[NON_FIELD_ERRORS][0]} Student - {s}.')
        # save enrollment records only if no error occurred
        for r in records:
            r.save()

    def create_lectures(self, ignore_existing=False):
        """ creates lectures b/w start date and end date using course schedule """
        from core.models import Lecture    # circular import fix

        entries = self.schedule.all()
        if not entries:
            raise ValidationError("No course schedule entries exist.")
        
        lectures = []
        for s in entries:
            dates = s.get_dates()
            for d in dates:
                try:
                    l = Lecture(course_schedule=s, date=d)
                    l.full_clean()
                    lectures.append(l)
                except ValidationError as e:
                    # if a lecture object already exists, then pass (it isn't added to lectures list either for saving)
                    specific_error_message = "Lecture with this Course schedule and Date already exists."
                    if ignore_existing and len(e.messages) == 1 and specific_error_message in e.messages:
                        continue
                    else:
                        raise ValidationError(f'{e.message_dict[NON_FIELD_ERRORS][0]} Course Schedule - {s}, Date - {d}.')
        # only save after all lecture objects are validated, i.e all are created or none are created
        for l in lectures:
            l.save()

class CourseInstanceAdmin(ModelAdmin):
    list_display = (
        'course', 'instructor', 'batch', 
        'start_date', 'end_date', 'get_semester',
        'is_active', 'min_attendance', 'count_students',
        'count_weekly_lectures', 'count_total_lectures',
        'created_at', 'updated_at', 'updated_by'
    )

    def count_students(self, obj):
        return len(obj.enrollments.all())
    
    def count_weekly_lectures(self, obj):
        return len(obj.schedule.all())
    
    def count_total_lectures(self, obj):
        return len(obj.get_finished_lectures())
    
    def get_semester(self, obj):
        return obj.batch_sem

    count_students.short_description = 'Students Enrolled'
    count_weekly_lectures.short_description = 'Lectures Per Week'
    count_total_lectures.short_description = 'Lectures Till Date'
    get_semester.short_description = 'Semester Studied'

    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        instance.updated_by = request.user
        instance.save()
        form.save_m2m()
        return instance