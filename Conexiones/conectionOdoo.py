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
