import xmlrpc.client
import os
import dotenv

class OdooAPI:
    """
    Una clase para manejar la conexión y las operaciones con la API de Odoo.
    """
    def __init__(self):
        dotenv.load_dotenv()
        self.url = os.getenv("URL_ODOO")
        self.db = os.getenv("DATABASE_ODOO")
        self.user = os.getenv("USERNAME_ODOO")
        self.password = os.getenv("PASSWORD_ODOO")
        
        # Valida que todas las variables de entorno estén presentes
        if not all([self.url, self.db, self.user, self.password]):
            raise ValueError("Una o más variables de entorno de Odoo no están definidas.")
            
        self.uid = None
        self.models = None
        self._connect()

    def _connect(self):
        """
        Establece la conexión y se autentica con Odoo.
        """
        try:
            # Conexión para autenticación
            common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            # print("Versión del servidor Odoo:", common.version())

            # Autenticación
            self.uid = common.authenticate(self.db, self.user, self.password, {})
            if self.uid:
                print(f"Conexión exitosa. UID: {self.uid}")
                # Proxy para llamar a los métodos de los modelos
                self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            else:
                raise ConnectionRefusedError("Autenticación fallida. Revisa tus credenciales o la configuración del servidor.")

        except Exception as e:
            print(f"Error al conectar con Odoo: {e}")
            raise

    """ def search_read_products(self, domain=[], fields=['id', 'name', 'default_code'], limit=5):
    
        Ejemplo de un método para buscar y leer productos.
        
        if not self.models:
            print("No hay conexión activa.")
            return []
            
        try:
            products = self.models.execute_kw(
                self.db, self.uid, self.password,
                'product.product', 'search_read',
                [domain],
                {'fields': fields, 'limit': limit}
            )
            return products
        except xmlrpc.client.Fault as e:
            print(f"Error al ejecutar la llamada a Odoo: {e}")
            return None """

# --- CÓMO USAR LA CLASE ---
if __name__ == "__main__":
    try:
        # 1. En cualquier parte de tu proyecto, solo necesitas crear una instancia.
        print("Iniciando conexión...")
        odoo_conn = OdooAPI()

        # 2. Ahora puedes usar el objeto para interactuar con Odoo.
        #    La conexión ya está lista.
        if odoo_conn.uid:
            print("\nBuscando los 5 primeros productos...")
            # Ejemplo: buscar productos que sean de tipo 'almacenable'
            """ filtro_productos = [('type', '=', 'product')]
            lista_productos = odoo_conn.search_read_products(domain=filtro_productos, limit=5)
            
            if lista_productos is not None:
                print("Productos encontrados:")
                for product in lista_productos:
                    print(f"- ID: {product['id']}, Código: {product.get('default_code', 'N/A')}, Nombre: {product['name']}") """

    except (ValueError, ConnectionRefusedError, ConnectionError) as e:
        print(f"No se pudo completar la operación. Error: {e}")