from modelosBd.ventasPV.models import VentasPVH, VentasPVA
from modelosBd.productos.models import Productos

# Create your views here.
# Create your views here.
#? Consultas para conexión con Odoo
def pullLineaVentaOdoo(productos, idVenta, fechaVenta):
    try:
        productosPSQL = Productos.objects.all().values_list('id', flat=True)
        
        for producto in productos:
            nombreP = producto['name'] if producto['name'].find("]") == -1 else producto['name'][producto['name'].find("]")+2:]
            skuP = "" if producto['name'].find("]") == -1 else producto['name'][:producto['name'].find("]")+1]
            
            if producto['product_id'][0] in productosPSQL:
                try:
                    VentasPVA.objects.create(
                        fecha      = fechaVenta,
                        cantidad        = producto['quantity'],
                        idProducto_id   = producto['product_id'][0]
                    )
                except:
                    VentasPVA.objects.create(
                        fecha      = fechaVenta,
                        cantidad        = producto['quantity'],
                        idInsumo_id     = producto['product_id'][0]
                    )
                
            VentasPVH.objects.create(
                cantidad        = producto['quantity'],
                precioUnitario  = producto['price_unit'],
                subtotal        = producto['price_subtotal'],
                marca           = producto['x_studio_marca'] if producto['x_studio_marca'] else "",
                idVenta_id      = idVenta,
                nombre          = nombreP,
                sku             = skuP
            )
        return({
            'status'  : 'success',
            'message' : f'Todos los productos han sido registrados'
        })   
        
    except Exception as e:
        return({
            'status'  : 'error',
            'message' : f'Ha ocurrido un error al tratar de insertar los datos en ventasPV: {e}'
        })