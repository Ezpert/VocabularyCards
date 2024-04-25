from django import forms


class CardFullForm(forms.Form):
    word = forms.CharField(label='Word', max_length=100,  widget=forms.TextInput(attrs={"class": "form-word"}))
    definition = forms.CharField(label='Definition', max_length=300,  widget=forms.TextInput(attrs={"class": "form-def"}))
    sentence = forms.CharField(label='Sentence', max_length=250,  widget=forms.TextInput(attrs={"class": "form-sen"}))


class CardEmptyForm(forms.Form):
    word = forms.CharField(label='Word', max_length=100)


class EditDefForm(forms.Form):
    definition = forms.CharField(label='Definition', max_length=300, required=True)
    sentence = forms.CharField(label='Sentence', max_length=250)