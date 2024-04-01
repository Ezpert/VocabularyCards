from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CardEmptyForm, CardFullForm, EditDefForm
from .models import Card, Definition
import requests


# Create your views here.
def home(request):
    # f_form = CardFullForm()
    # e_form = CardEmptyForm()
    # cards = Card.objects.all().order_by('word')

    return render(request, 'landing.html')


def viewCards(request):
    cards = Card.objects.all().order_by('word')
    return render(request, 'viewCards.html', {'cards': cards})


def viewCard(request, card_id):
    try:
        card = Card.objects.get(pk=card_id)
    except Card.DoesNotExist:
        # Handle the case where the card does not exist
        # For example, redirect to a custom error page or the homepage
        return redirect('viewCards')

    return render(request, 'viewCard.html', {'card': card})


def createPage(request):
    f_form = CardFullForm()
    e_form = CardEmptyForm()
    return render(request, 'createPage.html', {'f_form': f_form, 'e_form': e_form})


def addCard(request):
    if request.method == 'POST':

        if 'f_form' in request.POST:

            form_f = CardFullForm(request.POST)
            if form_f.is_valid():
                # Use get_or_create to find or create a Card instance with the word from the form
                new_card, created = Card.objects.get_or_create(
                    word=form_f.cleaned_data['word'].lower()
                )

                # Create a new Card instance with the word from the form
                if created:
                    new_card.save()

                definition_text = form_f.cleaned_data['definition']
                sentence_use = form_f.cleaned_data['sentence']
                new_definition = Definition(card=new_card, definition_text=definition_text, sentence_use=sentence_use)
                new_definition.save()

                return redirect('home')
        elif 'e_form' in request.POST:
            form_e = CardEmptyForm(request.POST)
            if form_e.is_valid():
                # Attempt to get or create the card
                wordF = form_e.cleaned_data['word'].lower()
                # Make a search for the definition of the word and using it in a sentence
                url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{wordF}'
                response = requests.get(url)

                # if the request is successful
                if response.status_code == 200:
                    # Convert the response to JSON
                    new_card = form_e.cleaned_data['word'].lower()
                    data = response.json()

                    definitions_and_examples = []
                    for item in data:
                        for meaning in item['meanings']:
                            for definition in meaning['definitions']:
                                definitions_and_examples.append({
                                    'word': new_card,
                                    'definition': definition['definition'],
                                    'example': definition.get('example', 'No example provided')
                                })

                    # Only save the new_card if it was created and we have definitions and examples

                    context = {'definitions_and_examples': definitions_and_examples}
                    return render(request, 'wordSearch.html', context)

                else:
                    # Handle the case where the API request failed
                    print("Failed to fetch data from the URL.")
                    return redirect('createPage')
            else:
                return render(request, 'landing.html')


def searchAdd(request, word, definition, example="No example provided"):
    if request.method == 'POST':
        if example != "No example provided":
            print('hello!')
            word_lower = word.lower()
            new_card, created = Card.objects.get_or_create(word=word_lower)

            if created:
                new_card.save()

            # Use get_or_create for the Definition model
            new_def, created = Definition.objects.get_or_create(
                card=new_card,
                definition_text=definition,
                sentence_use=example
            )

            # If the definition was not created (meaning it already existed), you might want to handle this case
            if not created:
                print("Definition already exists.")
                return redirect('createPage')
            else:
                new_def.save()

            return redirect('createPage')
        else:

            return redirect('home')

    else:
        print("ERROR!!!!")
        return redirect('createPage')


def deleteCard(request, card_id):
    if request.method == 'POST':
        Card.objects.filter(pk=card_id).delete()
        return redirect('viewCards')
    else:
        return redirect('viewCards')


def deleteDef(request, def_id):
    if request.method == 'POST':
        try:
            definition = Definition.objects.get(pk=def_id)
            card_id = definition.card.id
            definition.delete()
            return redirect('viewCard', card_id=card_id)
        except Definition.DoesNotExist:
            return redirect('viewCards')  # Redirect to 'viewCards' if the definition does not exist
    else:
        return redirect('viewCards')  # Redirect to 'viewCards' for non-POST requests


def editWordPage(request, card_id):
    card = Card.objects.get(pk=card_id)
    e_form = CardEmptyForm()
    # Was going to edit the cards and possibly be able to edit each definition.
    return render(request, 'editWord.html', {'card': card, 'e_form': e_form})


def editWord(request, card_id):
    print("Request received")  # Debugging line
    if request.method == 'POST':
        card_id = request.POST.get('card-id')
        def_id = request.POST.get('def-id')
        word_text = request.POST.get('word-text')
        def_text = request.POST.get('def-text')
        sentence = request.POST.get('sentence-use')

        print(
            f"Card ID: {card_id},"
            f" Word Text: {word_text},"
            f" Definition ID: {def_id}"
            f", Definition: {def_text}, "
            f"Sentence: {sentence}")

        try:
            card = Card.objects.get(pk=card_id)
            card.word = word_text.lower()
            definition = Definition.objects.get(pk=def_id)
            definition.definition_text = def_text
            definition.sentence_use = sentence

            card.save()
            definition.save()

            return JsonResponse({'status': 'success'}, status=200)
        except Definition.DoesNotExist:
            return JsonResponse({'status': 'Definition not found'}, status=404)
        except Card.DoesNotExist:
            return JsonResponse({'status': 'Card not found'}, status=404)
    else:
        return HttpResponseNotAllowed(['POST'])


def editDefPage(request, def_id):
    definition = Definition.objects.get(pk=def_id)
    editForm = EditDefForm()
    return render(request, 'editDef.html', {'def': definition, 'editForm': editForm})


def editDef(request, def_id):
    if request.method == 'POST':
        definition = Definition.objects.get(pk=def_id)
        c_id = definition.card.id
        word_name = definition.card.word

        if 'editForm' in request.POST:
            editForm = EditDefForm(request.POST)
            if editForm.is_valid():
                definition.definition_text = editForm.cleaned_data['definition']
                definition.sentence_use = editForm.cleaned_data['sentence']
                definition.save()
                return redirect('viewCard', card_id=c_id)
            else:
                # If the form is not valid, re-render the form with errors

                print(editForm.errors)
                return render(request, 'edit_definition.html', {'form': form_f})
        else:
            return redirect('viewCard', card_id=c_id)
    else:
        return HttpResponse("Invalid request method", status=400)
