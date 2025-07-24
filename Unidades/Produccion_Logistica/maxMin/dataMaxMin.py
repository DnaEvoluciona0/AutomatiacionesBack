from django.http import JsonResponse
from django.db.models import F, ExpressionWrapper, FloatField, Subquery, OuterRef, Sum, Count, Value, Case, When, Q
from django.db.models.functions import Cast, ExtractYear, ExtractMonth
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from modelosBd.insumos.models import Insumos
from modelosBd.materialPI.models import MaterialPI
from modelosBd.ventasPV.models import VentasPVA
from modelosBd.insumos.views import updateMaxMin


#!Actualizar máximos y mínimos de Odoo. 
def updateMinMax(request):

    response = []
    #? Traemos los datos que son necesarios 
    #? Primero hacemos la subconsulta del promedio de ventas de los productos
    fecha_doce_meses = datetime.now() - relativedelta(years=1)
    ventas12meses_subquery = VentasPVA.objects.filter(
        idProducto = OuterRef('producto_id'),
        fecha__year = datetime.now().year - 1
        #fecha__gte = fecha_doce_meses
    ).values('idProducto_id').annotate(
        total_ventas=Sum('cantidad'), 
        meses=Count('fecha__month', distinct=True)
    ).annotate(
        promedio_ventas=ExpressionWrapper(
            Case(
                When(meses__gt=0, then=F('total_ventas') / F('meses')),
                default=Value(0),
                output_field=FloatField()
            ),
            output_field=FloatField()
            
        )
    ).values('promedio_ventas')[:1]


    #? Subconsulta para promedio de ventas de productos que no cuentan con 12 meses de 
    #? ventas pero que pasan de los 3 meses.
    fecha6meses = datetime.now() - relativedelta(months=6)
    fecha3meses = datetime.now() - relativedelta(months=3)

    ventasMenores12meses_subquery = VentasPVA.objects.filter(
        idProducto = OuterRef('producto_id'),
        fecha__gte=fecha6meses
    ).values('idProducto_id').annotate(
        total_ventas=Sum('cantidad'),
        meses=Count('fecha__month', distinct=True)
    ).annotate(
        promedio_ventas=ExpressionWrapper(
            Case(
                When(meses__gt=0, then=F('total_ventas') / F('meses')),
                default=Value(0),
                output_field=FloatField()
            ),
            output_field=FloatField()
        )
    ).values('promedio_ventas')[:1]

    #? Consulta completa de todos los productos cons sus insumos cuando los insumos no son compartidos.
    #? Y que tengan más de 12 meses de existencia
    #Me arroja la cantidad de insumos promedio que se necesitan para crear los productos vendidos.

    #! Consulas para productos con mas de 12 meses de registro
    insumosUnicos12meses = MaterialPI.objects.select_related('producto', 'insumo').filter(
        Q(producto__tipoProducto='INTERNO RESURTIBLE') &
        ~Q(insumo__sku__icontains='00') &
        Q(producto__fechaCreacion__lt=fecha_doce_meses)
    ).annotate(
        promedio_ventas=Subquery(ventas12meses_subquery),
        insumo_promedio=ExpressionWrapper(
            F('promedio_ventas') * F('cantidad'),
            output_field=FloatField()
        )
    ).values(
        producto_id_ref=F('producto__id'),
        nombre_producto=F('producto__nombre'),
        marca=F('producto__marca'),
        insumo_id_ref=F('insumo__id'),
        cantidad_final=F('cantidad'),
        nombre_insumo=F('insumo__nombre'),
        sku=F('insumo__sku'),
        tiempo_entrega=F('insumo__tiempoEntrega'),
        insumo_promedio=F('insumo_promedio')
    ).order_by('producto__nombre')


    #? Insumos compartidos
    insumosCompartidos12meses = MaterialPI.objects.select_related('producto', 'insumo').filter(
        Q(producto__tipoProducto='INTERNO RESURTIBLE') &
        Q(insumo__sku__icontains='00') &
        Q(producto__fechaCreacion__lt=fecha_doce_meses)
    ).annotate(
        promedio_ventas=Subquery(ventas12meses_subquery),
        insumo_promedio=ExpressionWrapper(
            F('promedio_ventas') * F('cantidad'),
            output_field=FloatField()
        )
    ).values(
        producto_id_ref=F('producto__id'),
        nombre_producto=F('producto__nombre'),
        marca=F('producto__marca'),
        insumo_id_ref=F('insumo__id'),
        cantidad_final=F('cantidad'),
        nombre_insumo=F('insumo__nombre'),
        sku=F('insumo__sku'),
        tiempo_entrega=F('insumo__tiempoEntrega'),
        insumo_promedio=F('insumo_promedio')
    ).order_by('producto__nombre')

    #! Consultas para productos con menos de 12 meses de registro
    insumosUnicosMenor12meses = MaterialPI.objects.select_related('producto', 'insumo').filter(
        Q(producto__tipoProducto='INTERNO RESURTIBLE') &
        ~Q(insumo__sku__icontains='00') &
        Q(producto__fechaCreacion__gte=fecha_doce_meses) &
        Q(producto__fechaCreacion__lt=fecha3meses)
    ).annotate(
        promedio_ventas=Subquery(ventasMenores12meses_subquery),
        insumo_promedio=ExpressionWrapper(
            F('promedio_ventas') * F('cantidad'),
            output_field=FloatField()
        )
    ).values(
        producto_id_ref=F('producto__id'),
        nombre_producto=F('producto__nombre'),
        marca=F('producto__marca'),
        insumo_id_ref=F('insumo__id'),
        cantidad_final=F('cantidad'),
        nombre_insumo=F('insumo__nombre'),
        sku=F('insumo__sku'),
        tiempo_entrega=F('insumo__tiempoEntrega'),
        insumo_promedio=F('insumo_promedio')
    ).order_by('producto__nombre')

    #? Insumos compartidos
    insumosCompartidosMenor12meses = MaterialPI.objects.select_related('producto', 'insumo').filter(
        Q(producto__tipoProducto='INTERNO RESURTIBLE') &
        Q(insumo__sku__icontains='00') &
        Q(producto__fechaCreacion__gte=fecha_doce_meses) &
        Q(producto__fechaCreacion__lt=fecha3meses)
    ).annotate(
        promedio_ventas=Subquery(ventasMenores12meses_subquery),
        insumo_promedio=ExpressionWrapper(
            F('promedio_ventas') * F('cantidad'),
            output_field=FloatField()
        )
    ).values(
        producto_id_ref=F('producto__id'),
        nombre_producto=F('producto__nombre'),
        marca=F('producto__marca'),
        insumo_id_ref=F('insumo__id'),
        cantidad_final=F('cantidad'),
        nombre_insumo=F('insumo__nombre'),
        sku=F('insumo__sku'),
        tiempo_entrega=F('insumo__tiempoEntrega'),
        insumo_promedio=F('insumo_promedio')
    ).order_by('producto__nombre')



    #! Sacamos los minimos y máximos de todos los productos
    #? Traemos todos los insumos para poder actualizarlos
    insumosPSQL = list(Insumos.objects.all())
    insumosForUpdated = {i.id: i for i in insumosPSQL}

    insumosNoCompartidosUpdated = []
    insumosCompartidosUpdated   = []
    insumos_dict                = {}


    #!Realizamos el cálculo para los insumos no compartidos
    for insumo in insumosUnicos12meses:
        #Obtenemos el insumo que se va a actualizar
        insumoActual = insumosForUpdated.get(insumo['insumo_id_ref'])

        if insumoActual:
            #Realizamos el cálculo del máximo y del mínimo.
            if insumo['tiempo_entrega'] == 0:
                tiempoEntrega = 10
            elif insumo['insumo_promedio'] == None:
                tiempoEntrega = 10
            else:
                tiempoEntrega = insumo['insumo_promedio'] * (insumo['tiempo_entrega'] / 30)

            if insumo['insumo_promedio'] == None:
                newMinQty = tiempoEntrega
                newMaxQty = newMinQty + tiempoEntrega
            else:
                newMinQty = (insumo['insumo_promedio'] * 1.5) + tiempoEntrega
                newMaxQty = newMinQty + tiempoEntrega + insumo['insumo_promedio']

            #Actualizamos en las bases de datos
            updateMaxMin(insumoActual, newMaxQty, newMinQty)

            #print(response1)
            insumosNoCompartidosUpdated.append(insumo)

        #break  #! Para solo trabajar con uno

    for insumo in insumosUnicosMenor12meses:
        #Obtenemos el insumo que se va a actualizar
        insumoActual = insumosForUpdated.get(insumo['insumo_id_ref'])

        if insumoActual:
            #Realizamos el cálculo del máximo y del mínimo.
            #! Aqui establecer bien cuanto es por tiempo de entrega
            if insumo['tiempo_entrega'] == 0:
                tiempoEntrega = 10
            elif insumo['insumo_promedio'] == None:
                tiempoEntrega = 10
            else:
                tiempoEntrega = insumo['insumo_promedio'] * (insumo['tiempo_entrega'] / 30)

            if insumo['insumo_promedio'] == None:
                newMinQty = tiempoEntrega
                newMaxQty = newMinQty + tiempoEntrega
            else:
                newMinQty = (insumo['insumo_promedio'] * 1.5) + tiempoEntrega
                newMaxQty = newMinQty + tiempoEntrega + insumo['insumo_promedio']

            #Actualizamos en las bases de datos
            updateMaxMin(insumoActual, newMaxQty, newMinQty)

            #print(response1)
            insumosNoCompartidosUpdated.append(insumo)

        #break  #! Para solo trabajar con uno


    for insumo in insumosCompartidos12meses:
        nombre = insumo['nombre_insumo']
        if nombre in insumos_dict:
            if insumos_dict[nombre]['insumo_promedio'] == None:
                insumos_dict[nombre]['insumo_promedio'] = insumo['insumo_promedio']
            else:
                if insumo['insumo_promedio'] != None:
                    insumos_dict[nombre]['insumo_promedio'] += insumo['insumo_promedio']
        else:
            insumos_dict[nombre] = insumo.copy()

    for insumo in insumosCompartidosMenor12meses:
        nombre = insumo['nombre_insumo']
        if nombre in insumos_dict:
            if insumos_dict[nombre]['insumo_promedio'] == None:
                insumos_dict[nombre]['insumo_promedio'] = insumo['insumo_promedio']
            else:
                if insumo['insumo_promedio'] != None:
                    insumos_dict[nombre]['insumo_promedio'] += insumo['insumo_promedio']
        else:
            insumos_dict[nombre] = insumo.copy()
            

    #?Ya tengo la lista con insumos compartidos juntos.
    insumosCompartidosJuntos = list(insumos_dict.values())

    for insumoCompartido in insumosCompartidosJuntos:
        insumoActual = insumosForUpdated.get(insumoCompartido['insumo_id_ref'])
        if insumoActual:
            if insumoCompartido['tiempo_entrega'] == 0:
                tiempoEntrega = 10
            else:
                tiempoEntrega = insumoCompartido['insumo_promedio'] * (insumoCompartido['tiempo_entrega'] / 30)

            if insumoCompartido['insumo_promedio'] == None:
                newMinQty = tiempoEntrega
                newMaxQty = newMinQty + tiempoEntrega
            else:
                newMinQty = (insumoCompartido['insumo_promedio'] * 1.5) + tiempoEntrega
                newMaxQty = newMinQty + tiempoEntrega + insumoCompartido['insumo_promedio']

            #Actualizamos en las bases de datos
            updateMaxMin(insumoActual, newMaxQty, newMinQty)

            #print(response1)
            insumosCompartidosUpdated.append(insumoCompartido)

    return JsonResponse({
        'status'         : 'success', 
        'no_compartidos' : insumosNoCompartidosUpdated,
        'compartidos'    : insumosCompartidosUpdated
    })