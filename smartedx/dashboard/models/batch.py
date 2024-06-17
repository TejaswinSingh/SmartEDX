from .programme import Programme
from .utils import MIN_ADMISSION_GOBACK_LIMIT, MAX_GRADUATION_LIMIT, current_year

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


def get_sems():
    return {i: i for i in '12345678'}

class Batch(models.Model):
    """ admission batches """

    programme = models.ForeignKey(
        Programme,
        on_delete=models.PROTECT,
        related_name='batches'
    )
    admission_year = models.IntegerField(
        validators=[
            MinValueValidator(current_year() - MIN_ADMISSION_GOBACK_LIMIT), 
            MaxValueValidator(current_year())
        ]
    )
    graduation_year = models.IntegerField(
        validators=[
            MinValueValidator(current_year()), 
            MaxValueValidator(current_year() + MAX_GRADUATION_LIMIT)
        ]
    )
    semester = models.CharField(max_length=1, choices=get_sems, default='1')
    has_graduated = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'batches'
        constraints = [
            models.UniqueConstraint(
                fields=['programme', 'admission_year', 'graduation_year', 'semester'], 
                name='%(app_label)s_%(class)s_unique'
            )
        ]

    def count_students(self):
        return len(self.students.all())

    def __str__(self):
        return f'{self.programme.name}, SEM {self.semester}, {self.admission_year}-{self.graduation_year}'