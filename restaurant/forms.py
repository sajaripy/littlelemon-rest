from django import forms
import datetime
from .models import Book

class BookForm(forms.ModelForm):
    datetime = forms.DateTimeField(
        label='Date and Time',
        widget=forms.widgets.DateTimeInput(attrs={'type':'datetime-local'}),
    )
    def clean_date(self):
        datetime = self.cleaned_data['datetime']
        if datetime < datetime.date.today():
            raise forms.ValidationError("The date cannot be in the past!")
        return datetime
    class Meta:
        model = Book
        fields = ['name', 'datetime', 'guests_no', 'preference']