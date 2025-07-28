from Conexiones.conectionOdoo import OdooAPI
from datetime import datetime, timedelta

conn=OdooAPI()


### *Traer todos las ventas completadas y notas de credito
def get_allSales():
    #!Determinamos que haya algna conexión con Odoo
    if not conn.models:
        return ({
            'status'  : 'error',
            'message' : 'Error en la conexión con Odoo, no hay conexión Activa'
        })
    #try para hacer las consultas en Odoo
        
    order_sale = conn.models.execute_kw(
        conn.db, conn.uid, conn.password, 
        'account.move', 'search_read', 
        [[['state', '=', 'posted'], '|', ['move_type', '=', 'out_invoice'], ['move_type', '=', 'out_refund'], ['branch_id', 'not ilike', 'STUDIO'], ['branch_id', 'not ilike', 'TORRE'], '|', '|', ['name', 'ilike', 'INV/'], ['name', 'ilike', 'MUEST/'], ['name', 'ilike', 'BONIF/']]],
        { 'fields' : ['name', 'invoice_date', 'partner_id', 'invoice_user_id', 'partner_shipping_id', 'branch_id', 'amount_total_signed', 'move_type']}
    )
    
    for order in order_sale:
        # *Traemos los producto ordenados
        productos = conn.models.execute_kw(
            conn.db, conn.uid, conn.password, 
            'account.move.line', 'search_read', 
            [[['move_id', '=', order['id']], ['display_type', '=', 'product']]],
            { 'fields' :['name', 'product_id', 'quantity', 'price_unit', 'price_subtotal', 'x_studio_marca', 'x_studio_related_field_e1jP7']}
        )
        order['productsLines']=productos
        
        # *Traemos la dirección de a donde es el envio
        direccion = conn.models.execute_kw(
            conn.db, conn.uid, conn.password, 
            'res.partner', 'search_read', 
            [[['id', '=', order['partner_shipping_id'][0]]]],
            { 'fields' : ['city', 'state_id', 'country_id',]}
        )
        if direccion != []:
            order['country_id']= direccion[0]['country_id'][1] if direccion[0]['country_id'] != False else ""
            order['state_id']=direccion[0]['state_id'][1] if direccion[0]['state_id'] != False else ""
            order['city']=direccion[0]['city'] if direccion[0]['city'] != False else ""
        else:
            order['country_id']=""
            order['state_id']=""
            order['city']=""
    
    return ({
        'status'  : 'success',
        'ventas' : order_sale
    })
    
def get_newSales():
    lastDay = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    order_sale = conn.models.execute_kw(
        conn.db, conn.uid, conn.password, 
        'account.move', 'search_read', 
        [[['create_date', '>=', lastDay], ['state', '=', 'posted'], '|', ['move_type', '=', 'out_invoice'], ['move_type', '=', 'out_refund'], ['branch_id', 'not ilike', 'STUDIO'], ['branch_id', 'not ilike', 'TORRE'], '|', '|', ['name', 'ilike', 'INV/'], ['name', 'ilike', 'MUEST/'], ['name', 'ilike', 'BONIF/']]],
        { 'fields' : ['name', 'invoice_date', 'partner_id', 'invoice_user_id', 'partner_shipping_id', 'branch_id', 'amount_total_signed', 'move_type']}
    )
    
    for order in order_sale:
        # *Traemos los producto ordenados
        productos = conn.models.execute_kw(
            conn.db, conn.uid, conn.password, 
            'account.move.line', 'search_read', 
            [[['move_id', '=', order['id']], ['display_type', '=', 'product']]],
            { 'fields' :['name', 'product_id', 'quantity', 'price_unit', 'price_subtotal', 'x_studio_marca', 'x_studio_related_field_e1jP7']}
        )
        order['productsLines']=productos
        
        # *Traemos la dirección de a donde es el envio
        direccion = conn.models.execute_kw(
            conn.db, conn.uid, conn.password, 
            'res.partner', 'search_read', 
            [[['id', '=', order['partner_shipping_id'][0]]]],
            { 'fields' : ['city', 'state_id', 'country_id']}
        )
        if direccion != []:
            order['country_id']= direccion[0]['country_id'][1] if direccion[0]['country_id'] != False else ""
            order['state_id']=direccion[0]['state_id'][1] if direccion[0]['state_id'] != False else ""
            order['city']=direccion[0]['city'] if direccion[0]['city'] != False else ""
        else:
            order['country_id']=""
            order['state_id']=""
            order['city']=""
    
    return ({
        'status'  : 'success',
        'ventas' : order_sale
    })