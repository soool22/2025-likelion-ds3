from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "price", "image", "description", "is_main"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 가격 필수 설정
        self.fields['price'].required = True
        # is_main 체크박스로 표시
        self.fields['is_main'].widget = forms.CheckboxInput()
