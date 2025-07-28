from django.http import JsonResponse
from modelosBd.clientes.models import Clientes
from modelosBd.clientes import ctr_cliente

from Unidades.Administracion.Reportes_ventas import reporteVentas

def getClientesPSQL(request):
    return None

#? Consultas atraer todos lo clientes de odoo
def pullClientesOdoo(request):
    try:
        #Traer todos los clientes de Odoo
        clientesOdoo=ctr_cliente.get_allClients()
        
        if clientesOdoo['status'] == 'success':
            
            clientesPSQL = Clientes.objects.all().values_list('idCliente', flat=True)
            
            newClientes = 0
            
            for cliente in clientesOdoo['clientes']:
                
                if cliente['id'] not in clientesPSQL:
                    #Asignamos la distribución de la información en sus respectivas variables
                    Clientes.objects.create(
                        idCliente           = cliente['id'],
                        nombre              = cliente['name'] if cliente['name']!=False else "",
                        ciudad              = cliente['city'] if cliente['city']!=False else "",
                        estado              = cliente['state_id'][1] if cliente['state_id']!=False else "",
                        pais                = cliente['country_id'][1] if cliente['country_id']!=False else "",
                        tipoCliente         = "Cartera" if cliente['sale_order_count']>=2 else "Cliente Nuevo",
                        numTransacciones    = cliente['sale_order_count']
                    )
                    newClientes=newClientes+1
            
            return JsonResponse({
                'status'  : 'success',
                'message' : f'Los clientes son: {newClientes}'
            })
        else:
            return JsonResponse({
                'status'  : 'error',
                'message' : clientesOdoo['message']
            })
        
    except Exception as e:
        return JsonResponse({
            'status'  : 'error',
            'message' : f'Ha ocurrido un error al tratar de insertar los datos: {e}'
        })

#? Consultas para crear a los nuevos cliente de odoo
def createClientesOdoo(request):
    try:
        #Traer todos los clientes de Odoo
        clientesOdoo=ctr_cliente.get_newClients()
        
        if clientesOdoo['status'] == 'success':
            
            clientesPSQL = Clientes.objects.all().values_list('idCliente', flat=True)
            
            newClientes = 0
            
            for cliente in clientesOdoo['clientes']:
                
                if cliente['id'] not in clientesPSQL:
                    #Asignamos la distribución de la información en sus respectivas variables
                    Clientes.objects.create(
                        idCliente           = cliente['id'],
                        nombre              = cliente['name'] if cliente['name']!=False else "",
                        ciudad              = cliente['city'] if cliente['city']!=False else "",
                        estado              = cliente['state_id'][1] if cliente['state_id']!=False else "",
                        pais                = cliente['country_id'][1] if cliente['country_id']!=False else "",
                        tipoCliente         = "Cartera" if cliente['sale_order_count']>=2 else "Cliente Nuevo",
                        numTransacciones    = cliente['sale_order_count']
                    )
                    newClientes=newClientes+1
            
            return JsonResponse({
                'status'  : 'success',
                'message' : f'Los clientes nuevos son: {newClientes}'
            })
        else:
            return JsonResponse({
                'status'  : 'error',
                'message' : clientesOdoo['message']
            })
        
    except Exception as e:
        return JsonResponse({
            'status'  : 'error',
            'message' : f'Ha ocurrido un error al tratar de insertar los datos de los nuevos clientes: {e}'
        })

#? Consultas para actualizar a los clientes de odoo que se acualizaron un dia antes
def updateClientesOdoo(request):
    try:
        #Traer todos los clientes de Odoo
        clientesOdoo=ctr_cliente.update_Clients()
        
        if clientesOdoo['status'] == 'success':
            newClientes = 0
            
            for cliente in clientesOdoo['clientes']:
                try:
                    clienteAct = Clientes.objects.get(idCliente=cliente['id'])
                    
                    clienteAct.nombre              = cliente['name'] if cliente['name']!=False else ""
                    clienteAct.ciudad              = cliente['city'] if cliente['city']!=False else ""
                    clienteAct.estado              = cliente['state_id'][1] if cliente['state_id']!=False else ""
                    clienteAct.pais                = cliente['country_id'][1] if cliente['country_id']!=False else ""
                    clienteAct.tipoCliente         = "Cartera" if cliente['sale_order_count']>=2 else "Cliente Nuevo"
                    clienteAct.numTransacciones    = cliente['sale_order_count']
                    
                    clienteAct.save()
                    newClientes=newClientes+1
                except:
                    pass
            
            return JsonResponse({
                'status'  : 'success',
                'message' : f'Los clientes son: {newClientes}'
            })
        else:
            return JsonResponse({
                'status'  : 'error',
                'message' : clientesOdoo['message']
            })
        
    except Exception as e:
        return JsonResponse({
            'status'  : 'error',
            'message' : f'Ha ocurrido un error al tratar de insertar los datos: {e}'
        })
    
def deleteClientesPSQL(request):
    return None











#? Consulta para crear clientes desde el excel compact
def createClientesExcel(request):
    try:
        clientesPSQL = Clientes.objects.all().values_list('idCliente', flat=True)
        #Traer todos los clientes de Odoo
        clientesOdoo=reporteVentas.pullClientsExcel(clientesPSQL)
        
        if clientesOdoo['status'] == 'success':
            
            newClientes=0
            
            for cliente in clientesOdoo['clientes']:
                #Asignamos la distribución de la información en sus respectivas variables
                Clientes.objects.create(
                    idCliente           = cliente['id'],
                    nombre              = cliente['name'] if cliente['name']!=False else "",
                    ciudad              = cliente['city'] if cliente['city']!=False else "",
                    estado              = cliente['state_id'][1] if cliente['state_id']!=False else "",
                    pais                = cliente['country_id'][1] if cliente['country_id']!=False else "",
                    tipoCliente         = "Cartera" if cliente['sale_order_count']>=2 else "Cliente Nuevo",
                    numTransacciones    = cliente['sale_order_count']
                )
                newClientes=newClientes+1

            
            return JsonResponse({
                'status'  : 'success',
                'message' : f'Los clientes nuevos son: {newClientes}'
            })
        else:
            return JsonResponse({
                'status'  : 'error',
                'message' : clientesOdoo['message']
            })
        
    except Exception as e:
        return JsonResponse({
            'status'  : 'error',
            'message' : f'Ha ocurrido un error al tratar de insertar los datos de los nuevos clientes: {e}'
        })