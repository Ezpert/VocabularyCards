from django.db import models


class Card(models.Model):
    word = models.CharField(max_length=200, unique=True)

    def __str__(self):
        """String for representing the Model object."""
        return self.word


class Definition(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='definitions')
    definition_text = models.TextField(max_length=200, default='Default definition text', unique=True)
    sentence_use = models.TextField(max_length=200, default='Default sentence use')

    def __str__(self):
        """String for representing the Model object."""
        return f"{self.definition_text} (for {self.card.word})"
