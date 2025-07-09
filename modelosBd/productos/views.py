from django.shortcuts import render
from django.http import JsonResponse
from modelosBd.productos.models import Productos
from Conexiones.conectionOdoo import OdooAPI


# Create your views here.

#? Consultas a Base de datos PostgreSQL
#* Controlador para traer todos los productos de la base de datos
def getProductsPSQL(request):
    productsPSQL = Productos.objects.all().values(  'id', 'nombre', 'sku', 'marca', 'existenciaActual', 'maxActual', 'minActual'  ) 
    return JsonResponse(list(productsPSQL), safe=False)


#? Consultas para conexión con Odoo
#* Llenar la base de datos con los productos existentes en Odoo
def pullProductsOdoo(request):
    #Instancia con Odoo
    conOdoo = OdooAPI()

    try: 
        #Traer los productos que existen de odoo
        productsOdoo = conOdoo.get_product_by_category(category= "PRODUCTO TERMINADO")

        if productsOdoo['status'] == 'success':
            #traemos los productos existentes de PostgreSQL
            productsPSQL = Productos.objects.all().values_list('sku', flat=True)

            #añadir los productos a la base de datos de PostgreSQL
            new_products = []
            for product in productsOdoo['products']:
                if product['sku']: 
                    sku = product.get('sku', '').strip()
                    marca = product.get('marca')
                    if sku and sku not in productsPSQL:
                        new_products.append({
                            'id' : product.get('id')
                        })

                        createProduct = Productos.objects.create(
                            id = product.get('id'),
                            sku = sku,
                            nombre = product.get('name'),
                            maxActual = product.get('maxActual'),
                            minActual = product.get('minActual'),
                            existenciaActual =  product.get('existenciaActual'),
                            marca = marca[1],
                        )

            return JsonResponse({
                'status'  : 'success',
                'message' : f'Se han creado {len(new_products)} nuevos productos'
            })

        else:
            return JsonResponse({
                'status'  : 'error',
                'message' : productsOdoo['message']
            })
    
    except Exception as e:
        return JsonResponse({
            'status'  : 'error',
            'message' : f'Ha ocurrido un error al tratar de insertar los datos: {str(e)}'
        })
