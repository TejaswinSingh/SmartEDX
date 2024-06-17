import uuid
from django.utils import timezone

from .utils import MIN_YEAR_LIMIT, max_value_current_year

from django.db import models
from django.core.validators import MinValueValidator


class Department(models.Model):
    """ academic departments """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    established = models.IntegerField(validators=[MinValueValidator(MIN_YEAR_LIMIT), max_value_current_year])

    class Meta:
        verbose_name_plural = 'departments'

    def count_programmes(self):
        return len(self.programmes.all())
    
    def count_staff(self):
        return len(self.staff.all())
    
    def count_current_students(self):
        n = 0
        for p in self.programmes.all():
            current_year = timezone.now().year
            # lookup active batches only
            for b in p.batches.filter(graduation_year__gte=current_year, has_graduated=False):
                print(b)
                n += len(b.students.all())
        return n

    def __str__(self):
        return f'{self.name}'