from django.shortcuts import render
from django.http import JsonResponse
from modelosBd.insumos.models import Insumos
from Conexiones.conectionOdoo import OdooAPI


# Create your views here.
#? Consultas a Base de datos PostgreSql
#* Controlador para obtener todos los insumos de la base de datos
def getInsumosPSQL(request):
    insumosPSQL = Insumos.objects.all().values(  'id', 'nombre', 'sku', 'marca', 'existenciaActual', 'maxActual', 'minActual'  )
    return JsonResponse(list(insumosPSQL), safe=False)


#? Consultas para conexión con Odoo
def pullInsumosOdoo(request):
    conOdoo = OdooAPI()

    try:
        #Traemos los insumos de Odoo
        insumosOdoo = conOdoo.get_product_by_category(category="INSUMO")

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
                    if "MAQUILA" in categoria[1]: 
                        tipo = "MAQUILAS"
                    else:
                        tipo = "INTERNO"
                    
                    if sku and sku not in insumosPSQL:
                        new_insumos.append({
                            'id' : insumo.get('id')
                        })

                        createInsumo = Insumos.objects.create(
                            id = insumo.get('id'),
                            sku = sku,
                            nombre = insumo.get('name'),
                            maxActual = insumo.get('maxActual'),
                            minActual = insumo.get('minActual'),
                            existenciaActual = insumo.get('existenciaActual'),
                            marca = marca[1],
                            categoria = categoria[1],
                            tipoInsumo = tipo
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
            'message' : 'Ha ocurrido un error al tratar de insertar los datos'
        })