from django.db import models
from django.core.validators import MinValueValidator
from django.shortcuts import render

# Места хранения
class Location(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=[('home', 'Дом'), ('wb', 'WB склад')])

    def __str__(self):
        return self.name

# Материалы
class Material(models.Model):
    name = models.CharField(max_length=100)  # Тряпка 30x40, Зип 25x35
    unit = models.CharField(max_length=20)  # шт, рулон
    type = models.CharField(max_length=20, choices=[('raw', 'Сырьё'), ('pack', 'Упаковка'), ('other', 'Прочее')])

    def __str__(self):
        return self.name

# Готовая продукция
class Product(models.Model):
    name = models.CharField(max_length=100)  # Комплект 5 тряпок 30x40
    wb_article = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name

# Рецептура (что нужно на 1 упаковку)
class ProductBOM(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    qty_per_unit = models.FloatField(validators=[MinValueValidator(0.0001)])

    class Meta:
        unique_together = ('product', 'material')

# Остатки материалов
class MaterialStock(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    quantity = models.FloatField(default=0)

    class Meta:
        unique_together = ('material', 'location')

# Остатки готовой продукции
class ProductStock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    quantity = models.FloatField(default=0)

    class Meta:
        unique_together = ('product', 'location')

# Закупка материалов
class MaterialPurchase(models.Model):
    date = models.DateField()
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.FloatField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    supplier = models.CharField(max_length=100, blank=True)
# Производство
class Production(models.Model):
    date = models.DateField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    produced_qty = models.FloatField()

# Списание материалов
class ProductionMaterial(models.Model):
    production = models.ForeignKey(Production, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity_used = models.FloatField()
# Отгрузки на WB
class WBShipment(models.Model):
    date = models.DateField()
    from_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='shipments_from')
    to_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='shipments_to')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.FloatField()
    wb_shipment_number = models.CharField(max_length=50)  # Номер поставки WB
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"{self.wb_shipment_number} - {self.quantity} {self.product.name}"

# Логистика ТК
class ShipmentLogistics(models.Model):
    shipment = models.OneToOneField(WBShipment, on_delete=models.CASCADE)
    carrier = models.CharField(max_length=100)  # ТК название
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    tracking_number = models.CharField(max_length=100, blank=True)


from django.contrib.auth.models import User


class WBToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    api_key = models.TextField(verbose_name="WB API ключ")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"WB Token {self.user.username}"


from django.db.models import Sum
from .models import MaterialStock, ProductStock, Location


def wb_stocks(request):
    """Остатки материалов и готовой продукции"""
    location_filter = request.GET.get('location')

    material_stocks = MaterialStock.objects.select_related('material', 'location').all()
    product_stocks = ProductStock.objects.select_related('product', 'location').all()

    if location_filter:
        material_stocks = material_stocks.filter(location_id=location_filter)
        product_stocks = product_stocks.filter(location_id=location_filter)

    total_materials = material_stocks.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_products = product_stocks.aggregate(Sum('quantity'))['quantity__sum'] or 0

    context = {
        'material_stocks': material_stocks,
        'product_stocks': product_stocks,
        'total_materials': total_materials,
        'total_products': total_products,
        'critical_materials': material_stocks.filter(quantity=0).count(),
        'critical_products': product_stocks.filter(quantity__lt=5).count(),
        'locations': Location.objects.all(),
        'selected_location': location_filter,
    }
    return render(request, 'core/stocks.html', context)


from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username} - Profile"

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/img/default-avatar.png'
