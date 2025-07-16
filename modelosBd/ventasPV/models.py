from django.db import models
from modelosBd.productos.models import Productos
from modelosBd.insumos.models import Insumos
from modelosBd.ventas.models import Ventas

# Create your models here.
class VentasPVA(models.Model):
    fecha = models.DateTimeField()
    idProducto = models.ForeignKey(Productos, related_name="ventasPVProducto", on_delete=models.CASCADE, null=True)
    idInsumo = models.ForeignKey(Insumos, related_name="ventasPVInsumos", on_delete=models.CASCADE, null=True)
    cantidad = models.BigIntegerField()
    
class VentasPVH(models.Model):
    idVenta = models.ForeignKey(Ventas, related_name="ventasPVVenta", on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    sku = models.CharField(max_length=20)
    marca = models.CharField(max_length=50)
    cantidad = models.BigIntegerField()
    precioUnitario = models.DecimalField(decimal_places=2, max_digits=20)
    subtotal = models.DecimalField(decimal_places=2, max_digits=20)