from django.shortcuts import render
from django.http import JsonResponse
from modelosBd.materialPI.models import MaterialPI
from Conexiones.conectionOdoo import OdooAPI

# Create your views here.

#? Consultas a base de datos PostgreSQL
#* Controlador para traer todos los materialesPI de la base de datos
def getMaterialsPIPSQL(request):
    materialsPIPSQL = MaterialPI.objects.all().values(  'id', 'producto', 'insumo', 'cantidad'  )
    return JsonResponse(list(materialsPIPSQL), safe=False)


#? Consultas ara conexión con Odoo
#* Llenar la base de datos con los datos correspondientes entre Producto contine Insumos
def pullMaterialPi(request):

    conOdoo = OdooAPI()

    try:
        result = conOdoo.getInsumoByProduct()
        return JsonResponse(result)


    except Exception as e:
        return JsonResponse({
            'status'  : 'error',
            'message' : f'Ha ocurrido un error al tratar de insertar los datos: {str(e)}'
        })
    