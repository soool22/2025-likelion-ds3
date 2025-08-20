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
        widget=forms.PasswordInput,  # 입력 시 **** 표시
    )

    class Meta:
        model = Store
        fields = ['name', 'address', 'image', 'description', 'category', 'open_time', 'close_time', 'secret_code']
        widgets = {
            'description': forms.Textarea(attrs={'rows':3}),
            'category': forms.CheckboxSelectMultiple(),
        }