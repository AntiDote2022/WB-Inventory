from django import forms
from .models import Production, Location, MaterialPurchase, WBShipment

class ProductionForm(forms.ModelForm):
    class Meta:
        model = Production
        fields = ['date', 'product', 'location', 'produced_qty']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'Выберите дату производства'
            }),
            'product': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'Выберите продукт'
            }),
            'location': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'Выберите склад'
            }),
            'produced_qty': forms.NumberInput(attrs={
                'step': '0.1',
                'class': 'form-control',
                'placeholder': '0.0',
                'min': '0'
            }),
        }

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = MaterialPurchase
        fields = ['date', 'material', 'quantity', 'unit_price', 'supplier']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'Дата закупки'
            }),
            'material': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'Выберите материал'
            }),
            'quantity': forms.NumberInput(attrs={
                'step': '0.1',
                'class': 'form-control',
                'placeholder': '0.0',
                'min': '0'
            }),
            'unit_price': forms.NumberInput(attrs={
                'step': '0.01',
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0'
            }),
            'supplier': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название поставщика'
            }),
        }

class ShipmentForm(forms.ModelForm):
    class Meta:
        model = WBShipment
        fields = ['date', 'from_location', 'to_location', 'product', 'quantity', 'wb_shipment_number']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'Дата отгрузки'
            }),
            'from_location': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'Откуда'
            }),
            'to_location': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'Куда (WB склад)'
            }),
            'product': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'Выберите продукцию'
            }),
            'quantity': forms.NumberInput(attrs={
                'step': '0.1',
                'class': 'form-control',
                'placeholder': '0.0',
                'min': '0'
            }),
            'wb_shipment_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'WB-2026-00123'
            }),
        }
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'phone', 'company']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (999) 123-45-67'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название компании'}),
        }
