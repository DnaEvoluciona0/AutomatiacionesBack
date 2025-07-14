from django.shortcuts import render
from django.http import JsonResponse
from modelosBd.ventasPV.models import VentasPV

# Create your views here.
# Create your views here.
#? Consultas para conexión con Odoo
def pullLineaVentaOdoo(productos, idVenta):
    try:
        
        for producto in productos:
            
            try:
                VentasPV.objects.create(
                    cantidad        = producto['quantity'],
                    precioUnitario  = producto['price_unit'],
                    subtotal        = producto['price_subtotal'],
                    idVenta_id      = idVenta,
                    idProducto_id   = producto['product_id'][0]
                )
            except:
                VentasPV.objects.create(
                    cantidad        = producto['quantity'],
                    precioUnitario  = producto['price_unit'],
                    subtotal        = producto['price_subtotal'],
                    idVenta_id      = idVenta,
                    idInsumo_id     = producto['product_id'][0]
                )
        
        return JsonResponse({
            'status'  : 'success',
            'message' : f'Todos los productos han sido registrados'
        })   
        
    except Exception as e:
        return JsonResponse({
            'status'  : 'error',
            'message' : f'Ha ocurrido un error al tratar de insertar los datos en ventasPV: {e}'
        })