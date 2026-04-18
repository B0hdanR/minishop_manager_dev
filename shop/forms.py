from django import forms
from shop.models import Product, Order, ProductCategory


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "price",
            "stock_quantity",
            "category",
        ]


class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Category name",
            })
        }


class ProductCategorySearchForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        required=False,
        label="",
        widget=forms.TextInput(attrs={
            "placeholder": "Search category",
            "class": "form-control",
        }),
    )


class OrderStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["status"]


class OrderFilterForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        required=False,
        label="",
        widget=forms.TextInput(attrs={
            "placeholder": "Order ID or user",
            "class": "form-control",
        }),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[("", "Statuses")] + Order.STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    total_min = forms.DecimalField(
        required=False,
        min_value=0,
        label="Min total",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Min total",
        }),
    )

    total_max = forms.DecimalField(
        required=False,
        min_value=0,
        label="Max total",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Max total",
        }),
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "form-control",
        }),
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "form-control",
        }),
    )


class ProductFilterForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        required=False,
        label="",
        widget=forms.TextInput(attrs={
            "placeholder": "Product name",
            "class": "form-control",
        })
    )

    category = forms.ModelChoiceField(
        required=False,
        queryset=ProductCategory.objects.all(),
        widget=forms.Select(attrs={
            "class": "form-control",
            "placeholder": "Category",
        }),
    )

    price_min = forms.DecimalField(
        required=False,
        min_value=0,
        label="Min total",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Min total",
        }),
    )

    price_max = forms.DecimalField(
        required=False,
        min_value=0,
        label="Max total",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Max total",
        }),
    )
