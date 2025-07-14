from django.http import JsonResponse
from django.db.models import F, ExpressionWrapper, FloatField
from django.db.models.functions import Cast

from Conexiones.conectionOdoo import OdooAPI
from modelosBd.insumos.models import Insumos
from modelosBd.productos.models import Productos
from modelosBd.materialPI.models import MaterialPI



#Ruta de prueba
def hello(request):
    return JsonResponse({"menssage":"Hello World"})


#!Este ya no va a servir aquí
#Controlador para traer la cantidad de productos vendidos por producto
def get_sales_by_product(request):
    filtro_productos = ""

    #Conexión con Odoo
    conOdoo = OdooAPI()

    message = conOdoo.search_read_sales_by_product(start_date='2024-01-01', end_date='2025-07-01') 
    return JsonResponse(message)


#!Actualizar máximos y mínimos de Odoo. 
def updateMinMax(request):

    response = []
    #? Traemos los datos que son necesarios 
    #? Esta consulya trae los productos que no son compartidos
    insumosNoCompartidos = MaterialPI.objects.filter(
        producto__tipoProducto='INTERNO',
        insumo__sku__regex=r'^((?!00).)*$'  # Excluir SKUs que contienen '00'
    ).select_related(
        'producto', 'insumo'
    ).values(
        Producto_Id=F('producto__id'),
        Nombre_Producto=F('producto__nombre'),
        ID_Insumo=F('insumo__id'),
        Cantidad=F('cantidad'),
        Nombre_Insumo=F('insumo__nombre'),
        SKU=F('insumo__sku'),
        Insumo_Promedio=ExpressionWrapper(
            F('cantidad') * 84,
            output_field=FloatField()
        )
    ).order_by('producto__nombre').first()


    #? Consulta para los insumos compartidos
    insumosCompartidos = MaterialPI.objects.filter(
        producto__tipoProducto='INTERNO',
        insumo__sku__regex=r'00'
    ).select_related(
        'producto', 'insumo'
    ).values(
        Producto_Id=F('producto__id'),
        Nombre_Producto=F('producto__nombre'),
        Id_Insumo=F('insumo__id'),
        Cantidad=F('cantidad'),
        Nombre_Insumo=F('insumo__nombre'),
        SKU=F('insumo__sku'),
        Insumo_Promedio=ExpressionWrapper(
            F('cantidad') * 84,
            output_field=FloatField()
        )
    ).order_by('producto__nombre').first()



    #!hacemos los calculos correspondientes de los insumos 

    """ for result in queryset:
        response.append({
            'todo' : result
        })"""
 
    return JsonResponse({
        'status'         : 'success', 
        'compartidos'    : insumosNoCompartidos,
        'no_compartidos' : insumosCompartidos
    })