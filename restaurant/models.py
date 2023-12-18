from django.db import models

# Create your models here.
class Menu(models.Model):
    name = models.CharField(max_length=200)
    price = models.IntegerField()
    description = models.TextField(max_length=1000, default='')

    def __str__(self):
        return f"{self.name}, {self.price}rs"

class About(models.Model):
    about_text = models.CharField(max_length=2000)

class Book(models.Model):
    name = models.CharField(max_length=200)
    datetime = models.DateTimeField()
    guests_no = models.PositiveIntegerField() #choices=((i,i) for i in range(1, 101))
    preference = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name}, {self.datetime}"