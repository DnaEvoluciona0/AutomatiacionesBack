from django.shortcuts import render
from django.http import JsonResponse

from modelosBd.productos.models import Productos
from modelosBd.productos.ctr_producto import get_product_all_products, get_newproducts

#? Consultas a Base de datos PostgreSQL
#* Controlador para traer todos los productos de la base de datos
def getProductsPSQL(request):
    productsPSQL = Productos.objects.all().values(  'id', 'nombre', 'sku', 'marca', 
                   'existenciaActual', 'maxActual', 'minActual'  ) 
    return JsonResponse(list(productsPSQL), safe=False)


# --------------------------------------------------------------------------------------------------
# * Función: insertProducts
# * Descripción: Inserta productos en la base de datos PostgreSQL.
#
# ! Parámetros:
#     - Recibe una lista (array) de productos. Cada producto debe contener los siguientes campos:
#       { id, name, sku, maxActual, minActual, existenciaActual, marca, categoría, rutas, fechaCreacion }
#     - Nota: Solo el campo "id" es obligatorio; los demás son opcionales.
#
# ? Condiciones para insertar un producto en la base de datos:
#     1. El producto debe tener un SKU válido (no vacío).
#     2. El producto no debe existir previamente en la base de datos PostgreSQL.
#
# ? Lógica para determinar el tipo de producto:
#     - Si la categoría contiene "MAQUILAS" o el SKU contiene "MT" → Tipo: MAQUILAS.
#     - Si el SKU contiene "PC" → Tipo: PRODUCTO COMERCIAL.
#     - Si el SKU contiene "PT":
#         · Si contiene una o más rutas → Tipo: INTERNO RESURTIBLE.
#         · Si no contiene rutas → Tipo: INTERNO NO RESURTIBLE.
#     - Si no cumple con ninguna de las condiciones anteriores → Tipo: OTROS.
# --------------------------------------------------------------------------------------------------

def insertProducts(products):
    if products['status'] == 'success':
        #traemos los productos existentes de PostgreSQL
        productsPSQL = Productos.objects.all().values_list('sku', flat=True)

        #añadir los productos a la base de datos de PostgreSQL
        new_products = []
        for product in products['products']:
            
            sku = product.get('sku', '').strip() if product['sku'] else ""
            marca = product.get('marca')
            categoria = product.get('categoria')
            rutas = len(product.get('routes'))

            if "MAQUILAS" in categoria[1] or "MT" in sku: 
                tipo = "MAQUILAS"
            elif "PC" in sku:
                tipo = "PRODUCTO COMERCIAL"
            elif "PT" in sku and rutas > 0:
                tipo = "INTERNO RESURTIBLE"
            elif "PT" in sku and rutas == 0:
                tipo = "INTERNO NO RESURTIBLE"
            else:
                tipo = "OTROS"
                
            if sku not in productsPSQL:
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
                    marca = marca[1] if marca else "",
                    categoria = categoria[1],
                    tipoProducto = tipo,
                    fechaCreacion = product.get('fechaCreacion')
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


#* Llenar la base de datos con los productos existentes en Odoo
def pullProductsOdoo(request):
    try:     
        #Traer los productos que existen de odoo        
        productsOdoo = get_product_all_products()
        #print(productsOdoo)
        response = insertProducts(productsOdoo)

        if response['status'] == "success":
            totalRows = response['message']
            return JsonResponse({
                'status'  : 'success',
                'message' : f'Se han agregado correctamente {totalRows} Productos nuevos'
            })

        return JsonResponse({
            'status'  : 'error',
            'message' : response['message']
        })
    
    except Exception as e:
        return JsonResponse({
            'status'  : 'error',
            'message' : f'Ha ocurrido un error al tratar de insertar los datos: {str(e)}'
        })


#* Función updateProducts. Similar a insertProducts. Este consulta los productos de Odoo y actualiza los campos en la base de PostgreSQL
def updateProducts(request):
    try:
        #? Traemos todos los productos de odoo. 
        productsOdoo = get_product_all_products()

        if productsOdoo['status'] == 'success':
            odoo_dict = {p['sku']: p for p in productsOdoo['products']}
            productsPSQL = list(Productos.objects.all())

            updatedProducts = []

            for product in productsPSQL:
                odooProduct = odoo_dict.get(product.sku)

                if odooProduct:
                    sku = odooProduct.get('sku', '')
                    categoria = odooProduct.get('categoria', '')[1] if isinstance(odooProduct.get('categoria'), (list, tuple)) else ''
                    rutas = len(odooProduct.get('routes'))

                    if "MAQUILAS" in categoria or "MT" in sku: 
                        tipo = "MAQUILAS"
                    elif "PC" in sku:
                        tipo = "PRODUCTO COMERCIAL"
                    elif "PT" in sku and rutas > 0:
                        tipo = "INTERNO RESURTIBLE"
                    elif "PT" in sku and rutas == 0:
                        tipo = "INTERNO NO RESURTIBLE"
                    else:
                        tipo = "OTROS"

                    product.nombre           = odooProduct.get('name', '')
                    product.sku              = sku
                    product.marca            = odooProduct.get('marca', '')[1] if isinstance(odooProduct.get('marca'), (list, tuple)) else ''
                    product.maxActual        = odooProduct.get('maxActual', 0)
                    product.minActual        = odooProduct.get('minActual', 0)
                    product.existenciaActual = odooProduct.get('existenciaActual', 0)
                    product.categoria        = categoria
                    product.tipoProducto     = tipo
                    product.fechaCreacion    = odooProduct.get('fechaCreacion', '')
                    updatedProducts.append(product)

            Productos.objects.bulk_update(updatedProducts, ['nombre', 'sku', 'marca', 'maxActual', 'minActual', 'existenciaActual', 'categoria', 'tipoProducto', 'fechaCreacion'])
            return JsonResponse({
                'status'  : 'success',
                'message' : f'Se han actualizado {len(updatedProducts)} correctamente'
            })

        return JsonResponse({
            'status'  : 'error',
            'message' : f'Error en realizar la consulta a Odoo: '
        })
    except Exception as e:
        return JsonResponse({
            'status'  : 'error',
            'message' : f'Ha ocurrido un error al tratar de insertar los datos: {str(e)}'
        })


#* Función createProductsFromOdoo(). Crea nuevos productos en donde la condicion es que solo trae productos con fecha de creación menor a 1 día
def createProductsFromOdoo(request):
    try:     
        #Traer los productos que existen de odoo        
        productsOdoo = get_newproducts()
        response = insertProducts(productsOdoo)

        if response['status'] == "success":
            totalRows = response['message']
            return JsonResponse({
                'status'  : 'success',
                'message' : f'Se han agregado correctamente {totalRows} Productos nuevos'
            })

        return JsonResponse({
            'status'  : 'error',
            'message' : response['message']
        })
    
    except Exception as e:
        return JsonResponse({
            'status'  : 'error',
            'message' : f'Ha ocurrido un error al tratar de insertar los datos: {str(e)}'
        })