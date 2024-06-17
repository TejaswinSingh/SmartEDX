import uuid
from .department import Department

from django.db import models


class Programme(models.Model):
    """ department programmes """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='programmes'
    )

    class Meta:
        verbose_name_plural = 'programmes'

    def __str__(self):
        return f'{self.name}, {self.department}'