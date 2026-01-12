from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from .forms import ProductionForm, PurchaseForm, ShipmentForm, UserProfileForm
from .models import *
from .services.wb_api import WildberriesAPI  # ✅ Импорт API

# ✅ ГЛАВНЫЙ ДАШБОРД — ТЕПЕРЬ С @login_required!
@login_required
def dashboard(request):
    """🔒 Главный дашборд — только для авторизованных"""
    total_products = ProductStock.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_materials = MaterialStock.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
    critical_materials = MaterialStock.objects.filter(quantity=0).count()

    status_icon = "✓" if critical_materials == 0 else "⚠️"
    status_color = "success" if critical_materials == 0 else "warning"

    context = {
        'total_products': round(total_products, 1),
        'total_materials': round(total_materials, 1),
        'critical_materials': critical_materials,
        'status_icon': status_icon,
        'status_color': status_color,
        'now': timezone.now(),
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def production_create(request):
    """🔒 Производство"""
    if request.method == 'POST':
        form = ProductionForm(request.POST)
        if form.is_valid():
            production = form.save()

            # Автоматическое списание материалов
            for bom in production.product.productbom_set.all():
                stock, created = MaterialStock.objects.get_or_create(
                    material=bom.material,
                    location=production.location,
                    defaults={'quantity': 0}
                )
                stock.quantity -= bom.qty_per_unit * production.produced_qty
                if stock.quantity < 0:
                    stock.quantity = 0
                stock.save()

            # Поступление готовой продукции
            product_stock, created = ProductStock.objects.get_or_create(
                product=production.product,
                location=production.location,
                defaults={'quantity': 0}
            )
            product_stock.quantity += production.produced_qty
            product_stock.save()

            messages.success(request, f'✅ Произведено {production.produced_qty} {production.product.name}')
            return redirect('dashboard')
    else:
        form = ProductionForm()

    return render(request, 'core/production.html', {
        'form': form,
        'title': 'Производство'
    })


@login_required
def purchase_create(request):
    """🔧 ИСПРАВЛЕННЫЙ СЧЁТЧИК СУММЫ"""
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save(commit=False)

            # ✅ ТОЧНЫЙ РАСЧЁТ!
            quantity = float(form.cleaned_data['quantity'] or 0)
            unit_price = float(form.cleaned_data['unit_price'] or 0)
            purchase.total_amount = quantity * unit_price  # ✅ РАБОТАЕТ!

            purchase.save()

            # Остальной код без изменений...
            home_loc, created = Location.objects.get_or_create(
                name='Дом', defaults={'type': 'home'}
            )
            stock, _ = MaterialStock.objects.get_or_create(
                material=purchase.material, location=home_loc,
                defaults={'quantity': 0}
            )
            stock.quantity += purchase.quantity
            stock.save()

            messages.success(request,
                             f'✅ Закуплено {purchase.quantity} {purchase.material.unit} '
                             f'за {purchase.total_amount:,.0f} руб.')
            return redirect('dashboard')
    else:
        form = PurchaseForm()

    return render(request, 'core/purchase.html', {'form': form, 'title': 'Закупки'})


@login_required
def shipment_create(request):
    """🔒 Отгрузки"""
    if request.method == 'POST':
        form = ShipmentForm(request.POST)
        if form.is_valid():
            shipment = form.save()

            # Списание с "откуда"
            from_stock, _ = ProductStock.objects.get_or_create(
                product=shipment.product, location=shipment.from_location
            )
            if from_stock.quantity < shipment.quantity:
                messages.error(request, '❌ Недостаточно готовой продукции!')
                shipment.delete()
                form = ShipmentForm()
                return render(request, 'core/shipment.html', {'form': form, 'title': 'Отгрузки'})

            from_stock.quantity -= shipment.quantity
            from_stock.save()

            # Поступление "куда"
            to_stock, _ = ProductStock.objects.get_or_create(
                product=shipment.product, location=shipment.to_location
            )
            to_stock.quantity += shipment.quantity
            to_stock.save()

            messages.success(request,
                             f'✅ Отгружено {shipment.quantity} на склад {shipment.to_location}! №{shipment.wb_shipment_number}')
            return redirect('dashboard')
    else:
        form = ShipmentForm()

    return render(request, 'core/shipment.html', {'form': form, 'title': 'Отгрузки'})

@login_required
def wb_profile(request):
    """🔒 WB Токен"""
    token, created = WBToken.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        token.api_key = request.POST.get('api_key', '').strip()
        token.save()
        messages.success(request, "✅ Токен сохранен!")
        return redirect('wb_profile')

    test_result = None
    if token.api_key:
        try:
            wb_api = WildberriesAPI(token.api_key)
            test_result = wb_api.test_connection()
        except:
            test_result = {'status': 'error', 'message': 'Ошибка подключения'}

    return render(request, 'wb_settings.html', {
        'token': token,
        'test_result': test_result
    })

@login_required
def sync_wb_products(request):
    """🔒 Синхронизация WB"""
    token = WBToken.objects.get(user=request.user)
    try:
        wb_api = WildberriesAPI(token.api_key)
        test = wb_api.test_connection()
        products = wb_api.get_demo_products(limit=50)
    except:
        products = []
        test = {'status': 'error'}

    return render(request, 'wb_products.html', {
        'products': products,
        'count': len(products),
        'test_result': test
    })

@login_required
def wb_stocks(request):
    """🔒 Остатки WB"""
    location_filter = request.GET.get('location')

    material_stocks = MaterialStock.objects.select_related('material', 'location').all()
    product_stocks = ProductStock.objects.select_related('product', 'location').all()

    if location_filter:
        material_stocks = material_stocks.filter(location_id=location_filter)
        product_stocks = product_stocks.filter(location_id=location_filter)

    context = {
        'material_stocks': material_stocks,
        'product_stocks': product_stocks,
        'total_materials': material_stocks.aggregate(Sum('quantity'))['quantity__sum'] or 0,
        'total_products': product_stocks.aggregate(Sum('quantity'))['quantity__sum'] or 0,
        'critical_materials': material_stocks.filter(quantity=0).count(),
        'locations': Location.objects.all(),
        'selected_location': location_filter,
    }
    return render(request, 'core/stocks.html', context)

@login_required
def user_profile(request):
    """🔒 Профиль пользователя"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Профиль обновлён!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'core/profile.html', {
        'form': form,
        'profile': profile,
    })
