from django import forms
from .models import Store

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

    class Meta:
        model = Store
        fields = ['name', 'address', 'image', 'description', 'category', 'open_time', 'close_time']
        widgets = {
            'description': forms.Textarea(attrs={'rows':3}),
            'category': forms.CheckboxSelectMultiple(),
        }
