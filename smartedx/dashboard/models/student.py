import uuid
from .batch import Batch

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class Student(models.Model):
    """ batch students """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name='student')
    batch = models.ForeignKey(
        Batch,
        on_delete=models.PROTECT,
        related_name='students'
    )

    class Meta:
        verbose_name_plural = 'students'

    def clean(self):
        # Check if the user is associated with a Staff instance
        if hasattr(self.user, 'staff'):
            raise ValidationError('This user is already registered as a staff member.')

    def full_name(self):
        if not self.user.first_name and not self.user.last_name:
            return f'User({self.user.username})'
        return f'{self.user.first_name} {self.user.last_name}'.strip()

    def __str__(self):
        name = self.full_name()
        return f'{name}, {self.batch}'