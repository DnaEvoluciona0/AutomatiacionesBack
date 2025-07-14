from django.db import models

# Create your models here.
class Clientes(models.Model):
    idCliente=models.BigIntegerField(primary_key=True)
    nombre = models.CharField(max_length=200)
    pais = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=200)
    tipoCliente=models.CharField(max_length=20, default="Cliente Nuevo")
    numTransacciones=models.BigIntegerField(default=0)