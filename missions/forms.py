from django import forms
from .models import Mission
from django.utils import timezone

class MissionForm(forms.ModelForm):
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="미션 시작일"
    )
    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="미션 종료일"
    )

    class Meta:
        model = Mission
        fields = ['title', 'description', 'reward_description', 'start_date', 'end_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows':3}),
        }