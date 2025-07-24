import xmlrpc.client
import os
import dotenv


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

            self.uid = common.authenticate(self.db, self.user, self.password, {})
            if self.uid:
                self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            else:
                raise ConnectionRefusedError("Autenticación fallida. Revisa tus credenciales o la configuración del servidor.")

        except Exception as e:
            print(f"Error al conectar con Odoo: {e}")
            raise
            
              
    ### *Traer todos los clientes que hay en Odoo
    def get_allClients(self):
        #!Determinamos que haya algna conexión con Odoo
        if not self.models:
            return ({
                'status'  : 'error',
                'message' : 'Error en la conexión con Odoo, no hay conexión Activa'
            })
        #try para hacer las consultas en Odoo
        #!Agregar el filtro de fechas xd
        try:
            res_partner = self.models.execute_kw(
                self.db, self.uid, self.password, 
                'res.partner', 'search_read', 
                [[['invoice_ids', '!=', False], '|', ['active', '=', True], ['active', '=', False]]],
                { 'fields' : ['name', 'city', 'state_id', 'country_id', 'sale_order_count']}
            )
            
            return ({
                'status'  : 'success',
                'clientes' : res_partner
            })
            
        except xmlrpc.client.Fault as e:
            return ({
                'status'       : 'error',
                'message'      : f'Error al ejecutar la consulta a Odoo: {str(e)}',
                'fault_code'   : e.faultCode,
                'fault_string' : e.faultString,
            })
            
    ### *Traer todos las ventas completadas y notas de credito
    def get_allSales(self):
        #!Determinamos que haya algna conexión con Odoo
        if not self.models:
            return ({
                'status'  : 'error',
                'message' : 'Error en la conexión con Odoo, no hay conexión Activa'
            })
        #try para hacer las consultas en Odoo
        #!Agregar el filtro de fechas
        try:
            
            order_sale = self.models.execute_kw(
                self.db, self.uid, self.password, 
                'account.move', 'search_read', 
                [[['state', '=', 'posted'], '|', ['move_type', '=', 'out_invoice'], ['move_type', '=', 'out_refund'], ['branch_id', 'not ilike', 'STUDIO'], ['branch_id', 'not ilike', 'TORRE'], '|', '|', ['name', 'ilike', 'INV/'], ['name', 'ilike', 'MUEST/'], ['name', 'ilike', 'BONIF/']]],
                { 'fields' : ['name', 'invoice_date', 'partner_id', 'invoice_user_id', 'partner_shipping_id', 'branch_id', 'amount_total_signed', 'move_type'] }
            )
            
            
            for order in order_sale:
                # *Traemos los producto ordenados
                productos = self.models.execute_kw(
                    self.db, self.uid, self.password, 
                    'account.move.line', 'search_read', 
                    [[['move_id', '=', order['id']], ['display_type', '=', 'product']]],
                    { 'fields' :['name', 'product_id', 'quantity', 'price_unit', 'price_subtotal', 'x_studio_marca']}
                )
                order['productsLines']=productos
                
                # *Traemos la dirección de a donde es el envio
                direccion = self.models.execute_kw(
                    self.db, self.uid, self.password, 
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
            
        except xmlrpc.client.Fault as e:
            return ({
                'status'       : 'error',
                'message'      : f'Error al ejecutar la consulta a Odoo: {str(e)}',
                'fault_code'   : e.faultCode,
                'fault_string' : e.faultString,
            })