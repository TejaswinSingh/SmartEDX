from core.models import AssignmentSubmission

from django.forms import ModelForm


class AssignmentSubmissionForm(ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ["assignment", "student", "file"]