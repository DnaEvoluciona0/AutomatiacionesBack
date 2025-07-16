from django.db import models

# Create your models here.
class Insumos(models.Model):
    nombre = models.CharField(max_length=200)
    sku = models.CharField(max_length=15)
    marca = models.CharField(max_length=150, default='')
    maxActual = models.IntegerField()
    minActual = models.IntegerField()
    existenciaActual =  models.IntegerField(default=0)
    categoria = models.CharField(max_length=150, default='')
    proveedor = models.CharField(max_length=200, default="")