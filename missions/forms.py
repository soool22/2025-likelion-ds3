from django import forms
from .models import Mission
from django.utils import timezone

class MissionForm(forms.ModelForm):
    # 초 단위 제거
    now = timezone.now().replace(second=0, microsecond=0)

    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'step': 60,  # 초 단위 제거
            }
        ),
        label="미션 시작일",
        initial=now
    )
    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'step': 60,
            }
        ),
        label="미션 종료일",
        initial=now
    )

    class Meta:
        model = Mission
        fields = [
            'title', 
            'description',
            'reward_type',
            'reward_points',
            'reward_description', 
            'mission_type',
            'target_value',
            'start_date', 
            'end_date'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'mission_type': "미션 종류",
            'target_value': "목표치",
        }

# 누적 금액 입력
class AmountInputForm(forms.Form):
    amount = forms.IntegerField(label="소비 금액")
    secret_code = forms.CharField(label="점주 코드", widget=forms.PasswordInput)
