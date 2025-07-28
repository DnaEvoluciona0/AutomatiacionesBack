from Conexiones.conectionOdoo import OdooAPI
from datetime import datetime, timedelta

conn=OdooAPI()

### *Traer todos los clientes que hay en Odoo
def get_allClients():
    res_partner = conn.models.execute_kw(
        conn.db, conn.uid, conn.password, 
        'res.partner', 'search_read', 
        [[['invoice_ids', '!=', False], '|', ['active', '=', True], ['active', '=', False]]],
        { 'fields' : ['name', 'city', 'state_id', 'country_id', 'sale_order_count']}
    )
    
    return ({
        'status'  : 'success',
        'clientes' : res_partner
    })
    
def get_newClients():
    lastDay = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    res_partner = conn.models.execute_kw(
        conn.db, conn.uid, conn.password, 
        'res.partner', 'search_read', 
        [[['create_date', '>=', lastDay], '|', ['active', '=', True], ['active', '=', False]]],
        { 'fields' : ['name', 'city', 'state_id', 'country_id', 'sale_order_count']}
    )
    
    return ({
        'status'  : 'success',
        'clientes' : res_partner
    })

def update_Clients():
    lastDay = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    res_partner = conn.models.execute_kw(
        conn.db, conn.uid, conn.password, 
        'res.partner', 'search_read', 
        [[['write_date', '>=', lastDay], ['invoice_ids', '!=', False], '|', ['active', '=', True], ['active', '=', False]]],
        { 'fields' : ['name', 'city', 'state_id', 'country_id', 'sale_order_count']}
    )
    
    return ({
        'status'  : 'success',
        'clientes' : res_partner
    })