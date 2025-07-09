from django.http import JsonResponse
from Conexiones.conectionOdoo import OdooAPI

#Ruta de prueba
def hello(request):
    return JsonResponse({"menssage":"Hello World"})


#Controlador para traer la cantidad de productos vendidos por producto
def get_sales_by_product(request):
    filtro_productos = ""

    #Conexión con Odoo
    conOdoo = OdooAPI()

    message = conOdoo.search_read_sales_by_product(start_date='2024-01-01', end_date='2025-07-01') 
    return JsonResponse(message)