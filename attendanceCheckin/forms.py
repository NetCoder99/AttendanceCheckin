from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy

from attendanceCheckin.models import CheckinStudentRecords
from attendanceData.models import BeltsByRank


class CheckinForm(forms.ModelForm):
    formTitle   = "Student Checkin"
    banner      = forms.ImageField()
    studentName = "Luke Skywalker"

    badgeNumber = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'input w-1/4',
            'placeholder': 'Card Number',
        })
    )

    class Meta:
        model = CheckinStudentRecords
        fields = (
            'badgeNumber',
            'firstName',
            'lastName',
            'status',
            'studentImageBase64',
            'banner',
            'studentImageField'
        )


class RequiredRanks(forms.Form):
    student_name = "Luke Skywalker"
    badge_number = forms.IntegerField(widget=forms.HiddenInput())
    # Choices are defined as a tuple of 2-tuples: (internal_value, human_readable_name)
    RANKS = [
        ('1', 'White Belt'),
        ('2', 'Orange Belt'),
        ('3', 'Yellow Belt'),
        ('4', 'Blue Belt'),
        ('5', 'Green Belt'),
        ('6', 'Purple Belt'),
        ('7', 'Brown Belt'),
        ('8', 'Black Belt'),
    ]
    required_ranks = forms.ChoiceField(
        choices=RANKS,
        widget=forms.Select(attrs={
            'hx-get': reverse_lazy('get_stripes'),  # Use reverse_lazy to get the URL
            'hx-trigger': 'change',
            'hx-target': '#div_belt_stripes',
            'class': 'select w-1/2',
            'style': 'border: 1px solid #d1d1d1 !important;'
        })
    )

    required_stripes = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={
            'class': 'select w-1/3',
            'style': 'border: 1px solid #d1d1d1 !important;'
        })
    )

    def __init__(self, *args, **kwargs):
        initial_rank_data = kwargs.pop('initial_rank_data')
        self.student_name = initial_rank_data['student_name']
        self.badge_number = initial_rank_data['badge_number']
        super(RequiredRanks, self).__init__(*args, **kwargs)
        self.fields['required_ranks'].initial   = initial_rank_data['current_rank_num']

    class Meta:
        fields = (
            'student_name',
            'badge_number',
            'required_ranks',
            'required_stripes',
        )

