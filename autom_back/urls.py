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
from Unidades.Produccion_Logistica.maxMin.dataMaxMin import updateMinMax
from modelosBd.productos.views import pullProductsOdoo, getProductsPSQL, updateProducts, createProductsFromOdoo
from modelosBd.insumos.views import pullInsumosOdoo, getInsumosPSQL, updateInsumosOdoo, createInsumosFromOdoo
from modelosBd.materialPI.views import getMaterialsPIPSQL, pullMaterialPi
from modelosBd.clientes.views import pullClientesOdoo
from modelosBd.ventas.views import pullVentasOdoo

urlpatterns = [
    path('admin/', admin.site.urls),

    #!Rutas Actualizar Max y Min Insumos
    path('updatemaxmin/', updateMinMax),

    #!Rutas de productos
    path('getProducts/', getProductsPSQL),
    path('pullProductsOdoo/', pullProductsOdoo),
    path('updateProducts/', updateProducts),
    path('createProductsOdoo/', createProductsFromOdoo),

    #!Rutas de Insumos
    path('getInsumos/', getInsumosPSQL),
    path('pullInsumosOdoo/', pullInsumosOdoo),
    path('updateInsumosOdoo/', updateInsumosOdoo),
    path('createInsumosOdoo/', createInsumosFromOdoo),

    #!Rutas para MaterialesPI
    path('getMaterials/', getMaterialsPIPSQL),
    path('pullMaterialPI/', pullMaterialPi),
    
    #!Rutas para Clientes
    path('pullClientes/', pullClientesOdoo),
    
    #!Rutas para Ventas
    path('pullVentas/', pullVentasOdoo)
]
