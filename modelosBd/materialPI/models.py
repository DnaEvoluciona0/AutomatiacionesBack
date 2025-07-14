from django.db import models
from modelosBd.productos.models import Productos
from modelosBd.insumos.models import Insumos

# Create your models here.
class MaterialPI(models.Model):
    producto = models.ForeignKey(Productos, on_delete=models.CASCADE)
    insumo = models.ForeignKey(Insumos, on_delete=models.CASCADE)
    cantidad = models.FloatField()

    class Meya:
        unique_together = ('producto', 'insumo')