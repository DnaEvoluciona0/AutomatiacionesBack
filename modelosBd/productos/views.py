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
        def insertProducts(products):
            if products['status'] == 'success':
                #traemos los productos existentes de PostgreSQL
                productsPSQL = Productos.objects.all().values_list('sku', flat=True)

                #añadir los productos a la base de datos de PostgreSQL
                new_products = []
                for product in products['products']:
                    if product['sku']: 
                        sku = product.get('sku', '').strip()
                        marca = product.get('marca')
                        categoria = product.get('categoria')
                        if "MAQUILAS" in categoria[1] or "MT" in sku: 
                            tipo = "MAQUILAS"
                        elif "PC" in sku:
                            tipo = "PRODUCTO COMERCIAL"
                        else:
                            tipo = "INTERNO"
                        

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
                                categoria = categoria[1],
                                tipoProducto = tipo, 
                                precio = product.get('precio')
                            )

                return ({
                    'status'  : 'success',
                    'message' : len(new_products)
                })

            else:
                return ({
                    'status'  : 'error',
                    'message' : products['message']
                })

        #Traer los productos que existen de odoo
        productsTOdoo = conOdoo.get_product_by_category(category= "PRODUCTO TERMINADO")
        productsCOdoo = conOdoo.get_product_by_category(category= "PRODUCTO COMERCIAL")

        response1 = insertProducts(productsTOdoo)
        response2 = insertProducts(productsCOdoo)

        if response1['status'] == "success" and response2['status'] == 'success':

            totalRows = response1['message'] + response2['message']
            return JsonResponse({
                'status'  : 'success',
                'message' : f'Se han agregado correctamente {totalRows} datos'
            })

        return JsonResponse({
            'status'  : 'error',
            'message' : response1['message']
        })
    
    except Exception as e:
        return JsonResponse({
            'status'  : 'error',
            'message' : f'Ha ocurrido un error al tratar de insertar los datos: {str(e)}'
        })
