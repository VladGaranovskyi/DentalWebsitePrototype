from django.db import models

class Comment(models.Model):
    name = models.CharField(max_length=40)
    content = models.CharField(max_length=400)
    posted_on = models.DateField(auto_now=True)
