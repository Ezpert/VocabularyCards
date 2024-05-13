from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect, get_object_or_404
from openai import OpenAI
from .forms import CardEmptyForm, CardFullForm, EditDefForm
from .models import Card, Definition
from django.urls import reverse
import requests
from django.core.cache import cache
import os
from dotenv import load_dotenv

load_dotenv(override=True)  # take environment variables from .env.

client = OpenAI(
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY")
)


def chat_completion(
        message,
        model="gpt-4",
        prompt="You are a helpful assistant.",
        temperature=0,
        messages=[],
):
    # Add the prompt to the messages list
    if prompt is not None:
        messages = [{"role": "system", "content": prompt}] + messages

    if message is not None:
        # Add the user's message to the messages list
        messages += [{"role": "user", "content": message}]

    print (messages)


    # Make an API call to the OpenAI ChatCompletion endpoint with the model and messages
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )

    # Extract and return the AI's response from the API response
    # Check if completion and completion.choices are not None
    if completion is not None and completion.choices:
        return completion.choices[0].message.content.strip()
    else:
        # Handle the case where completion or completion.choices is None
        return "Error generating response."


def ai_example(word=None, definition=None):
    prompt = """

        You are a Professional Dictionary. You are going to be given a word and a definition with no sentence example and you are
    to make a sentence using the context of the definition. You MUST include the given Word in the sentence response, 
    If you do not use it the example would be considered incorrect! You should respond with nothing but the sentence, meaning do not add
    any other formatting besides the sentence string.
    This is an example of a word and a definition that are without an example:
    Word: ling 
    Definition: Any of various marine food fish, of the genus Molva, resembling the cod
    "No example provided"
    
    
    These are correct examples:
        Word: minion 
        Definition: The smallest member of a batch or sample or the lower bound of a probability distribution
        In the statistical analysis, the minion represented the lowest score in the entire data set.
        
        
        Word: minion
        Definition: A loyal servant of another, usually a more powerful being.
        The archvillain deployed his minions to simultaneously rob every bank in the city.
    
    These are incorrect examples:
        Word: minion
        Definition: A period of minimum brightness or energy intensity (of a star).
        The Maunder minimum of the Sun reportedly corresponded to a period of great cold on Earth.
        Reason for being incorrect: The word was not used in the sentence, make sure to always include the word in the examples!
        
        Word: minion
        Definition: The lowest limit.
        We need a minimum of three staff members on duty at all time.
        Reason for being incorrect: The word was not used in the sentence, make sure to always include the word in the examples!
        
        
        Word: son
        Definition: A male person who has such a close relationship with an older or otherwise more authoritative person that he can be regarded as a son of the other person.
        "The young apprentice admired his mentor so much that he considered him a son +, a father figure in his life."
        Reason for being incorrect: The sentence includes a random character i.e '+'. Do not include random characters inside the examples!
        
        Word: son
        Definition: A male adopted person in relation to his adoptive parents.
        "After years of longing for a child, they finally adopted a boy and proudly introduced him as their son+."
        Reason for being incorrect: The sentence includes a random character i.e '+'. Do not include random characters inside the examples!
        
        Make sure that the responses given do not include a '+' inside of the sentence unless it makes sense grammatically!
        
    """
    outputs = {}
    message = f"Word: {word} + \n Definition: {definition}"
    response = chat_completion(message, prompt=prompt, model='gpt-4')

    print(response)
    return response


def makeSen(request):
    if request.method == 'POST':
        word_example = request.POST.get('word_example')
        definition_example = request.POST.get('definition_example')
        new_sentence = ai_example(word=word_example, definition=definition_example)
        return JsonResponse({'new_sentence': new_sentence})
    else:
        return HttpResponseNotAllowed(['POST'])


# Create your views here.
def home(request):
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
        print("Valid method!")
        if 'f_form' in request.POST:

            print("Form f found!")
            form_f = CardFullForm(request.POST)
            if form_f.is_valid():
                print("Valid form!")
                try:
                    print("Working!")
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
                    return JsonResponse({'status': 'success'}, status=200)
                except Definition.DoesNotExist:

                    return JsonResponse({'status': 'Definition not found'}, status=404)
                except Card.DoesNotExist:
                    return JsonResponse({'status': 'Card not found'}, status=404)

        elif 'e_form' in request.POST:
            print("Form e found!")
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
                                example = definition.get('example', 'No example provided')
                                if example == 'No example provided':
                                    example = 'No example Provided'
                                    # example = ai_example(word=new_card, definition=definition['definition'])
                                definitions_and_examples.append({
                                    'word': new_card,
                                    'definition': definition['definition'],
                                    'example': example

                                })

                    context = {'definitions_and_examples': definitions_and_examples}
                    return render(request, 'wordSearch.html', context)

                else:
                    # Handle the case where the API request failed
                    print("Failed to fetch data from the URL.")
                    return redirect('createPage')
            else:
                return render(request, 'landing.html')
        else:
            print("Form f or e not found!")
            return JsonResponse({'status': 'Form not found'}, status=404)
    else:
        return HttpResponseNotAllowed(['POST'])

def searchAdd(request):
    print("Request received")  # Debugging line
    if request.method == 'POST':
        print('Method: POST')
        word = request.POST.get('word')
        definition = request.POST.get('definition')
        sentence = request.POST.get('sentence')

        print(f'Word: {word} Definition: {definition} Sentence: {sentence}')

        try:

            new_card, created = Card.objects.get_or_create(
                word=word.lower()
            )
            if created:
                new_card.save()

            new_def, createdDef = Definition.objects.get_or_create(
                card_id=new_card.id,
                definition_text=definition,
                sentence_use=sentence
            )

            if createdDef:
                new_def.sentence_use = sentence
                new_def.save()

            return JsonResponse({'status': 'success'}, status=200)
        except Definition.DoesNotExist:
            return JsonResponse({'status': 'Definition not found'}, status=404)
        except Card.DoesNotExist:
            return JsonResponse({'status': 'Card not found'}, status=404)
    else:
        print('Method: GET')
        return HttpResponseNotAllowed(['POST'])


def deleteCard(request, card_id):
    if request.method == 'POST':
        Card.objects.filter(pk=card_id).delete()
        redirect_url = reverse('viewCards')
        response_data = {'redirect_url': redirect_url}

        return JsonResponse(response_data)
    else:
        return HttpResponseNotAllowed(['POST'])


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
