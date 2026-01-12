from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    # ✅ Логин/Логаут Django
    path('accounts/login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='dashboard'), name='logout'),
    path('profile/', views.user_profile, name='profile'),  # ✅ ИСПРАВЛЕНО!

    # ✅ Основные формы
    path('', views.dashboard, name='dashboard'),
    path('production/', views.production_create, name='production_create'),
    path('purchase/', views.purchase_create, name='purchase_create'),
    path('shipment/', views.shipment_create, name='shipment_create'),

    # ✅ WB модули (убрал проблемный!)
    path('wb/profile/', views.wb_profile, name='wb_profile'),
    # path('wb/sync-products/', views.wb_sync_products, name='sync_wb_products'),  # ❌ УБРАЛ!
    path('wb/stocks/', views.wb_stocks, name='wb_stocks'),
]
