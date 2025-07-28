import xmlrpc.client
import os
import dotenv
import pandas as pd

from django.http import JsonResponse

class OdooAPI:
    #clase para manejar la conexión con Odoo
    def __init__(self):
        dotenv.load_dotenv()
        self.url      = os.getenv("URL_ODOO")
        self.db       = os.getenv("DATABASE_ODOO")
        self.user     = os.getenv("USERNAME_ODOO")
        self.password = os.getenv("PASSWORD_ODOO")
        
        # Valida que todas las variables de entorno estén presentes
        if not all([self.url, self.db, self.user, self.password]):
            raise ValueError("Una o más variables de entorno de Odoo no están definidas.")
            
        self.uid = None
        self.models = None
        self._connect()

    #Funcion connect. 
    def _connect(self):
        try:
            # Conexión para autenticación
            common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')

            # Autenticación
            self.uid = common.authenticate(self.db, self.user, self.password, {})
            if self.uid:
                # Proxy para llamar a los métodos de los modelos
                self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            else:
                raise ConnectionRefusedError("Autenticación fallida. Revisa tus credenciales o la configuración del servidor.")

        except Exception as e:
            print(f"Error al conectar con Odoo: {e}")
            raise

    ### *Traer productos a partir de la catedoría o todos
    def get_product_by_category(self, category):
        #!Determinamos si existe conexión con odoo
        if not self.models:
            return ({
                'status'  : 'error',
                'message' : 'Error en la conexión con Odoo, no hay conexión Activa'
            })

        if category == "INSUMO":
            validacion1 = ('categ_id', 'ilike', 'INSUMO')
        else: 
            validacion1 = ('categ_id', 'not ilike', 'INSUMO')
        #Función try para traer productos a partir de la categoria dada
        try: 
            productsOdoo = self.models.execute_kw(
                self.db, self.uid, self.password,
                'product.product', 'search_read',
                [[  '&',
                    validacion1,
                    #('purchase_ok', '=', 'TRUE'),
                    #('default_code', '=', 'IZLM03ET'),
                    ('categ_id.parent_id', 'not ilike', 'AGENCIA DIGITAL'),
                    ('default_code', 'not ilike', 'STUDIO'),
                    ('default_code', 'not ilike', 'T-S'),
                    ('default_code', 'not ilike', 'T-T'),

                ]],
                {  'fields' : ['id', 'name', 'default_code', 'qty_available', 'product_brand_id', 'categ_id', 'route_ids'] }
            )

            orderpoints = self.models.execute_kw(
                self.db, self.uid, self.password,
                'stock.warehouse.orderpoint', 'search_read',
                [[]],
                {  'fields' : ['product_id', 'product_min_qty', 'product_max_qty']  }
            )

            providers = self.models.execute_kw(
                self.db, self.uid, self.password,
                'product.supplierinfo', 'search_read',
                [[]],
                {  'fields' : ['product_tmpl_id', 'partner_id']  }
            )

            finalProducts = []

            #print(providers)
            
            for product in productsOdoo:
                productId = product['id']
                productName = product['name'] 
                points    = [op for op in orderpoints if op['product_id'][0] == productId]
                provider  = [pr for pr in providers   if productName in pr['product_tmpl_id'][1]] 

                minQty = points[0]['product_min_qty'] if points else 0
                maxQty = points[0]['product_max_qty'] if points else 0

                
                finalProducts.append({
                    'id'               : productId,
                    'name'             : product['name'],
                    'sku'              : product['default_code'],
                    'existenciaActual' : product['qty_available'],
                    'minActual'        : minQty, 
                    'maxActual'        : maxQty,
                    'marca'            : product['product_brand_id'],
                    'categoria'        : product['categ_id'],
                    'routes'           : product['route_ids'],
                    'proveedor'        : provider
                }) 
            return ({
                'status'   : 'success',
                'products' : finalProducts
            })

        except xmlrpc.client.Fault as e:
            return ({
                'status'       : 'error',
                'message'      : f'Error al ejecutar la consulta a Odoo: {str(e)}',
                'fault_code'   : e.faultCode,
                'fault_string' : e.faultString,
            })

    ### *Traer todos los insumos de los productos y las cantidades de cada uno de estos.
    def getInsumoByProduct(self):
        #!Determinamos que haya algna conexión con Odoo
        if not self.models:
            return ({
                'status'  : 'error',
                'message' : 'Error en la conexión con Odoo, no hay conexión Activa'
            })

        #try para hacer las consultas en Odoo Trae todos las combinaciones entre productos
        try:
            finalMaterials = []
            mrp_bom_line = self.models.execute_kw(
                self.db, self.uid, self.password,
                'mrp.bom.line', 'search_read',
                [[]],
                {  'fields' : ['product_id', 'product_qty', 'bom_id']  }
            )

            for item in mrp_bom_line:
                finalMaterials.append({
                    'product'  : item['bom_id'],
                    'material' : item['product_id'],
                    'qty'      : item['product_qty'],
                }) 

            return ({
                'status'  : 'success',
                'message' : finalMaterials
            })

        except xmlrpc.client.Fault as e:
            return ({
                'status'       : 'error',
                'message'      : f'Error al ejecutar la consulta a Odoo: {str(e)}',
                'fault_code'   : e.faultCode,
                'fault_string' : e.faultString,
            })
            
