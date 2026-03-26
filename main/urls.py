from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('catalog/<int:pk>/', views.flower_detail, name='flower_detail'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:pk>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile, name='profile'),

    path('review/add/', views.add_review, name='add_review'),
    path('api/reviews/<int:flower_id>/', views.reviews_api, name='reviews_api'),
    path('api/ai-chat/', views.ai_chat, name='ai_chat'),
    path('api/change-language/', views.change_language, name='change_language'),

    path('order/success/<str:receipt_code>/', views.order_success, name='order_success'),
    path('check-receipt/', views.check_receipt, name='check_receipt'),

    path('admin/block-user/<int:user_id>/', views.admin_block_user, name='admin_block_user'),
    path('admin/delete-user/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),

    path('pay/<int:order_id>/', views.pay, name='pay'),
    path('payme/', views.payme, name='payme'),
]