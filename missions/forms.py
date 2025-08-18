from django import forms
from .models import Mission
from django.utils import timezone

# 챌린지 생성 
class MissionForm(forms.ModelForm):
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="미션 시작일",
        initial=timezone.now
    )
    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="미션 종료일",
        initial=timezone.now
    )

    class Meta:
        model = Mission
        fields = [
            'title', 
            'description', 
            'reward_description', 
            'mission_type',     # 챌린지 종류 선택
            'target_value',     # 목표치 입력 (금액, 방문 횟수, 기간)
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