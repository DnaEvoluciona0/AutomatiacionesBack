from django.shortcuts import render
from django.http import JsonResponse
from modelosBd.clientes.models import Clientes
from Conexiones.conectionOdoo import OdooAPI

#? Consultas para conexión con Odoo
def pullClientesOdoo(request):
    conn = OdooAPI()
    
    try:
        #Traer todos los clientes de Odoo
        clientesOdoo=conn.get_allClients()
        
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