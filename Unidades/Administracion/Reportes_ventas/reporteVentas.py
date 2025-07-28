from Conexiones.conectionOdoo import OdooAPI
import pandas as pd

from modelosBd.ventasPV.models import VentasPVH, VentasPVA
from modelosBd.productos.models import Productos

conn=OdooAPI()
archivo = 'C:/Users/DSWB-PC02/Downloads/ContpaqBD.xlsx'

dfVenta = pd.read_excel(archivo, sheet_name='pvh')

def pullClientsExcel(idsclientes):
    df = pd.read_excel(archivo, sheet_name='Clientes')
    clientes=[]
    
    for index, cliente in df.iterrows():
        
        if cliente["idCliente"] not in idsclientes:
            res_partner = conn.models.execute_kw(
                conn.db, conn.uid, conn.password, 
                'res.partner', 'search_read', 
                [[['id', '=', cliente["idCliente"]], '|', ['active', '=', True], ['active', '=', False]]],
                { 'fields' : ['name', 'city', 'state_id', 'country_id', 'sale_order_count']}
            )
            if res_partner != []:
                clientes.append(res_partner[0])
            if res_partner == []:
                clientes.append({
                    'id': cliente["idCliente"],
                    'name': cliente["Cliente"],
                    'city': False,
                    'state_id': False,
                    'country_id': False,
                    'sale_order_count': 0,
                })
    
    return ({
        'status'  : 'success',
        'clientes' : clientes
    })

def pullVentasExcel():
    df = pd.read_excel(archivo, sheet_name='Ventas')
    Ventas=[]
    
    for index, venta in df.iterrows():
        print(index)
        direccion = conn.models.execute_kw(
            conn.db, conn.uid, conn.password, 
            'res.partner', 'search_read', 
            [[['id', '=', venta["idcliente"]], '|', ['active', '=', True], ['active', '=', False]]],
            { 'fields' : ['city', 'state_id', 'country_id']}
        )
        
        if direccion != []:
            Ventas.append(
                {
                'idVenta': venta["idVenta"],
                'fecha': venta["Fecha"],
                'paisVenta': direccion[0]['country_id'][1] if direccion[0]['country_id'] != False else "",
                'estadoVenta': direccion[0]['state_id'][1] if direccion[0]['state_id'] != False else "",
                'ciudadVenta': direccion[0]['city'] if direccion[0]['city'] != False else "",
                'unidad': venta["unidad"],
                'vendedor': venta["vendedor"],
                'total': 0,
                'idCliente': venta["idcliente"]
            }
            )
            
        if direccion == []:
            Ventas.append({
                'idVenta': venta["idVenta"],
                'fecha': venta["Fecha"],
                'paisVenta': False,
                'estadoVenta': False,
                'ciudadVenta': False,
                'unidad': venta["unidad"],
                'vendedor': venta["vendedor"],
                'total': 0,
                'idCliente': venta["idcliente"]
            })
            
    return ({
        'status'  : 'success',
        'ventas' : Ventas
    })
        

def pullLineaVentaExcel(idVenta, fecha):
    try:
        productosList=dfVenta[dfVenta['idVenta']==idVenta]
        
        
        productsPSQL = Productos.objects.all().values_list('sku', flat=True)
        
        total=0
        
        for index, venta in productosList.iterrows():
            if venta["idVenta"] == idVenta:
                
                total=total+(venta['Cantidad facturada']*venta['Precio unitario'])
                productsOdoo = conn.models.execute_kw(
                    conn.db, conn.uid, conn.password, 
                    'product.product', 'search_read',
                    [[['default_code', '=', venta['SKU']], '|', ['active', '=', True], ['active', '=', False]]],
                    { 'fields' : ['name', 'categ_id']}
                )
                
                if venta['SKU'] in productsPSQL and productsOdoo != []:
                    try:
                        VentasPVA.objects.create(
                            fecha           = fecha,
                            cantidad        = venta['Cantidad facturada'],
                            idProducto_id   = productsOdoo[0]['id']
                        )
                    except:
                        try:
                            VentasPVA.objects.create(
                                fecha           = fecha,
                                cantidad        = venta['Cantidad facturada'],
                                idInsumo_id     = productsOdoo[0]['id']
                            )
                        except:
                            pass
                
                VentasPVH.objects.create(
                        cantidad        = venta['Cantidad facturada'],
                        precioUnitario  = venta['Precio unitario'],
                        subtotal        = venta['Total'],
                        marca           = venta['Marca'] if venta['Marca'] else "",
                        categoria       = productsOdoo[0]['categ_id'][1] if productsOdoo != [] else "PRODUCTO DESCONTINUADO/"+venta['categoria'],
                        idVenta_id      = idVenta,
                        nombre          = productsOdoo[0]['name'] if productsOdoo != [] else venta['nombreProducto'],
                        sku             = venta['SKU']
                )
                
        return({
            'status'  : 'success',
            'total' : total
        })   
        
    except Exception as e:
        return({
            'status'  : 'error',
            'message' : f'Ha ocurrido un error al tratar de insertar los datos en ventasPV excel: {e}'
        })