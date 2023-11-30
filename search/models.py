from django.db import models

class PalabraURL(models.Model):
    palabra = models.CharField(max_length=50, unique=True)
    urls = models.TextField()