from django.shortcuts import render
from django.http import JsonResponse
from modelosBd.materialPI.models import MaterialPI
from modelosBd.productos.models import Productos
from modelosBd.insumos.models import Insumos
from Conexiones.conectionOdoo import OdooAPI
from modelosBd.materialPI.ctr_matrerialPI import getInsumoByProduct

# Create your views here.

#? Consultas a base de datos PostgreSQL
#* Controlador para traer todos los materialesPI de la base de datos
def getMaterialsPIPSQL(request):
    materialsPIPSQL = MaterialPI.objects.all().values(  'id', 'producto', 'insumo', 'cantidad'  )
    return JsonResponse(list(materialsPIPSQL), safe=False)


#? Consultas ara conexión con Odoo
#* Llenar la base de datos con los datos correspondientes entre Producto contine Insumos
def pullMaterialPi(request):

    try:
        result = getInsumoByProduct()

        if result['status'] == 'success':

            MaterialPI.objects.all().delete()

            cantidad = 0
            for material in result['message']:
                productSKU = material.get('product')[1].split(']')[0]
                productSKU = productSKU.split('[')[1]
                materialSKU = material.get('material')[1].split(']')[0]
                materialSKU = materialSKU.split('[')[1]

                try: 
                    instanceProduct = Productos.objects.get(sku=f'{productSKU}')
                    
                except Productos.DoesNotExist:
                    continue

                try:
                    instanceInsumo = Insumos.objects.get(sku=f'{materialSKU}')
                except Insumos.DoesNotExist:
                    continue

                tupleMaterial = (Productos.objects.only('id').get(sku=productSKU).id, material.get('material')[0])

                if tupleMaterial:
                
                    if instanceProduct and instanceInsumo:
                        cantidad += 1
                        materialPI = MaterialPI.objects.create(
                            producto = instanceProduct,
                            insumo = instanceInsumo,
                            cantidad = material.get('qty')
                        )

            return JsonResponse({
                'status' : 'success',
                'message' : f'Se han cargado {cantidad} materiales de productos.'
            })
        return JsonResponse({
            'status'  : 'error',
            'message' : result['message']
        })

    except Exception as e:
        return JsonResponse({
            'status'  : 'error',
            'message' : f'Ha ocurrido un error al tratar de insertar los datos: {str(e)}'
        })
    