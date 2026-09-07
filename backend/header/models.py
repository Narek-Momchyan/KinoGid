
from django.db import models
class Logo(models.Model):
    name= models.CharField(max_length=50)
    href = models.CharField(max_length=200)
    def __str__(self):
        return self.name
class Language(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

class Navbar(models.Model):
    title = models.CharField(max_length=50, verbose_name="Վերնագիր")
    slug = models.SlugField()
    lang = models.CharField(max_length=2, default='am', verbose_name="Լեզու")
    href = models.CharField(max_length=200,verbose_name="Ուղղորդում" , blank=True,null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ('slug', 'lang') 

    def __str__(self):
        return f"{self.title} ({self.lang.upper()})"


class Category(models.Model):
    navbar = models.ForeignKey(Navbar, on_delete=models.CASCADE, related_name='categories')
    href = models.CharField(max_length=200,verbose_name="Ուղղորդում", null=True,blank=True)
    name = models.CharField(max_length=100, verbose_name="Կատեգորիայի անուն")
    slug = models.SlugField()
    lang = models.CharField(max_length=2, default='am', verbose_name="Լեզու")

    class Meta:
        unique_together = ('slug', 'lang')

    def __str__(self):
        return f"{self.name} ({self.lang.upper()})"