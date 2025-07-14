"""
URL configuration for autom_back project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

#rutas agregadas
from Unidades.Produccion_Logistica.maxMin.dataMaxMin import hello, get_sales_by_product
from modelosBd.productos.views import pullProductsOdoo, getProductsPSQL
from modelosBd.insumos.views import pullInsumosOdoo, getInsumosPSQL
from modelosBd.materialPI.views import getMaterialsPIPSQL, pullMaterialPi
from modelosBd.clientes.views import pullClientesOdoo
from modelosBd.ventas.views import pullVentasOdoo

urlpatterns = [
    path('admin/', admin.site.urls),

    #!Ruta de prueba
    path('hello/', hello),

    #!Rutas Sales by Product
    path('getSalesByProduct/', get_sales_by_product),

    #!Rutas de productos
    path('getProducts/', getProductsPSQL),
    path('pullProductsOdoo/', pullProductsOdoo),

    #!Rutas de Insumos
    path('getInsumos/', getInsumosPSQL),
    path('pullInsumosOdoo/', pullInsumosOdoo),

    #!Rutas para MaterialesPI
    path('getMaterials/', getMaterialsPIPSQL),
    path('pullMaterialPI/', pullMaterialPi),
    
    #!Rutas para Clientes
    path('pullClientes/', pullClientesOdoo),
    
    #!Rutas para Ventas
    path('pullVentas/', pullVentasOdoo)
]
