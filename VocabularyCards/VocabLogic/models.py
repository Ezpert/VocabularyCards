from django.db import models


class Card(models.Model):
    word = models.CharField(max_length=200)

    def __str__(self):
        """String for representing the Model object."""
        return self.word


class Definition(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='definitions')
    definition_text = models.CharField(max_length=200)
    sentence_use = models.CharField(max_length=200)

    def __str__(self):
        """String for representing the Model object."""
        return f"{self.definition_text} (for {self.card.word})"
