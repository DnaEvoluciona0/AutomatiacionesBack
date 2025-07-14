from django.shortcuts import render
from django.http import JsonResponse
from modelosBd.ventas.models import Ventas
from modelosBd.ventasPV.views import pullLineaVentaOdoo
from Conexiones.conectionOdoo import OdooAPI

# Create your views here.
#? Consultas para conexión con Odoo
def pullVentasOdoo(request):
    conn = OdooAPI()
    
    try:
        #Traer todos los clientes de Odoo
        clientesOdoo=conn.get_allSales()
        
        if clientesOdoo['status'] == 'success':
            
            ventasPSQL = Ventas.objects.all().values_list('idVenta', flat=True)
       
            newVentas = 0
            newNota = 0
            
            for venta in clientesOdoo['ventas']:
                try:
                    if venta['name'] not in ventasPSQL:
                        if venta['move_type'] != 'out_refund':
                            newVentas=newVentas+1
                            '''if venta['branch_id']!=False:
                                #Asignamos la distribución de la información en sus respectivas variables
                            
                                Ventas.objects.create(
                                    idVenta         = venta['name'],
                                    fecha           = venta['invoice_date'],
                                    ciudadVenta     = venta['city'],
                                    estadoVenta     = venta['state_id'],
                                    paisVenta       = venta['country_id'],
                                    unidad          = venta['branch_id'][1],
                                    vendedor        = venta['invoice_user_id'][1],
                                    total           = venta['amount_total_signed'],
                                    idCliente_id    = venta['partner_id'][0]
                                )
                            else:
                                Ventas.objects.create(
                                    idVenta         = venta['name'],
                                    fecha           = venta['invoice_date'],
                                    ciudadVenta     = venta['city'],
                                    estadoVenta     = venta['state_id'],
                                    paisVenta       = venta['country_id'],
                                    unidad          = "",
                                    vendedor        = venta['invoice_user_id'][1],
                                    total           = venta['amount_total_signed'],
                                    idCliente_id    = venta['partner_id'][0]
                                )'''
                        else:
                            newNota=newNota+1
                            Ventas.objects.create(
                                    idVenta         = venta['name'],
                                    fecha           = venta['invoice_date'],
                                    ciudadVenta     = venta['city'],
                                    estadoVenta     = venta['state_id'],
                                    paisVenta       = venta['country_id'],
                                    unidad          = venta['branch_id'][1],
                                    vendedor        = venta['invoice_user_id'][1],
                                    total           = venta['amount_total_signed'],
                                    idCliente_id    = venta['partner_id'][0]
                                )
                        pullLineaVentaOdoo(venta['productsLines'], venta['name'])
                            
                except Exception as e:
                    return JsonResponse({
                        'estatus': 'Error',
                        'message': e
                    })
        
            return JsonResponse({
                'status'  : 'success',
                'message' : f'{newVentas} ventas nuevas y {newNota} nuevas notas de credito'
            })    
        
        else:
            return JsonResponse({
                'status'  : 'error',
                'message' : clientesOdoo['message']
            })
        
    except Exception as e:
        return JsonResponse({
            'status'  : 'error',
            'message' : f'Ha ocurrido un error al tratar de insertar los datos en ventas: {e}'
        })