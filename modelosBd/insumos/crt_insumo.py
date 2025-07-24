import xmlrpc.client
from datetime import datetime, timedelta

from Conexiones.conectionOdoo import OdooAPI

#? Instania de coneción a Odoo
conOdoo = OdooAPI()

def get_all_insumos():
    if not conOdoo.models:
        return ({
            'status'  : 'error',
            'message' : 'Error en la conexión con Odoo, no hay conexión Activa'
        })

    #funcion try para arrojar los insumos de odoo
    try:
        insumosOdoo = conOdoo.models.execute_kw(
            conOdoo.db, conOdoo.uid, conOdoo.password,
            'product.product', 'search_read', 
            [[
                '&',
                ('categ_id', 'ilike', 'INSUMO'),
                ('categ_id.parent_id', 'not ilike', 'AGENCIA DIGITAL'),
                ('default_code', 'not ilike', 'STUDIO'),
                ('default_code', 'not ilike', 'T-S'),
                ('default_code', 'not ilike', 'T-T'),
            ]],
            {  'fields' : ['id', 'name', 'default_code', 'qty_available', 'product_brand_id', 'categ_id', 'route_ids']  }
        )

        orderpoints = conOdoo.models.execute_kw(
            conOdoo.db, conOdoo.uid, conOdoo.password, 
            'stock.warehouse.orderpoint', 'search_read', 
            [[]],
            {  'fields' : ['product_id', 'product_min_qty', 'product_max_qty']  }
        )

        providers = conOdoo.models.execute_kw(
            conOdoo.db, conOdoo.uid, conOdoo.password,
            'product.supplierinfo', 'search_read', 
            [[]],
            {  'fields' : ['product_tmpl_id', 'partner_id', 'delay'] }
        )

        finalInsumos = []

        for insumo in insumosOdoo:
            insumoId   = insumo['id']
            insumoName = insumo['name']
            points     = [op for op in orderpoints if op['product_id'][0] == insumoId]
            provider   = [pr for pr in providers   if insumoName in pr['product_tmpl_id'][1]]

            minQty = points[0]['product_min_qty'] if points else 0
            maxQty = points[0]['product_max_qty'] if points else 0

            finalInsumos.append({
                'id'               : insumoId,
                'name'             : insumo['name'],
                'sku'              : insumo['default_code'],
                'existenciaActual' : insumo['qty_available'],
                'minActual'        : minQty,
                'maxActual'        : maxQty,
                'marca'            : insumo['product_brand_id'],
                'categoria'        : insumo['categ_id'],
                'routes'           : insumo['route_ids'],
                'proveedor'        : provider
            })

        return ({
            'status'   : 'success',
            'products' : finalInsumos
        })

    except xmlrpc.client.Fault as e:
        return ({
            'status'       : 'error',
            'message'      : f'Error al ejecutar la consulta a Odoo: {str(e)}',
            'fault_code'   : e.faultCode,
            'fault_string' : e.faultString,
        })


#? Obtenemos los nuevos Insumos creados en el día anterior a hoy.
def get_newInsumos():
    #Verificamos que haya alguna conexion con odoo
    if not conOdoo.models:
        return({
            'status'  : 'error',
            'message' : 'Error en la conexión con Odoo, no hay conexión Activa'
        })

    try:
        today     = datetime.now()
        yesterday = today - timedelta(days=1)

        dateStart = yesterday.strftime('%Y-%m-%d 00:00:00')
        dateEnd   = today.strftime('%Y-%m-%d 23:59:59')

        insumoTemplateID = conOdoo.models.execute_kw(
            conOdoo.db, conOdoo.uid, conOdoo.password,
            'product.template', 'search',
            [[
                ('create_date', '>=', dateStart),
                ('create_date', '<=', dateEnd)
            ]],

        )
        
        insumosOdoo = conOdoo.models.execute_kw(
            conOdoo.db, conOdoo.uid, conOdoo.password,
            'product.product', 'search_read', 
            [[
                '&',
                ('categ_id', 'ilike', 'INSUMO'),
                ('product_tmpl_id', 'in', insumoTemplateID),
                ('categ_id.parent_id', 'not ilike', 'AGENCIA DIGITAL'),
                ('default_code', 'not ilike', 'STUDIO'),
                ('default_code', 'not ilike', 'T-S'),
                ('default_code', 'not ilike', 'T-T'),
            ]],
            {  'fields' : ['id', 'name', 'default_code', 'qty_available', 'product_brand_id', 'categ_id', 'route_ids']  }
        )

        orderpoints = conOdoo.models.execute_kw(
            conOdoo.db, conOdoo.uid, conOdoo.password, 
            'stock.warehouse.orderpoint', 'search_read', 
            [[]],
            {  'fields' : ['product_id', 'product_min_qty', 'product_max_qty']  }
        )

        providers = conOdoo.models.execute_kw(
            conOdoo.db, conOdoo.uid, conOdoo.password,
            'product.supplierinfo', 'search_read', 
            [[]],
            {  'fields' : ['product_tmpl_id', 'partner_id', 'delay'] }
        )

        finalInsumos = []

        for insumo in insumosOdoo:
            insumoId   = insumo['id']
            insumoName = insumo['name']
            points     = [op for op in orderpoints if op['product_id'][0] == insumoId]
            provider   = [pr for pr in providers   if insumoName in pr['product_tmpl_id'][1]]

            minQty = points[0]['product_min_qty'] if points else 0
            maxQty = points[0]['product_max_qty'] if points else 0

            finalInsumos.append({
                'id'               : insumoId,
                'name'             : insumo['name'],
                'sku'              : insumo['default_code'],
                'existenciaActual' : insumo['qty_available'],
                'minActual'        : minQty,
                'maxActual'        : maxQty,
                'marca'            : insumo['product_brand_id'],
                'categoria'        : insumo['categ_id'],
                'routes'           : insumo['route_ids'],
                'proveedor'        : provider
            })
        return ({
            'status'   : 'success',
            'products' : finalInsumos
        })
    except xmlrpc.client.Fault as e:
        return ({
            'status'       : 'error',
            'message'      : f'Error al ejecutar la consulta a Odoo: {str(e)}',
            'fault_code'   : e.faultCode,
            'fault_string' : e.faultString,
        })

def updateMaxMinOdoo(idInsumo, max, min):
    try:

        orderPoint = conOdoo.models.execute_kw(
            conOdoo.db, conOdoo.uid, conOdoo.password,
            'stock.warehouse.orderpoint', 'search_read',
            [[  ('product_id', '=', idInsumo)  ]],
            {  'fields' : ['id']  }
        )
        
        if orderPoint:
            idOrderPoint = orderPoint[0]['id']

            conOdoo.models.execute_kw(
                conOdoo.db, conOdoo.uid, conOdoo.password,
                'stock.warehouse.orderpoint', 'write', 
                [[  idOrderPoint  ], 
                {
                    'product_min_qty' : int(round(min)),
                    'product_max_qty' : int(round(max))
                }]
            )

            return({
                'status'  : 'success',
                'message' : 'Se ha modificado correctamente el producto'
            })

        return({
            'status'  : 'error',
            'message' : f'No existe Máximo ni Mínimo de este producto {idInsumo}'
        })
    except xmlrpc.client.Fault as e:
        return ({
            'status'       : 'error',
            'message'      : f'Error al ejecutar la consulta a Odoo: {str(e)}',
            'fault_code'   : e.faultCode,
            'fault_string' : e.faultString,
        })