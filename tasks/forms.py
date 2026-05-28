from django import forms 
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'important', 'scheduled_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción'}),
            'important': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'scheduled_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        labels = {
            'title': 'Título',
            'description': 'Descripción',
            'important': 'Importante',
            'scheduled_date': 'Fecha programada',
        }


class StatsFilterForm(forms.Form):
    start_date = forms.DateField(required=False, label='Fecha de inicio', widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    end_date = forms.DateField(required=False, label='Fecha de fin', widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))