from django.db import models
from modelosBd.productos.models import Productos

# Create your models here.
class Caducidades(models.Model):
    fechaCaducidad = models.DateField()
    cantidad = models.IntegerField()
    productoId = models.ForeignKey(Productos, related_name="productoCaducidad", on_delete=models.CASCADE)