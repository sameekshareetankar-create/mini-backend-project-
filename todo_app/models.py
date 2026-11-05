from django.db import models

# Create your models here.
class todo_table(models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=30)
    done = models.BooleanField(default=False)
    created = models.DateField(auto_now_add=True)
    