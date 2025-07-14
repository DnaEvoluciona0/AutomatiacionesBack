from django.db import models
from modelosBd.clientes.models import Clientes

# Create your models here.
class Ventas(models.Model):
    idVenta = models.CharField(max_length=20, primary_key=True)
    fecha = models.DateTimeField()
    idCliente = models.ForeignKey(Clientes, related_name="ventasCliente", on_delete=models.CASCADE)
    paisVenta = models.CharField(max_length=100)
    estadoVenta = models.CharField(max_length=100)
    ciudadVenta = models.CharField(max_length=200)
    unidad = models.CharField(max_length=20)
    vendedor = models.CharField(max_length=200)
    total = models.DecimalField(decimal_places=2, max_digits=20)