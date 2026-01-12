from django.contrib import admin
from .models import (
    Location, Material, Product, ProductBOM, MaterialStock,
    ProductStock, MaterialPurchase, Production, ProductionMaterial,
    WBShipment, ShipmentLogistics  # ← новые
)

admin.site.register(Location)
admin.site.register(Material)
admin.site.register(Product)
admin.site.register(ProductBOM)
admin.site.register(MaterialStock)
admin.site.register(ProductStock)
admin.site.register(MaterialPurchase)
admin.site.register(Production)
admin.site.register(ProductionMaterial)
admin.site.register(WBShipment)
admin.site.register(ShipmentLogistics)
