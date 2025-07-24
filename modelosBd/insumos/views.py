from django.shortcuts import render
from django.http import JsonResponse

from modelosBd.insumos.models import Insumos
from modelosBd.insumos.crt_insumo import get_all_insumos, updateMaxMinOdoo, get_newInsumos


# Create your views here.
#? Consultas a Base de datos PostgreSql
#* Controlador para obtener todos los insumos de la base de datos
def getInsumosPSQL(request):
    insumosPSQL = Insumos.objects.all().values(  'id', 'nombre', 'sku', 'marca', 'existenciaActual', 'maxActual', 'minActual'  )
    return JsonResponse(list(insumosPSQL), safe=False)


#? Consultas para conexión con Odoo
def pullInsumosOdoo(request):

    try:
        #Traemos los insumos de Odoo
        insumosOdoo = get_all_insumos()

        if insumosOdoo['status'] == 'success':
            #Traemos los insumos dentro de postgreSQL
            insumosPSQL = Insumos.objects.all().values_list('sku', flat=True)

            #Añadimos las insumos a la base de datos PosgreSQL
            new_insumos = []

            for insumo in insumosOdoo['products']:
                if insumo['sku']:
                    sku = insumo.get('sku', '').strip()
                    marca = insumo.get('marca')
                    categoria = insumo.get('categoria')
                    #print(insumo)
                    if sku and sku not in insumosPSQL:
                        new_insumos.append({
                            'id' : insumo.get('id')
                        })

                        provider = len(insumo.get('proveedor'))
                        
                        if provider > 0:
                            proveedor = insumo.get('proveedor')
                            proveedorFinal = proveedor[0]['partner_id'][1]
                        else:
                            proveedorFinal = ""
                        

                        createInsumo = Insumos.objects.create(
                            id = insumo.get('id'),
                            sku = sku,
                            nombre = insumo.get('name'),
                            maxActual = insumo.get('maxActual'),
                            minActual = insumo.get('minActual'),
                            existenciaActual = insumo.get('existenciaActual'),
                            marca = marca[1],
                            categoria = categoria[1],
                            proveedor = proveedorFinal,
                        ) 
            
            return JsonResponse({
                'status'  : 'success',
                'message' : f'Se han creado {len(new_insumos)} nuevos Insumos'
            })

        else: 
            return JsonResponse({
                'status'  : 'error',
                'message' : insumosOdoo['message']
            })

    except Exception as e:
        return JsonResponse({
            'status'  : 'error',
            'message' : f'Ha ocurrido un error al tratar de insertar los datos {str(e)}'
        })


def updateInsumosOdoo(request):

    try:
        #? Traemos los insumos de odoo
        insumosOdoo = get_all_insumos()
        
        odoo_dict = {i['sku']: i for i in insumosOdoo['products']}

        #?Traemos los productos de PostgreSQL
        insumosPSQL = list(Insumos.objects.all())
        
        insumosActualizados = []
        for insumo in insumosPSQL:
            odooInsumo = odoo_dict.get(insumo.sku)
            if odooInsumo:
                insumo.nombre           = odooInsumo.get('name', '')
                insumo.sku              = odooInsumo.get('sku', '')
                insumo.marca            = odooInsumo.get('marca', '')[1] if isinstance(odooInsumo.get('marca'), (list, tuple)) else ''
                insumo.maxActual        = odooInsumo.get('maxActual', 0)
                insumo.minActual        = odooInsumo.get('minActual', 0)
                insumo.existenciaActual = odooInsumo.get('existenciaActual', 0)
                insumo.categoria        = odooInsumo.get('categoria', '')[1] if isinstance(odooInsumo.get('categoria'), (list, tuple)) else ''
                insumo.proveedor        = odooInsumo.get('proveedor')[0]['partner_id'][1] if len(odooInsumo.get('proveedor')) > 0 else ''
                insumo.tiempoEntrega    = odooInsumo.get('proveedor')[0]['delay'] if len(odooInsumo.get('proveedor')) > 0 else 0
                insumosActualizados.append(insumo)

        Insumos.objects.bulk_update(insumosActualizados, ['nombre', 'sku', 'marca', 'maxActual', 'minActual', 'existenciaActual', 'categoria', 'proveedor', 'tiempoEntrega'])
        return JsonResponse({
            'status'  : 'success',
            'message' : f'Se han actualizado {len(insumosActualizados)} correctamente'
        })
    except Exception as e:
        return JsonResponse({
            'status'  : 'error',
            'message' : f'Ha ocurrido un error al tratar de insertar los datos {str(e)}'
        })
        
def createInsumosFromOdoo(request):
    try:
        #traemos los productos nuevos de odoo
        insumosOdoo = get_newInsumos()
        if insumosOdoo['status'] == 'success':
            #Traemos los insumos dentro de postgreSQL
            insumosPSQL = Insumos.objects.all().values_list('sku', flat=True)

            #Añadimos las insumos a la base de datos PosgreSQL
            new_insumos = []

            for insumo in insumosOdoo['products']:
                if insumo['sku']:
                    sku = insumo.get('sku', '').strip()
                    marca = insumo.get('marca')
                    categoria = insumo.get('categoria')
                    
                    #print(insumo)
                    if sku and sku not in insumosPSQL:
                        new_insumos.append({
                            'id' : insumo.get('id')
                        })

                        provider = len(insumo.get('proveedor'))
                        
                        if provider > 0:
                            proveedor = insumo.get('proveedor')
                            proveedorFinal = proveedor[0]['partner_id'][1]
                        else:
                            proveedorFinal = ""
                        
                        
                        createInsumo = Insumos.objects.create(
                            id = insumo.get('id'),
                            sku = sku,
                            nombre = insumo.get('name'),
                            maxActual = insumo.get('maxActual'),
                            minActual = insumo.get('minActual'),
                            existenciaActual = insumo.get('existenciaActual'),
                            marca = marca[1] ,
                            categoria = categoria[1],
                            proveedor = proveedorFinal,
                        ) 
            
            return JsonResponse({
                'status'  : 'success',
                'message' : f'Se han creado {len(new_insumos)} nuevos Insumos'
            })
        return JsonResponse({
            'status'  : 'error',
            'message' : insumosOdoo['message']
        })
    except Exception as e:
        return JsonResponse({
            'status'  : 'error',
            'message' : f'Ha ocurrido un error al tratar de insertar los datos: {str(e)}'
        })

def updateMaxMin(insumo, max, min):
    try:

        response = updateMaxMinOdoo(insumo.id, max, min)
        if response['status'] == 'success':

            insumo.maxActual = int(round(max))
            insumo.minActual = int(round(min))

            insumo.save(update_fields=['maxActual', 'minActual'])
        
            return ({
                'status'  : 'success',
                'message' : f'Se ah actualizado correctamente el insumo {insumo.nombre}'
            })

        return ({
            'status'  : 'error',
            'message' : response['message']
        })

    except Exception as e:
        return ({
            'status'  : 'error',
            'message' : f'Ha ocurrido un error al tratar de insertar los datos {str(e)}'
        })