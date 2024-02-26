from django.shortcuts import render, redirect
from .forms import CardEmptyForm, CardFullForm
from .models import Card, Definition
import requests


# Create your views here.
def home(request):
    f_form = CardFullForm()
    e_form = CardEmptyForm()
    cards = Card.objects.all().order_by('word')

    return render(request, 'landing.html', {'f_form': f_form, 'e_form': e_form, 'cards': cards})


def addCard(request):
    if request.method == 'POST':

        if 'f_form' in request.POST:

            form_f = CardFullForm(request.POST)
            if form_f.is_valid():
                # Use get_or_create to find or create a Card instance with the word from the form
                new_card, created = Card.objects.get_or_create(
                    word=form_f.cleaned_data['word']
                )

                # Create a new Card instance with the word from the form
                if created:
                    new_card.save()

                definition_text = form_f.cleaned_data['definition']
                print(definition_text)
                sentence_use = form_f.cleaned_data['sentence']
                new_definition = Definition(card=new_card, definition_text=definition_text, sentence_use=sentence_use)
                new_definition.save()

                return redirect('home')
        elif 'e_form' in request.POST:

            form_e = CardEmptyForm(request.POST)
            if form_e.is_valid():

                # if the card is already in the database then get it from there.
                new_card, created = Card.objects.get_or_create(
                    word=form_e.cleaned_data['word']
                )
                # if it was created then we save it to the database.
                # if created:
                #     new_card.save()

                # Make a search for the definition of the word and using it in a sentence
                url = f'https://wordsapiv1.p.mashape.com/words/{new_card.word}'
                response = requests.get(url)

                # if the request is successful
                if response.status_code == 200:
                    # Convert the response to JSON
                    data = response.json()
                    print(data)
                else:
                    print("Failed to fetch data from the URL.")

                return redirect('home')
        else:
            return render(request, 'landing.html')
