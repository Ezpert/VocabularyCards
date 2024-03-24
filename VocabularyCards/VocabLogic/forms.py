from django import forms


class CardFullForm(forms.Form):
    word = forms.CharField(label='Word', max_length=100)
    definition = forms.CharField(label='Definition', max_length=300)
    sentence = forms.CharField(label='Sentence', max_length=250)


class CardEmptyForm(forms.Form):
    word = forms.CharField(label='Word', max_length=100)


class EditDefForm(forms.Form):
    definition = forms.CharField(label='Definition', max_length=300, required=True)
    sentence = forms.CharField(label='Sentence', max_length=250)