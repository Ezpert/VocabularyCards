from django import forms
from django.utils.safestring import mark_safe


class CardFullForm(forms.Form):

    word = forms.CharField(label=mark_safe('<span class="custom-label-class" id="word-label">Word</span>'), max_length=100,  widget=forms.TextInput(attrs={"class": "form-word", "placeholder": "Enter a Word"}))
    definition = forms.CharField(label=mark_safe('<span class="custom-label-class" id="definition-label">Definition</span>'), max_length=300,  widget=forms.TextInput(attrs={"class": "form-def", "placeholder": "Enter Definition"}))
    sentence = forms.CharField(label=mark_safe('<span class="custom-label-class" id="sentence-label">Sentence</span>'), max_length=250,  widget=forms.TextInput(attrs={"class": "form-sen", "placeholder": "Enter Sentence"}))


class CardEmptyForm(forms.Form):
    word = forms.CharField(label='',max_length=100, widget=forms.TextInput(attrs={"class": "form-search", "placeholder": "Search"}))


class EditDefForm(forms.Form):
    definition = forms.CharField(label='Definition', max_length=300, required=True)
    sentence = forms.CharField(label='Sentence', max_length=250)