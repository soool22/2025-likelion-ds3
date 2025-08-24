from django import forms
from .models import Store

# 가게 정보 입력 form
class StoreForm(forms.ModelForm):
    open_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label="오픈 시간",
        required=False
    )
    close_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label="종료 시간",
        required=False
    )
    secret_code = forms.CharField(
        max_length=10,
        label="점주 코드",
        help_text="누적 금액 업데이트용 점주 코드",
        widget=forms.PasswordInput(attrs={'placeholder': '챌린지에 이용되는 코드입니다.'}),  # 입력 시 **** 표시
    )

    class Meta:
        model = Store
        fields = ['name', 'address', 'gu_name', 'number', 'image', 'description', 'category', 'open_time', 'close_time', 'secret_code']
        widgets = {
            'address': forms.TextInput(attrs={'placeholder': '지번, 도로명'}),
            'gu_name': forms.TextInput(attrs={'placeholder': '지역구 / ex)도봉구'}),
            'description': forms.Textarea(attrs={'rows':3}),
            'number': forms.TextInput(attrs={'placeholder': '전화번호'}),
            'category': forms.CheckboxSelectMultiple(),
        }