from django.http import JsonResponse
from modelosBd.ventas.models import Ventas
from modelosBd.ventasPV.views import pullLineaVentaOdoo
from modelosBd.ventas import ctr_ventas

from Unidades.Administracion.Reportes_ventas import reporteVentas

# Create your views here.
def getVentasPSQL(request):
    pass

#? Consultas para conexión con Odoo
def pullVentasOdoo(request):
    
    try:
        #Traer todos los clientes de Odoo
        ventasOdoo=ctr_ventas.get_allSales()
        
        if ventasOdoo['status'] == 'success':
            
            ventasPSQL = Ventas.objects.all().values_list('idVenta', flat=True)
       
            newVentas = 0
            newNota = 0
            
            for venta in ventasOdoo['ventas']:
                try:
                    if venta['name'] not in ventasPSQL:
                        if any(line.get('product_id') is False for line in venta['productsLines']):
                            pass
                        else:
                            if venta['move_type'] == 'out_invoice':
                                newVentas=newVentas+1
                            if venta['move_type'] == 'out_refund':
                                newNota=newNota+1
                                #Asignamos la distribución de la información en sus respectivas variables
                            Ventas.objects.create(
                                idVenta         = venta['name'],
                                fecha           = venta['invoice_date'],
                                ciudadVenta     = venta['city'],
                                estadoVenta     = venta['state_id'],
                                paisVenta       = venta['country_id'],
                                unidad          = venta['branch_id'][1] if venta['branch_id'] else "",
                                vendedor        = venta['invoice_user_id'][1],
                                total           = venta['amount_total_signed'],
                                idCliente_id    = venta['partner_id'][0]
                            )
                                
                            pullventas=pullLineaVentaOdoo(venta['productsLines'], venta['name'], venta['invoice_date'])
                            if pullventas['status'] == "error":
                                return JsonResponse({
                                        'status': 'error',
                                        'message': f"{pullventas['message']}, {venta}"
                                    })
                            
                except Exception as e:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Error registrando ventas: {e}'
                    })
        
            return JsonResponse({
                'status'  : 'success',
                'message' : f'{newVentas} ventas nuevas y {newNota} nuevas notas de credito'
            })    
        
        else:
            return JsonResponse({
                'status'  : 'error',
                'message' : ventasOdoo['message']
            })
        
    except Exception as e:
        return JsonResponse({
            'status'  : 'error',
            'message' : f'Ha ocurrido un error en pull Ventas: {e}'
        })
        
def createVentasOdoo(request):
    try:
        #Traer todos los clientes de Odoo
        ventasOdoo=ctr_ventas.get_newSales()
        
        if ventasOdoo['status'] == 'success':
            
            ventasPSQL = Ventas.objects.all().values_list('idVenta', flat=True)
       
            newVentas = 0
            newNota = 0
            
            for venta in ventasOdoo['ventas']:
                try:
                    if venta['name'] not in ventasPSQL:
                        if any(line.get('product_id') is False for line in venta['productsLines']):
                            pass
                        else:
                            if venta['move_type'] == 'out_invoice':
                                newVentas=newVentas+1
                            if venta['move_type'] == 'out_refund':
                                newNota=newNota+1
                                #Asignamos la distribución de la información en sus respectivas variables
                            Ventas.objects.create(
                                idVenta         = venta['name'],
                                fecha           = venta['invoice_date'],
                                ciudadVenta     = venta['city'],
                                estadoVenta     = venta['state_id'],
                                paisVenta       = venta['country_id'],
                                unidad          = venta['branch_id'][1] if venta['branch_id'] else "",
                                vendedor        = venta['invoice_user_id'][1],
                                total           = venta['amount_total_signed'],
                                idCliente_id    = venta['partner_id'][0]
                            )
                                
                            pullventas=pullLineaVentaOdoo(venta['productsLines'], venta['name'], venta['invoice_date'])
                            if pullventas['status'] == "error":
                                return JsonResponse({
                                        'status': 'error',
                                        'message': f"{pullventas['message']}, {venta}"
                                    })
                            
                except Exception as e:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Error registrando ventas: {e}'
                    })
        
            return JsonResponse({
                'status'  : 'success',
                'message' : f'{newVentas} ventas nuevas y {newNota} nuevas notas de credito'
            })    
        
        else:
            return JsonResponse({
                'status'  : 'error',
                'message' : ventasOdoo['message']
            })
        
    except Exception as e:
        return JsonResponse({
            'status'  : 'error',
            'message' : f'Ha ocurrido un error en pull Ventas: {e}'
        })

def updateVentasOdoo(request):
    pass

def deleteVentasPSQL():
    pass



#? Consulta para crear ventas desde el excel compact
def createSalesExcel(request):
    try:
        #Traer todos los clientes de Odoo
        ventasOdoo=reporteVentas.pullVentasExcel()
        
        if ventasOdoo['status'] == 'success':            
            newVenta=0
            
            ventasPSQL = Ventas.objects.all().values_list('idVenta', flat=True)
            
            for venta in ventasOdoo['ventas']:
                if venta['idVenta'] not in ventasPSQL:
                    newVenta=newVenta+1
                    #Asignamos la distribución de la información en sus respectivas variables
                    Ventas.objects.create(
                        idVenta         = venta['idVenta'],
                        fecha           = venta['fecha'],
                        ciudadVenta     = venta['ciudadVenta'],
                        estadoVenta     = venta['estadoVenta'],
                        paisVenta       = venta['paisVenta'],
                        unidad          = venta['unidad'],
                        vendedor        = venta['vendedor'],
                        total           = venta['total'],
                        idCliente_id    = venta['idCliente']
                    )
                    pullventas=reporteVentas.pullLineaVentaExcel(venta["idVenta"], venta['fecha'])
                    if pullventas['status'] == "error":
                        return JsonResponse({
                                'status': 'error',
                                'message': f"{pullventas['message']}, {venta}"
                            })
                    ventaFinal = Ventas.objects.get(idVenta=venta['idVenta'])
                    ventaFinal.total=pullventas['total']
                    ventaFinal.save()
                    print(newVenta)
                        
            return JsonResponse({
                'status'  : 'success',
                'message' : f'Las ventas nuevas son: {newVenta}'
            })
        else:
            return JsonResponse({
                'status'  : 'error',
                'message' : ventasOdoo['message']
            })
        
    except Exception as e:
        return JsonResponse({
            'status'  : 'error',
            'message' : f'Ha ocurrido un error en createSalesExcel: {e}'
        })