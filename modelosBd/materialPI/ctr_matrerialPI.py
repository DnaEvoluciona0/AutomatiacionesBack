import xmlrpc.client
from Conexiones.conectionOdoo import OdooAPI


conOdoo = OdooAPI()
def getInsumoByProduct():
    if not conOdoo.models:
        return ({
            'status'  : 'error',
            'message' : 'Error en la conexión con Odoo, no hay conexión Activa'
        })

    try:
        finalMaterial = []

        mrp_bom_line = conOdoo.models.execute_kw(
            conOdoo.db, conOdoo.uid, conOdoo.password,
            'mrp.bom.line', 'search_read',
            [[]],
            {  'fields' : ['product_id', 'product_qty', 'bom_id'] }
        )

        for item in mrp_bom_line:
            finalMaterial.append({
                'product' : item['bom_id'],
                'material' : item['product_id'],
                'qty' : item['product_qty'],
            })

        return ({
            'status'  : 'success',
            'message' : finalMaterial
        })

    except xmlrpc.client.Fault as e:
        return ({
            'status'       : 'error',
            'message'      : f'Error al ejecutar la consulta a Odoo: {str(e)}',
            'fault_code'   : e.faultCode,
            'fault_string' : e.faultString,
        })