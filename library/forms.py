from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["title", "subject", "level", "pdf_url", "cover_image"]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'border p-2 w-full'}),
            'subject': forms.TextInput(attrs={'class': 'border p-2 w-full'}),
            'level': forms.Select(attrs={'class': 'border p-2 w-full'}),
            'pdf_file': forms.FileInput(attrs={'class': 'border p-2 w-full'}),
            'cover_image': forms.FileInput(attrs={'class': 'border p-2 w-full'}),
        }