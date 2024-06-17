from .department import Department

from django.db import models


class StaffRole(models.Model):
    """ staff roles """

    title = models.CharField(max_length=100, unique=True)
    only_one = models.BooleanField(default=False)
    one_per_dept = models.BooleanField(default=False)
    only_for_dept = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name_plural = 'staff roles'

    def __str__(self):
        return self.title