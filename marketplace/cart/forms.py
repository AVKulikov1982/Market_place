from django import forms
# from django.utils.translation import gettext_lazy as _

#PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]


class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(label='количество', min_value=1)
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)